from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from .contracts import loads, read_json
from .tools import Tools
from .transport import serve


def main():
    parser=argparse.ArgumentParser(description="Portable knowledge/tools for code-rendered animation")
    parser.add_argument("--workspace",default=".kit-workspace")
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("tools")
    sub.add_parser("serve",help="MCP stdio server")
    call=sub.add_parser("call")
    call.add_argument("tool")
    source=call.add_mutually_exclusive_group()
    source.add_argument("--input",help="JSON arguments file")
    source.add_argument("--json",default=None,help="JSON arguments; use --input for shell-safe file input")
    sub.add_parser("doctor")
    arguments=parser.parse_args()
    api=Tools(arguments.workspace)
    if arguments.command=="serve":
        serve(api)
        return
    if arguments.command=="tools":
        response=api.definitions
    elif arguments.command=="doctor":
        from .render import ffmpeg_path
        import PIL
        executable,version=ffmpeg_path()
        from .story import font
        for name in ("sans","display"): font(name,24)
        response={"python":sys.version.split()[0],"pillow":PIL.__version__,"ffmpeg_path":executable,"ffmpeg":version,"workspace":str(api.store.root),"backend":"authored2d_v2","bundled_fonts":"ok","video_generation_models":False}
    else:
        payload=read_json(arguments.input) if arguments.input else loads(arguments.json or "{}")
        response=api.call(arguments.tool,payload)
    print(json.dumps(response,indent=2))
    if isinstance(response,dict) and response.get("ok") is False:
        raise SystemExit(1)


if __name__=="__main__":
    main()
