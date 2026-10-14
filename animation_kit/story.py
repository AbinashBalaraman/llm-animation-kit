"""Deterministic hierarchical vector artwork, authored poses, and local shot clocks."""
from __future__ import annotations
import math
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .contracts import DATA, KitError

IDENTITY = (1, 0, 0, 1, 0, 0)
DEFAULTS = {"x": 0, "y": 0, "scale_x": 1, "scale_y": 1, "rotation": 0, "opacity": 1}


def value_at(value, frame):
    if not isinstance(value, dict):
        return value
    keys = value["keys"]
    if frame <= keys[0]["frame"]:
        return keys[0]["value"]
    for a, b in zip(keys, keys[1:]):
        if frame < b["frame"]:
            t = (frame - a["frame"]) / (b["frame"] - a["frame"])
            ease = b.get("ease", "smooth")
            if ease == "hold": t = 0
            elif ease == "smooth": t = t*t*(3-2*t)
            elif ease == "in_cubic": t = t*t*t
            elif ease == "out_cubic": t = 1-(1-t)**3
            elif ease == "out_back": t = 1+2.70158*(t-1)**3+1.70158*(t-1)**2
            return a["value"] + (b["value"] - a["value"]) * t
    return keys[-1]["value"]


def multiply(a, b):
    aa, ab, ac, ad, ax, ay = a
    ba, bb, bc, bd, bx, by = b
    return (aa*ba+ac*bb, ab*ba+ad*bb, aa*bc+ac*bd, ab*bc+ad*bd,
            aa*bx+ac*by+ax, ab*bx+ad*by+ay)


def transform(props):
    r = math.radians(props["rotation"])
    c, s = math.cos(r), math.sin(r)
    return (c*props["scale_x"], s*props["scale_x"], -s*props["scale_y"], c*props["scale_y"], props["x"], props["y"])


def point(matrix, xy):
    a,b,c,d,x,y = matrix
    return a*xy[0]+c*xy[1]+x, b*xy[0]+d*xy[1]+y


def descendants(nodes):
    for node in nodes:
        yield node
        yield from descendants(node.get("children", []))


