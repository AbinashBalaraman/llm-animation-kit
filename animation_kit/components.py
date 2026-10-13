"""Original procedural puppet, camera and motion controllers; no learned weights."""
from __future__ import annotations

import math
from PIL import Image, ImageDraw, ImageFont

PALETTE = {"night": "#182c3c", "ink": "#10212f", "paper": "#f6ecd7", "mint": "#9bd4c8", "rose": "#ee9d96", "gold": "#f7c66c", "ground": "#355565"}


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


def evaluate(scene, frame):
    """Evaluate directly at any frame, preserving persistent root/gaze/expression."""
    actors = {}
    for actor in scene["actors"]:
        state = dict(actor, gaze=0.0, emotion="neutral", intensity=0.0, gesture="none", phase=0.0, stride=0.0)
        actors[actor["id"]] = state
    entities = {x["id"]: x for x in scene["props"]}
    ordered = sorted(scene["actions"], key=lambda a: (a["start"], a["id"]))
    # Root motion first so gaze targets use their evaluated positions.
    for action in ordered:
        if action["type"] != "move_to" or frame < action["start"]:
            continue
        state = actors[action["actor"]]
        u = (frame - action["start"]) / max(1, action["end"] - action["start"] - 1)
        state["x"] = lerp(state["x"], action["x"], smooth(u))
        if frame < action["end"]:
            state["stride"] = math.sin(u * math.pi * max(2, abs(action["x"] - state["x"]) / 40)) * math.sin(math.pi * min(1, u))
    entities.update(actors)
    for action in ordered:
        if action["type"] == "move_to" or frame < action["start"]:
            continue
        state = actors[action["actor"]]
        length = action["end"] - action["start"]
        u = min(1.0, (frame - action["start"]) / max(1, length - 1))
        if action["type"] == "look_at":
            dx = entities[action["target"]]["x"] - state["x"]
            state["gaze"] = lerp(state["gaze"], max(-1, min(1, dx / 180)), smooth(min(1, u * 4)))
        elif action["type"] == "expression":
            state["emotion"] = action["emotion"]
            state["intensity"] = lerp(state["intensity"], action["intensity"], smooth(min(1, u * 4)))
        elif action["type"] == "gesture" and frame < action["end"]:
            state["gesture"], state["phase"] = action["variant"], u
    shot = next(s for s in scene["shots"] if s["start"] <= frame < s["end"])
    camera = shot["camera"]
    return {"frame": frame, "actors": actors, "props": scene["props"], "camera": camera, "shot": shot["id"]}


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def draw_frame(scene, frame, width=960, height=540):
    scale = width / 960
    image = Image.new("RGB", (width * 2, height * 2), PALETTE["night"])
    draw = ImageDraw.Draw(image)
    sx = width * 2 / 960
    sy = height * 2 / 540
    state = evaluate(scene, frame)
    cam = state["camera"]
    def point(x, y):
        return ((x - cam["x"]) * cam["zoom"] * sx + width,
                (y - cam["y"]) * cam["zoom"] * sy + height)
    def ellipse(x, y, rx, ry, color, outline=None, line=2):
        left, top = point(x-rx, y-ry)
        right, bottom = point(x+rx, y+ry)
        draw.ellipse((left, top, right, bottom), fill=color, outline=outline, width=max(1, round(line*sx*cam["zoom"])))
    def line(points, color, thickness=4):
        draw.line([point(*p) for p in points], fill=color, width=max(1, round(thickness*sx*cam["zoom"])), joint="curve")
    def poly(points, color, outline=None):
        pts = [point(*p) for p in points]
        draw.polygon(pts, fill=color)
        if outline:
            draw.line(pts+[pts[0]], fill=outline, width=max(1, round(3*sx*cam["zoom"])), joint="curve")
    # Original midnight garden artwork, rebuilt procedurally every frame.
    ellipse(770, 106, 47, 47, "#e5dcbc")
    ellipse(790, 89, 44, 44, PALETTE["night"])
    for i in range(35):
        x = (i * 137 + 53) % 960
        y = (i * 67 + 39) % 295
        ellipse(x, y, 1.7, 1.7, "#829da7")
    poly([(-400,440),(90,330),(240,365),(470,309),(740,348),(1250,290),(1400,650),(-400,650)], "#274451")
    poly([(-400,456),(230,420),(430,442),(670,412),(1400,434),(1400,700),(-400,700)], PALETTE["ground"])
    line([(-400,455),(1400,455)], "#537784", 2)
    for x in (100, 150, 840, 895):
        line([(x,455),(x+3,426)], "#70a89d", 3)
        ellipse(x-6,435,9,4,"#70a89d")
        ellipse(x+10,442,10,4,"#8bc2ad")
    for prop in scene["props"]:
        x, y, size = prop["x"], prop["y"], prop["size"]
        if prop["kind"] == "star":
            pulse = 1 + .035 * math.sin(frame * .12)
            points=[]
            for j in range(10):
                r=size*pulse*(1 if j%2==0 else .46)
                a=-math.pi/2+j*math.pi/5
                points.append((x+math.cos(a)*r,y+math.sin(a)*r))
            ellipse(x,y,size*1.45,size*1.45,"#3d6062")
            poly(points, prop["color"], PALETTE["ink"])
            ellipse(x-5,y-2,2,3,PALETTE["ink"])
            ellipse(x+5,y-2,2,3,PALETTE["ink"])
            line([(x-3,y+6),(x,y+8),(x+3,y+6)],PALETTE["ink"],2)
        elif prop["kind"] == "orb":
            ellipse(x,y,size,size,prop["color"],PALETTE["ink"],3)
            ellipse(x-size*.3,y-size*.3,size*.22,size*.15,PALETTE["paper"])
        else:
            poly([(x-size,y-size),(x+size,y-size),(x+size,y+size),(x-size,y+size)],prop["color"],PALETTE["ink"])
    for actor in state["actors"].values():
        x, base, s = actor["x"], actor["y"], actor["scale"]
        emotion, strength = actor["emotion"], actor["intensity"]
        surprise = strength if emotion == "surprised" else 0
        happy = strength if emotion == "happy" else 0
        bob = math.sin(frame*.055)*1.2
        if actor["gesture"] == "celebrate":
            bob -= abs(math.sin(actor["phase"]*math.pi*3))*8
        def p(a,b): return (x+a*s,base+(b+bob)*s)
        def el(a,b,rx,ry,color,outline=None): ellipse(*p(a,b),rx*s,ry*s,color,outline,3)
        def ln(coords,color,thickness): line([p(a,b) for a,b in coords],color,thickness*s)
        ellipse(x,base+5,53*s,9*s,"#233e4a")
        # Legs: motion controller articulates them while feet remain on the stage.
        stride=actor["stride"]*10
        ln([(-21,-47),(-23-stride,-15),(-27-stride,0)],PALETTE["ink"],15)
        ln([(21,-47),(23+stride,-15),(27+stride,0)],PALETTE["ink"],15)
        el(-29-stride,0,18,7,PALETTE["paper"],PALETTE["ink"])
        el(29+stride,0,18,7,PALETTE["paper"],PALETTE["ink"])
        el(0,-81,43,52,actor["color"],PALETTE["ink"])
        el(0,-73,25,27,"#f2dab1")
        el(0,-75,6,6,actor["accent"],PALETTE["ink"])
        # Arms are actual 2D pose components, not frame synthesis.
        phase=actor["phase"]
        left=[(-35,-111),(-56,-84),(-49,-62)]
        right=[(35,-111),(56,-84),(49,-62)]
        weight=math.sin(math.pi*phase)**.5 if actor["gesture"] != "none" else 0
        if actor["gesture"] == "wave":
            goal=[(35,-111),(60,-138),(62+math.sin(phase*math.pi*6)*12,-180)]
            right=[(lerp(a,c,weight),lerp(b,d,weight)) for (a,b),(c,d) in zip(right,goal)]
        elif actor["gesture"] == "reach":
            goal=[(35,-111),(71,-122),(101,-130)]
            right=[(lerp(a,c,weight),lerp(b,d,weight)) for (a,b),(c,d) in zip(right,goal)]
        elif actor["gesture"] == "celebrate":
            left=[(-35,-111),(-65,-140),(-70,-183)]
            right=[(35,-111),(65,-140),(70,-183)]
            left=[(lerp(a,c,weight),lerp(b,d,weight)) for (a,b),(c,d) in zip([(-35,-111),(-56,-84),(-49,-62)],left)]
            right=[(lerp(a,c,weight),lerp(b,d,weight)) for (a,b),(c,d) in zip([(35,-111),(56,-84),(49,-62)],right)]
        for arm in (left,right):
            ln(arm,PALETTE["ink"],14)
            ln(arm,actor["color"],9)
            el(*arm[-1],10,10,actor["accent"],PALETTE["ink"])
        # Large face and ear fins retain identity across every shot.
        el(-51,-172,14,24,actor["accent"],PALETTE["ink"])
        el(51,-172,14,24,actor["accent"],PALETTE["ink"])
        el(0,-169-surprise*4,57,50+surprise*2,actor["color"],PALETTE["ink"])
        el(0,-167-surprise*4,47,38,PALETTE["paper"],PALETTE["ink"])
        gaze=actor["gaze"]*5
        blink=(frame%103 in (76,77))
        for eye in (-18,18):
            if blink:
                ln([(eye-6,-171),(eye+6,-171)],PALETTE["ink"],4)
            else:
                el(eye+gaze,-171,5+surprise*2,7+surprise*5,PALETTE["ink"])
                el(eye+gaze+1,-174,1.5,2,"#ffffff")
            brow= -187-surprise*7
            tilt=5*strength if emotion in ("curious","sad") else 0
            ln([(eye-7,brow+tilt),(eye+7,brow-tilt)],PALETTE["ink"],3)
        el(-30,-154,7,4,"#e6b0a1")
        el(30,-154,7,4,"#e6b0a1")
        if emotion == "surprised":
            el(0,-150,5+strength*2,5+strength*6,PALETTE["ink"])
        elif emotion == "happy":
            ln([(-12,-154),(-7,-148-happy*2),(0,-146-happy*2),(7,-148-happy*2),(12,-154)],PALETTE["ink"],3)
        elif emotion == "sad":
            ln([(-10,-148),(0,-153),(10,-148)],PALETTE["ink"],3)
        else:
            ln([(-8,-151),(8,-151)],PALETTE["ink"],3)
        el(0,-222-surprise*4,9,9,actor["accent"],PALETTE["ink"])
    # Typography is screen-space, independent of the scene camera.
    draw.text((42*sx,29*sy),scene["title"].upper(),font=font(round(22*sx)),fill=PALETTE["paper"])
    draw.text((44*sx,61*sy),scene["subtitle"],font=font(round(12*sx)),fill="#abc1c3")
    draw.text((44*sx,507*sy),"CODE / CHARACTER / MOTION",font=font(round(10*sx)),fill="#abc1c3")
    return image.resize((width,height),Image.Resampling.LANCZOS), state
