"""Bounded native frame rendering, artifact verification and FFmpeg assembly."""
from __future__ import annotations

import hashlib
import math
import os
import struct
import subprocess
import time
import wave
from pathlib import Path

from PIL import Image, ImageDraw, __version__ as pillow_version
import imageio_ffmpeg

from .components import draw_frame, evaluate, font
from .contracts import KitError, read_json
from .store import atomic_json, digest

PROFILES={"preview":(640,360),"final":(1280,720)}


def file_hash(path):
    hasher=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ffmpeg_path():
    # The wheel-provided executable avoids installer stubs accidentally placed on PATH.
    candidate=os.environ.get("ANIMATION_KIT_FFMPEG") or imageio_ffmpeg.get_ffmpeg_exe()
    try:
        result=subprocess.run([candidate,"-version"],capture_output=True,text=True,timeout=10)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise KitError("ffmpeg_unavailable",str(exc),hint="Set ANIMATION_KIT_FFMPEG to a working ffmpeg executable.") from exc
    if result.returncode:
        raise KitError("ffmpeg_unavailable",result.stderr[-1000:])
    return candidate,result.stdout.splitlines()[0]


def soundtrack(path,scene):
    if scene.get("schema_version") == "kit.story/2.0":
        from array import array
        rate=24000
        count=math.ceil(scene["frames"]*rate/scene["fps"])
        samples=array("f",[0])*count
        for cue in scene["audio"]:
            start=round(cue["frame"]*rate/scene["fps"])
            length=round(cue["duration"]*rate)
            for j in range(min(length,count-start)):
                t=j/rate
                envelope=min(1,t/.008)*max(0,1-j/length)**2
                frequency=cue["frequency"]
                if cue["kind"]=="pop": frequency*=1+2*math.exp(-30*t)
                tone=math.sin(math.tau*frequency*t)
                if cue["kind"]=="bell": tone=(tone+.3*math.sin(math.tau*frequency*2*t))/1.3
                if cue["kind"]=="purr": tone*=.4+.6*abs(math.sin(math.tau*24*t))
                samples[start+j]+=cue["gain"]*envelope*tone
        with wave.open(str(path),"wb") as output:
            output.setparams((1,2,rate,0,"NONE","not compressed"))
            output.writeframes(b"".join(struct.pack("<h",round(max(-1,min(1,v))*32767)) for v in samples))
        return
    rate=48000
    count=scene["frames"]*rate//scene["fps"]
    accents=[a["start"]/scene["fps"] for a in scene["actions"] if a["type"]=="expression"]
    with wave.open(str(path),"wb") as out:
        out.setparams((1,2,rate,0,"NONE","not compressed"))
        for block in range(0,count,4096):
            samples=bytearray()
            for i in range(block,min(count,block+4096)):
                t=i/rate
                fade=min(1,t/0.6,(count/rate-t)/0.6)
                value=.035*math.sin(math.tau*196*t)+.025*math.sin(math.tau*246.94*t)+.02*math.sin(math.tau*293.66*t)
                for onset in accents:
                    dt=t-onset
                    if 0<=dt<1.2:
                        value+=.1*math.exp(-dt*4)*math.sin(math.tau*783.99*dt)*min(1,dt/.02)
                samples.extend(struct.pack("<h",int(max(-1,min(1,value*fade))*32767)))
            out.writeframes(samples)


def artifact_valid(path,expected):
    return path.is_file() and file_hash(path)==expected


def engine_fingerprint(ffmpeg_version):
    from .contracts import DATA
    return digest({"components":file_hash(Path(__file__).with_name("components.py")),
                   "story":file_hash(Path(__file__).with_name("story.py")),
                   "fonts":{p.name:file_hash(Path(str(p))) for p in DATA.joinpath("fonts").iterdir() if p.name.endswith(".ttf")},
                   "renderer":file_hash(Path(__file__)),"pillow":pillow_version,"ffmpeg":ffmpeg_version})