def validate_semantics(scene):
    issues = []
    if "direction" in scene:
        from .direction import scene_plan_issues
        issues.extend(scene_plan_issues(scene))
    def issue(code, pointer, message):
        issues.append({"code": code, "pointer": pointer, "message": message,
                       "repair_hint": "Repair the named artwork, timeline or brief evidence; do not substitute a stock scene."})
    if scene["frames"] / scene["fps"] > 120:
        issue("duration", "/frames", "Stories are bounded to 120 seconds.")
    assets = {a["id"]: a for a in scene["assets"]}
    if len(assets) != len(scene["assets"]): issue("duplicate_asset", "/assets", "Asset IDs must be unique.")
    requirements = {r["id"] for r in scene["brief"]["requirements"]}
    if len(requirements) != len(scene["brief"]["requirements"]): issue("duplicate_requirement", "/brief", "Requirement IDs must be unique.")
    shots = {s["id"]: s for s in scene["shots"]}
    ordered = sorted(scene["shots"], key=lambda s: s["start"])
    if len(shots) != len(ordered): issue("duplicate_shot", "/shots", "Shot IDs must be unique.")
    if ordered[0]["start"] != 0 or ordered[-1]["end"] != scene["frames"] or any(a["end"] != b["start"] for a,b in zip(ordered, ordered[1:])):
        issue("shot_coverage", "/shots", "Shots must partition [0, frames) exactly.")
    def check_tracks(node, duration, ptr):
        if isinstance(node, dict):
            if "keys" in node:
                frames = [k["frame"] for k in node["keys"]]
                if frames != sorted(set(frames)) or frames[-1] > duration:
                    issue("keyframe_timing", ptr, "Keyframes must increase strictly and stay within the local shot duration.")
            for name, item in node.items():
                check_tracks(item, duration, ptr+"/"+name)
                if name in ("opacity", "scale_x", "scale_y", "zoom") and (isinstance(item, (int,float)) or isinstance(item, dict) and "keys" in item):
                    vals = [k["value"] for k in item["keys"]] if isinstance(item,dict) else [item]
                    if name == "opacity" and any(v < 0 or v > 1 for v in vals): issue("opacity", ptr, "Opacity values must be within [0,1].")
                    if name == "zoom" and any(v < .1 or v > 8 for v in vals): issue("camera_zoom", ptr, "Camera zoom must be within [.1,8].")
                    if name.startswith("scale") and any(abs(v) > 20 for v in vals): issue("scale", ptr, "Absolute scale must not exceed 20.")
        elif isinstance(node, list):
            for i, item in enumerate(node): check_tracks(item, duration, ptr+f"/{i}")
    def nodes_check(nodes, ptr, in_asset=False, depth=0):
        if depth > 24:
            issue("depth", ptr, "Node hierarchy exceeds 24 levels."); return
        for node in nodes:
            if node["kind"] == "instance":
                asset = assets.get(node["asset"])
                if in_asset: issue("nested_asset", ptr, "Asset definitions use geometry/groups; instances belong in shots.")
                if asset is None: issue("missing_asset", ptr, f"Unknown asset: {node['asset']}")
                else:
                    ids = {n["id"] for n in descendants(asset["nodes"])}
                    if set(node.get("overrides", {})) - ids:
                        issue("missing_override_target", ptr, "A pose override names a node absent from its asset.")
            if node["kind"] == "path":
                active=False
                for cmd in node["commands"]:
                    if cmd[0]=="M": active=True
                    elif not active: issue("path_start", ptr, "Begin each path/subpath with M, including after Z."); break
                    elif cmd[0]=="Z": active=False
            nodes_check(node.get("children", []), ptr+"/"+node["id"], in_asset, depth+1)
    for i, asset in enumerate(scene["assets"]):
        nodes_check(asset["nodes"], f"/assets/{i}", True)
        ids = [n["id"] for n in descendants(asset["nodes"])]
        if len(set(ids)) != len(ids): issue("duplicate_node", f"/assets/{i}", "Node IDs must be unique within an asset.")
        # Asset drawings are reusable static geometry. Shot instances supply poses.
        def has_track(value):
            return isinstance(value,dict) and ("keys" in value or any(has_track(v) for v in value.values())) or isinstance(value,list) and any(has_track(v) for v in value)
        if has_track(asset): issue("asset_clock", f"/assets/{i}", "Put animation in shot instance overrides; assets are static reusable drawings.")
        check_tracks(asset, scene["frames"], f"/assets/{i}")
    for i, shot in enumerate(ordered):
        duration = shot["end"]-shot["start"]
        if duration <= 0: issue("shot_timing", f"/shots/{i}", "Shot duration must be positive.")
        nodes_check(shot["nodes"], f"/shots/{i}")
        ids = [n["id"] for n in descendants(shot["nodes"])]
        if len(set(ids)) != len(ids): issue("duplicate_node", f"/shots/{i}", "Node IDs must be unique within a shot.")
        count = len(ids) + sum(len(list(descendants(assets[n["asset"]]["nodes"]))) for n in descendants(shot["nodes"]) if n["kind"] == "instance" and n["asset"] in assets)
        if count > 2500: issue("node_budget", f"/shots/{i}", "Expanded shot exceeds 2500 nodes.")
        check_tracks(shot, duration, f"/shots/{i}")
    covered = set()
    beat_ids = set()
    for i, beat in enumerate(scene["beats"]):
        ptr = f"/beats/{i}"
        if beat["id"] in beat_ids: issue("duplicate_beat", ptr, "Beat IDs must be unique.")
        beat_ids.add(beat["id"])
        covered.update(beat["requirements"])
        if set(beat["requirements"])-requirements: issue("missing_requirement", ptr, "Beat refers to an unknown requirement.")
        shot = shots.get(beat["shot"])
        if not shot or not shot["start"] <= beat["frame"] < shot["end"]:
            issue("beat_timing", ptr, "Evidence frame must lie in its named shot.")
        elif set(beat["nodes"])-{n["id"] for n in descendants(shot["nodes"])}:
            issue("missing_evidence_node", ptr, "Beat evidence refers to an absent shot node.")
    if requirements-covered: issue("uncovered_requirement", "/beats", "No visual beat covers: "+", ".join(sorted(requirements-covered)))
    for i, cue in enumerate(scene["audio"]):
        if cue["frame"] >= scene["frames"] or cue["frame"]/scene["fps"] + cue["duration"] > scene["frames"]/scene["fps"]+.001:
            issue("audio_timing", f"/audio/{i}", "Audio cue must lie within the story.")
    return issues


@lru_cache(maxsize=256)
def font(name, size):
    filename = {"sans": "NunitoSans.ttf", "display": "LilitaOne.ttf"}[name]
    return ImageFont.truetype(str(DATA.joinpath("fonts", filename)), max(1, round(size)))


