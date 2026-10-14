"""Host-side motion builders. Compile to ordinary tracks, never runtime code.

Coordinates and frames are shot-local. These helpers do not infer anatomy or
solve collisions: the author still chooses pivots, poses and contact times.
"""
import math
from .authoring import track
from .story import DEFAULTS, IDENTITY, multiply, point, transform, value_at


def arc(start, end, origin, destination, *, lift=60):
    """A ballistic-looking path with exact endpoints; positive lift arches up.

    Sample every integer frame so x/y interpolation cannot distort the path at
    rendered frames. Returns {x: track, y: track} for ** unpacking into a node.
    """
    if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end or end-start > 499:
        raise ValueError("arc needs 0 <= start < end and at most 500 samples")
    if not all(math.isfinite(v) for v in (*origin, *destination, lift)):
        raise ValueError("arc values must be finite")
    points=[]
    for frame in range(start, end+1):
        t=(frame-start)/(end-start)
        points.append((frame, origin[0]+(destination[0]-origin[0])*t,
                       origin[1]+(destination[1]-origin[1])*t-4*lift*t*(1-t)))
    return {name:track(*[(p[0],p[i]) for p in points],ease="linear") for i,name in [(1,"x"),(2,"y")]}


def follow_anchor(frames, transforms, anchor=(0, 0)):
    """Bake an anchor through an outer-to-inner transform chain into world x/y.

    Use for a held object or a matching release position. Include every parent
    transform and use every rendered frame for exact contact during rotation.
    Camera transforms are excluded: these are world coordinates. Move the held
    object to the shot root, or use a shared parent group instead.
    """
    frames=list(frames)
    if not frames or len(frames)>500 or any(not isinstance(f,int) or f<0 for f in frames) or frames!=sorted(set(frames)):
        raise ValueError("frames must be 1..500 increasing nonnegative integers")
    points=[]
    for frame in frames:
        matrix=IDENTITY
        for props in transforms:
            pose={k:value_at(props.get(k,v),frame) for k,v in DEFAULTS.items()}
            matrix=multiply(matrix,transform(pose))
        x,y=point(matrix,anchor)
        if not math.isfinite(x+y): raise ValueError("anchor transform must be finite")
        points.append((frame,x,y))
    return {name:track(*[(p[0],p[i]) for p in points],ease="linear") for i,name in [(1,"x"),(2,"y")]}
