"""Small authoring SDK: build your own artwork and keyframes, then save plain JSON.

This module has no cat, astronaut, stage, or story templates. Host-authored Python
runs in the host like other project code; the render server consumes data only.
"""
from __future__ import annotations
import copy
from pathlib import Path
from .contracts import require_valid
from .store import atomic_json


def track(*keys, ease="smooth"):
    """track((0, 10), (12, 30), (24, 10, 'out_back')); easing belongs to the destination."""
    return {"keys": [{"frame": k[0], "value": k[1], "ease": k[2] if len(k) == 3 else ease} for k in keys]}


def group(ident, *children, **props):
    return {"id": ident, "kind": "group", "children": list(children), **props}


def ellipse(ident, rx, ry, fill, **props):
    return {"id": ident, "kind": "ellipse", "rx": rx, "ry": ry, "fill": fill, **props}


def rect(ident, width, height, fill, **props):
    """Rectangles start at local (0,0); ellipses are centred on local (0,0)."""
    return {"id": ident, "kind": "rect", "width": width, "height": height, "fill": fill, **props}


def polygon(ident, points, fill, **props):
    return {"id": ident, "kind": "polygon", "points": [list(p) for p in points], "fill": fill, **props}


def path(ident, commands, fill=None, **props):
    return {"id": ident, "kind": "path", "commands": [list(c) for c in commands], "fill": fill, **props}


def text(ident, content, x, y, size=32, fill="#172f43", **props):
    return {"id": ident, "kind": "text", "text": content, "x": x, "y": y,
            "size": size, "fill": fill, **props}


def instance(ident, asset, **props):
    return {"id": ident, "kind": "instance", "asset": asset, **props}


def shot(ident, start, end, purpose, background, *nodes, **props):
    return {"id": ident, "start": start, "end": end, "purpose": purpose, "background": background,
            "nodes": list(nodes), **props}


def beat(ident, shot_id, frame, description, requirements, nodes):
    return {"id": ident, "shot": shot_id, "frame": frame, "description": description,
            "requirements": list(requirements), "nodes": list(nodes)}


def story(prompt, requirements, *, title="Untitled", fps=24):
    """An intentionally blank document. Supply shots, assets and beats before saving."""
    return {"schema_version": "kit.story/2.0", "title": title,
            "brief": {"prompt": prompt, "requirements": [{"id": i, "description": d} for i, d in requirements]},
            "fps": fps, "frames": 1, "assets": [], "shots": [], "beats": [], "audio": []}


def save(document, destination):
    value = copy.deepcopy(document)
    require_valid(value)
    atomic_json(Path(destination), value)
    return Path(destination)