def vertices(node):
    kind = node["kind"]
    if kind == "ellipse":
        return [([(node["rx"]*math.cos(i*math.tau/72), node["ry"]*math.sin(i*math.tau/72)) for i in range(72)], True)]
    if kind == "polygon": return [(node["points"], True)]
    if kind == "rect":
        w,h = node["width"],node["height"]
        r = min(node.get("radius",0), w/2, h/2)
        pts = []
        for cx,cy,start in [(w-r,r,-90),(w-r,h-r,0),(r,h-r,90),(r,r,180)]:
            pts += [(cx+r*math.cos(math.radians(start+i*90/8)), cy+r*math.sin(math.radians(start+i*90/8))) for i in range(9)]
        return [(pts, True)]
    if kind == "path":
        contours, pts, current = [], [], (0,0)
        for c in node["commands"]:
            if c[0] == "M":
                if pts: contours.append((pts, False))
                pts = [tuple(c[1:])]; current = pts[0]
            elif c[0] == "L": current = tuple(c[1:]); pts.append(current)
            elif c[0] in ("Q", "C"):
                start = current
                controls = [start]+[(c[i], c[i+1]) for i in range(1,len(c),2)]
                for step in range(1,25):
                    t=step/24; level=controls
                    while len(level)>1:
                        level=[((1-t)*a[0]+t*b[0], (1-t)*a[1]+t*b[1]) for a,b in zip(level,level[1:])]
                    pts.append(level[0])
                current=pts[-1]
            elif c[0] == "Z":
                contours.append((pts, True)); current=pts[0]; pts=[]
        if pts: contours.append((pts,False))
        return contours
    return []


def evaluate(scene, frame):
    if not 0 <= frame < scene["frames"]: raise KitError("frame_range", "Frame outside story.")
    shot = next(s for s in scene["shots"] if s["start"] <= frame < s["end"])
    local = frame-shot["start"]
    camera = {k:value_at(v,local) for k,v in shot.get("camera", {"x":480,"y":270,"zoom":1}).items()}
    cm = (camera["zoom"],0,0,camera["zoom"],480-camera["x"]*camera["zoom"],270-camera["y"]*camera["zoom"])
    assets={a["id"]: a for a in scene["assets"]}
    paints, states = [], {}
    def walk(nodes, parent, opacity, prefix="", overrides=None):
        for raw in nodes:
            node = dict(raw, **(overrides or {}).get(raw["id"], {}))
            props={k:value_at(node.get(k,v),local) for k,v in DEFAULTS.items()}
            matrix=multiply(parent,transform(props)); alpha=max(0,min(1,opacity*props["opacity"]))
            ident=prefix+node["id"]
            states[ident]={"kind":node["kind"],"opacity":alpha,"matrix":[round(x,5) for x in matrix],"bounds":None}
            start=len(paints)
            if node["kind"] == "instance":
                walk(assets[node["asset"]]["nodes"],matrix,alpha,ident+"/",node.get("overrides",{}))
            elif node["kind"] == "group": walk(node["children"],matrix,alpha,prefix,overrides)
            else:
                if node["kind"] == "text":
                    f=font(node.get("font","sans"),node["size"])
                    box=f.getbbox(node["text"])
                    w,h=box[2]-box[0],box[3]-box[1]
                    shift={"left":0,"center":-w/2,"right":-w}.get(node.get("align","center"),-w/2)
                    geometry=[(shift,-h/2),(shift+w,-h/2),(shift+w,h/2),(shift,h/2)]
                else: geometry=[p for points,_ in vertices(node) for p in points]
                pts=[point(matrix,p) for p in geometry]
                bounds=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)] if pts else None
                if bounds and node.get("stroke") and node.get("stroke_width",2)>0:
                    radius=node.get("stroke_width",2)*math.sqrt(abs(matrix[0]*matrix[3]-matrix[1]*matrix[2]))/2
                    bounds=[bounds[0]-radius,bounds[1]-radius,bounds[2]+radius,bounds[3]+radius]
                paints.append({"id":ident,"node":node,"matrix":matrix,"opacity":alpha,"bounds":bounds})
            boxes=[p["bounds"] for p in paints[start:] if p["bounds"] and p["opacity"] > .01 and (p["node"].get("fill", "#172f43") is not None or (p["node"].get("stroke") and p["node"].get("stroke_width",2)>0))]
            states[ident]["paint_ids"]=[p["id"] for p in paints[start:]]
            if boxes: states[ident]["bounds"]=[round(min(b[0] for b in boxes),2),round(min(b[1] for b in boxes),2),round(max(b[2] for b in boxes),2),round(max(b[3] for b in boxes),2)]
    walk(shot["nodes"],cm,1)
    return {"frame":frame,"local_frame":local,"shot":shot["id"],"camera":camera,"nodes":states,"paints":paints,"background":shot["background"]}


