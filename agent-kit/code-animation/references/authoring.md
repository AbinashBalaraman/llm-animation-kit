# Author new artwork and motion

Use `animation_kit.authoring` in a local Python script to construct a `kit.story/2.0` document. You supply the script adaptation, artwork, shots and timing. `save(document, path)` validates and writes portable JSON; CLI and MCP consume the same document.

```python
from animation_kit.authoring import *

doc = story(original_user_prompt, [
    ("subject", "Describe the subject's identifying visible features"),
    ("event", "Describe the requested visible action and its outcome"),
], title="Your title")
# Add your own assets, shots, beats and optional audio cues.
# Set doc['frames'] to the final shot's end, then save(doc, 'story.json').
```

There is deliberately no default artwork. The blank scaffold is not a completed scene.

## Drawing vocabulary

`ellipse(id, rx, ry, fill, **props)` is centred on its local origin. `rect(id, width, height, fill, **props)` extends right/down from its origin; optional `radius` rounds corners. `polygon(id, points, fill, **props)` accepts arbitrary geometry. `path(id, commands, fill=None, **props)` supports M/L/Q/C/Z commands with numeric coordinates; each subpath begins with M. Filled subpaths are painted individually, without even-odd holes.

`text(id, content, x, y, size=32, fill='#172f43', **props)` uses packaged fonts `sans` or `display`. Text is vertically centred; `align` is `left`, `center` (default), or `right`. Split multiline copy into individually positioned text nodes. Render text to check fit. Use concise, legible copy.

Every node can use `x`, `y`, `rotation` in degrees, `scale_x`, `scale_y`, `opacity`, `fill`, `stroke`, `stroke_width`. `group(id, *children, **props)` creates a local coordinate system. Put its origin at a joint for rotation. Later nodes cover earlier ones. Opacity is inherited per paint rather than offscreen group compositing. Negative scale mirrors an illustration. Shapes and text use their own paint properties; group paint is not inherited.

Design coordinates are 960×540. Output is 640×360 preview or 1280×720 final. Never position using output pixels. The optional camera is `{'x':480, 'y':270, 'zoom':1}` for the untransformed canvas; its fields may be animated.

## Reusable artwork and poses

An asset is `{'id':'your_asset', 'description':'what you drew', 'nodes':[...]}`. Assets hold static geometry; instances in shots provide motion. An asset can contain groups but not nested instances. Node IDs are unique within an asset or shot.

```python
actor = instance('actor', 'your_asset', x=480, y=400,
    overrides={'your_joint_id': {'rotation': track((0, 0), (18, -35), (30, 0))}})
```

Overrides target an original node ID anywhere inside that asset, changing transforms/paint for that instance only. Geometry remains editable in the asset definition. Author new shapes and joints as needed; there is no finite list of character types or gestures.

## Clocks and keyframes

Integer frames use 24, 30 or 60 fps. Shots cover `[0, frames)` exactly. **Tracks use local shot frames. Beats and audio cues use global frames.** `track((0, value), (12, next_value), ...)` holds before its first and after its last key. Keys strictly increase. A key at shot duration is a legal endpoint but is not rendered.

The destination key controls interpolation: `track((0,0), (20,100,'out_cubic'))`. Available easings: `linear`, `hold`, `smooth`, `in_cubic`, `out_cubic`, `out_back`. `hold` switches at the destination frame. Add anticipation and settling for a reason, rather than bouncing every object.

`shot(id, start, end, purpose, background, *nodes, camera=...)` builds a shot. `beat(id, shot_id, global_frame, description, requirement_ids, node_ids)` records where drawing demonstrates a requirement. Cite shot nodes/instances, not just text. This is a review plan, not semantic proof.

Optional audio cues have `frame`, `duration` in seconds, `frequency`, `gain` and `kind` (`bell`, `pop`, `purr`). These are conventional synthesized accents, not narration, music generation or a video model.

See `get_schema` for exact limits. `scripts/create_cat_president.py` and `scripts/create_space_toaster.py` demonstrate different art and actions. Read them for construction techniques, then invent the content your brief needs.
