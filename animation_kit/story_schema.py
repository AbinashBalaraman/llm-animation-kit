"""The authored-vector contract. Primitives describe artwork, not story subjects."""


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


def arr(items, minimum=0, maximum=1000):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


ID = {"type": "string", "pattern": "^[a-z][a-z0-9_-]{0,63}$"}
TEXT = {"type": "string", "minLength": 1, "maxLength": 3000}
COLOR = {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"}
NUM = {"type": "number", "minimum": -10000, "maximum": 10000}
FRAME = {"type": "integer", "minimum": 0, "maximum": 7200}
EASING = {"enum": ["linear", "hold", "smooth", "in_cubic", "out_cubic", "out_back"]}
TRACK = obj({"keys": arr(obj({"frame": FRAME, "value": NUM, "ease": EASING},
                             ["frame", "value"]), 1, 500)})
VALUE = {"oneOf": [NUM, {"$ref": "#/$defs/track"}]}
PAINT = {"oneOf": [COLOR, {"type": "null"}]}
PROPS = {name: VALUE for name in ("x", "y", "scale_x", "scale_y", "rotation", "opacity")}
PROPS.update(fill=PAINT, stroke=PAINT, stroke_width={"type": "number", "minimum": 0, "maximum": 80})
POINT = arr(NUM, 2, 2)


def command(letter, count):
    return {"type": "array", "prefixItems": [{"const": letter}] + [NUM] * count,
            "items": False, "minItems": count + 1, "maxItems": count + 1}


def schema():
    common = {"id": ID, **PROPS}
    types = []
    for kind, fields, required in [
        ("group", {"children": arr({"$ref": "#/$defs/node"}, 1, 600)}, ["children"]),
        ("ellipse", {"rx": {"type": "number", "exclusiveMinimum": 0, "maximum": 4000},
                     "ry": {"type": "number", "exclusiveMinimum": 0, "maximum": 4000}}, ["rx", "ry"]),
        ("rect", {"width": {"type": "number", "exclusiveMinimum": 0, "maximum": 8000},
                  "height": {"type": "number", "exclusiveMinimum": 0, "maximum": 8000},
                  "radius": {"type": "number", "minimum": 0, "maximum": 4000}}, ["width", "height"]),
        ("polygon", {"points": arr(POINT, 3, 500)}, ["points"]),
        ("path", {"commands": arr({"oneOf": [command("M", 2), command("L", 2), command("Q", 4),
                                                       command("C", 6), command("Z", 0)]}, 2, 500)}, ["commands"]),
        ("text", {"text": {"type": "string", "minLength": 1, "maxLength": 500},
                  "font": {"enum": ["sans", "display"]},
                  "size": {"type": "number", "minimum": 8, "maximum": 400},
                  "align": {"enum": ["left", "center", "right"]}}, ["text", "size"]),
        ("instance", {"asset": ID, "overrides": {"type": "object", "propertyNames": ID,
                                                  "additionalProperties": obj(PROPS, [])}}, ["asset"]),
    ]:
        types.append(obj({**common, "kind": {"const": kind}, **fields}, ["id", "kind", *required]))
    shot = obj({"id": ID, "start": FRAME, "end": FRAME, "purpose": TEXT, "background": COLOR,
                "camera": obj({"x": VALUE, "y": VALUE, "zoom": VALUE}),
                "nodes": arr({"$ref": "#/$defs/node"}, 1, 600)},
               ["id", "start", "end", "purpose", "background", "nodes"])
    result = obj({
        "schema_version": {"const": "kit.story/2.0"}, "title": TEXT,
        "brief": obj({"prompt": TEXT, "requirements": arr(obj({"id": ID, "description": TEXT}), 1, 24)}),
        "fps": {"enum": [24, 30, 60]}, "frames": {"type": "integer", "minimum": 1, "maximum": 7200},
        "assets": arr(obj({"id": ID, "description": TEXT, "nodes": arr({"$ref": "#/$defs/node"}, 1, 600)}), 0, 100),
        "shots": arr(shot, 1, 40),
        "beats": arr(obj({"id": ID, "shot": ID, "frame": FRAME, "description": TEXT,
                          "requirements": arr(ID, 1, 24), "nodes": arr(ID, 1, 40)}), 1, 120),
        "audio": arr(obj({"frame": FRAME, "duration": {"type": "number", "exclusiveMinimum": 0, "maximum": 5},
                          "frequency": {"type": "number", "minimum": 40, "maximum": 4000},
                          "gain": {"type": "number", "minimum": 0, "maximum": 0.5},
                          "kind": {"enum": ["bell", "pop", "purr"]}}), 0, 200)
    })
    result.update({"$schema": "https://json-schema.org/draft/2020-12/schema",
                   "$id": "urn:animation-kit:story:2.0", "$defs": {"node": {"oneOf": types}, "track": TRACK}})
    return result