def visible_evidence(state, node_id, allow_text=False):
    node=state["nodes"].get(node_id)
    if not node or node["opacity"] < .1 or not node["bounds"]: return False
    x0,y0,x1,y1=node["bounds"]
    if min(960,x1)-max(0,x0)<3 or min(540,y1)-max(0,y0)<3: return False
    # A renamed title is not pictorial evidence of an actor or story event.
    if not allow_text:
        candidates=[p for p in state["paints"] if p["id"] in node["paint_ids"]]
        if not any(p["node"]["kind"] != "text" and p["opacity"]>.1 and p["bounds"] and
                   min(960,p["bounds"][2])-max(0,p["bounds"][0])>3 and min(540,p["bounds"][3])-max(0,p["bounds"][1])>3 for p in candidates): return False
    return True


def trace(state):
    return {k:v for k,v in state.items() if k not in ("paints","background")}


def draw_frame(scene, frame, width=640, height=360):
    state=evaluate(scene,frame)
    # All shape geometry is drawn at twice the output resolution, then filtered.
    scale=width/960*2; W,H=width*2,height*2
    image=Image.new("RGB",(W,H),state["background"])
    draw=ImageDraw.Draw(image,"RGBA")
    def color(value, opacity):
        if value is None: return None
        return (*tuple(int(value[i:i+2],16) for i in (1,3,5)),round(255*opacity))
    for paint in state["paints"]:
        node,alpha=paint["node"],paint["opacity"]
        if alpha <= .001: continue
        matrix=tuple(x*scale for x in paint["matrix"])
        if node["kind"] == "text":
            # Rasterize typography locally and affine-transform a tight patch.
            density=3
            f=font(node.get("font","sans"),node["size"]*density)
            box=f.getbbox(node["text"]); tw,th=box[2]-box[0],box[3]-box[1]
            if tw<=0 or th<=0: continue
            patch=Image.new("RGBA",(tw+4,th+4))
            ImageDraw.Draw(patch).text((2-box[0],2-box[1]),node["text"],font=f,fill=color(node.get("fill","#172f43"),alpha))
            lw,lh=tw/density,th/density
            shift={"left":0,"center":-lw/2,"right":-lw}[node.get("align","center")]
            tm=multiply(matrix,(1/density,0,0,1/density,shift-2/density,-lh/2-2/density))
            a,b,c,d,x,y=tm; det=a*d-b*c
            if abs(det)<1e-8: continue
            corners=[point(tm,p) for p in [(0,0),patch.size,(patch.width,0),(0,patch.height)]]
            left=max(0,math.floor(min(p[0] for p in corners))); top=max(0,math.floor(min(p[1] for p in corners)))
            right=min(W,math.ceil(max(p[0] for p in corners))); bottom=min(H,math.ceil(max(p[1] for p in corners)))
            if right<=left or bottom<=top: continue
            inverse=(d/det,-c/det,(d*(left-x)-c*(top-y))/det,-b/det,a/det,(-b*(left-x)+a*(top-y))/det)
            warped=patch.transform((right-left,bottom-top),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC)
            image.paste(warped,(left,top),warped)
            continue
        fill=color(node.get("fill","#172f43"),alpha); stroke=color(node.get("stroke"),alpha)
        stroke_width=max(1,round(node.get("stroke_width",2)*math.sqrt(abs(matrix[0]*matrix[3]-matrix[1]*matrix[2]))))
        for points,closed in vertices(node):
            points=[point(matrix,p) for p in points]
            if len(points)<2: continue
            if fill and len(points)>2: draw.polygon(points,fill=fill)
            if stroke and node.get("stroke_width",2)>0:
                draw.line(points+[points[0]] if closed else points, fill=stroke,width=stroke_width,joint="curve")
                r=stroke_width/2
                for x,y in (points[:1]+points[-1:] if not closed else []): draw.ellipse((x-r,y-r,x+r,y+r),fill=stroke)
    return image.resize((width,height),Image.Resampling.LANCZOS),trace(state)