def render(store,project_id,profile="preview",expected_scene_hash=None):
    started=time.monotonic()
    width,height=PROFILES[profile]
    executable,ffmpeg_version=ffmpeg_path()
    engine_hash=engine_fingerprint(ffmpeg_version)
    with store.lock(project_id) as project:
        snapshot=store.load(project_id)
        if expected_scene_hash is not None and snapshot["scene_hash"]!=expected_scene_hash:
            raise KitError("stale_render","Project changed after review; inspect and review the new revision.")
        scene=snapshot["scene"]
        is_story=scene.get("schema_version")=="kit.story/2.0"
        render_frame=draw_frame
        evaluate_frame=evaluate
        if is_story:
            from .story import draw_frame as render_frame, evaluate as evaluate_story, trace as story_trace
            evaluate_frame=lambda s,f: story_trace(evaluate_story(s,f))
        has_sound=bool(scene["audio"]) if is_story else scene["sound"]=="chime"
        key=digest({"scene":snapshot["scene_hash"],"profile":profile,"engine":engine_hash})[:24]
        folder=(project/"renders"/key).resolve()
        if not folder.is_relative_to(store.root):
            raise KitError("path_escape","Render directory escapes workspace.")
        folder.mkdir(parents=True,exist_ok=True)
        manifest_path=folder/"manifest.json"
        manifest=read_json(manifest_path) if manifest_path.exists() else {}
        frame_cache=manifest.get("frames",{})
        if manifest.get("status")=="succeeded" and len(frame_cache)==scene["frames"] and all(artifact_valid(folder/"frames"/name,sha) for name,sha in frame_cache.items()) and all(artifact_valid(folder/name,sha) for name,sha in manifest.get("artifacts",{}).items()) and manifest.get("artifacts"):
            return dict(manifest,revision=snapshot["revision"],cached=True,manifest_path=str(manifest_path),video_path=str(folder/"video.mp4"),contact_sheet_path=str(folder/"contact-sheet.png"))
        frames_dir=folder/"frames"
        if not frames_dir.resolve().is_relative_to(store.root):
            raise KitError("path_escape","Frame directory escapes workspace.")
        frames_dir.mkdir(exist_ok=True)
        old_frames=manifest.get("frames",{})
        manifest={"job_id":key,"revision":snapshot["revision"],"scene_hash":snapshot["scene_hash"],"engine_hash":engine_hash,
                  "backend":"authored2d_v2" if is_story else "puppet2d_v1","profile":profile,"width":width,"height":height,"fps":scene["fps"],"frame_count":scene["frames"],
                  "ffmpeg":ffmpeg_version,"status":"running","frames":{},"artifacts":{},"cached":False}
        atomic_json(manifest_path,manifest)
        trace=[]
        warnings=[]
        resumed=0
        try:
            for frame in range(scene["frames"]):
                name=f"{frame:06d}.png"
                destination=frames_dir/name
                if artifact_valid(destination,old_frames.get(name,"")):
                    state=evaluate_frame(scene,frame)
                    resumed+=1
                else:
                    image,state=render_frame(scene,frame,width,height)
                    temporary=frames_dir/f".{name}.tmp"
                    image.save(temporary,format="PNG")
                    os.replace(temporary,destination)
                manifest["frames"][name]=file_hash(destination)
                trace.append(state)
                camera=state["camera"]
                for actor in state.get("actors",{}).values():
                    left=(actor["x"]-75*actor["scale"]-camera["x"])*camera["zoom"]+480
                    right=(actor["x"]+110*actor["scale"]-camera["x"])*camera["zoom"]+480
                    top=(actor["y"]-235*actor["scale"]-camera["y"])*camera["zoom"]+270
                    bottom=(actor["y"]+10*actor["scale"]-camera["y"])*camera["zoom"]+270
                    if (left<0 or right>960 or top<85 or bottom>500) and frame==next(s["start"] for s in scene["shots"] if s["id"]==state["shot"]):
                        warnings.append({"code":"framing","frame":frame,"actor":actor["id"],"message":"Actor bounds approach crop/title area.","repair_hint":"Read camera recipe; widen framing, reduce zoom or shift camera centre."})
                if frame%24==23:
                    atomic_json(manifest_path,manifest)
            atomic_json(folder/"trace.json",{"frames":trace,"diagnostics":warnings,"limits":["No 3D collision/contact solver","Technical diagnostics do not certify visual appeal"]})
            markers=([b["frame"] for b in scene["beats"]] + [s["start"] for s in scene["shots"]]) if is_story else [a["start"] for a in scene["actions"]]
            sampled=sorted(set([0,scene["frames"]-1]+[min(scene["frames"]-1,int(scene["frames"]*i/7)) for i in range(1,7)]+markers))
            # Contact sheet includes temporal evidence and action onsets.
            tw,th=320,180
            columns=4
            rows=math.ceil(len(sampled)/columns)
            sheet=Image.new("RGB",(columns*tw,rows*(th+24)),"#142733")
            draw=ImageDraw.Draw(sheet)
            for index,frame in enumerate(sampled):
                with Image.open(frames_dir/f"{frame:06d}.png") as im:
                    thumb=im.resize((tw,th))
                    x,y=(index%columns)*tw,(index//columns)*(th+24)
                    sheet.paste(thumb,(x,y))
                    draw.text((x+8,y+th+3),f"frame {frame} / {frame/scene['fps']:.2f}s",fill="#f6ecd7",font=font(12))
            sheet.save(folder/"contact-sheet.png")
            args=[executable,"-hide_banner","-loglevel","error","-y","-framerate",str(scene["fps"]),"-i",str(frames_dir/"%06d.png")]
            if has_sound:
                soundtrack(folder/"sound.wav",scene)
                args += ["-i",str(folder/"sound.wav"),"-c:a","aac","-b:a","128k"]
            args += ["-frames:v",str(scene["frames"]),"-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",str(folder/"video.tmp.mp4")]
            encoded=subprocess.run(args,capture_output=True,text=True,timeout=180)
            if encoded.returncode:
                raise KitError("encode_failed",encoded.stderr[-2000:])
            os.replace(folder/"video.tmp.mp4",folder/"video.mp4")
            # Decode verifies the delivered stream's actual dimensions and frame count.
            reader=imageio_ffmpeg.read_frames(str(folder/"video.mp4"))
            meta=next(reader)
            decoded=sum(1 for _ in reader)
            if decoded!=scene["frames"] or tuple(meta["size"])!=(width,height):
                raise KitError("encode_mismatch","Export did not preserve dimensions/frame count.")
            if abs(meta["fps"]-scene["fps"])>.01:
                raise KitError("fps_mismatch","Encoded frame rate differs from project.")
            artifacts=["video.mp4","contact-sheet.png","trace.json"]
            if has_sound:
                artifacts.append("sound.wav")
            # Editable source is included with every export.
            atomic_json(folder/"scene.json",scene)
            artifacts.append("scene.json")
            manifest.update(status="succeeded",seconds=round(time.monotonic()-started,3),resumed_frames=resumed,decoded_frame_count=decoded,
                            diagnostics=warnings,artifacts={name:file_hash(folder/name) for name in artifacts})
            atomic_json(manifest_path,manifest)
            return dict(manifest,manifest_path=str(manifest_path),video_path=str(folder/"video.mp4"),contact_sheet_path=str(folder/"contact-sheet.png"))
        except Exception as exc:
            manifest.update(status="failed",error=str(exc),seconds=round(time.monotonic()-started,3))
            atomic_json(manifest_path,manifest)
            raise
