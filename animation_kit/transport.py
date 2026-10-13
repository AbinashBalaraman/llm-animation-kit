"""MCP stdio subset: initialize, ping, tools/list and tools/call."""
from __future__ import annotations
import base64
import json
import sys
from pathlib import Path

from .contracts import loads

PROTOCOLS=("2025-11-25","2025-06-18","2024-11-05")


def dispatch(api,message):
    if not isinstance(message,dict) or message.get("jsonrpc")!="2.0" or not isinstance(message.get("method"),str):
        return {"jsonrpc":"2.0","id":message.get("id") if isinstance(message,dict) else None,"error":{"code":-32600,"message":"Invalid JSON-RPC request"}}
    if "id" not in message:
        return None
    ident=message["id"]
    method=message["method"]
    params=message.get("params",{})
    if not isinstance(params,dict):
        return {"jsonrpc":"2.0","id":ident,"error":{"code":-32602,"message":"params must be an object"}}
    if method=="initialize":
        version=params.get("protocolVersion")
        result={"protocolVersion":version if version in PROTOCOLS else PROTOCOLS[0],"capabilities":{"tools":{"listChanged":False}},
                "serverInfo":{"name":"llm-animation-kit","version":"0.2.0"},"instructions":"Author original kit.story/2.0 artwork and motion from the brief. Never substitute a legacy demo. Use get_schema, preview_frames, preview and per-requirement review_story. No video-generation models."}
    elif method=="ping":
        result={}
    elif method=="tools/list":
        result={"tools":api.definitions}
    elif method=="tools/call":
        if not isinstance(params.get("name"),str) or not isinstance(params.get("arguments",{}),dict):
            return {"jsonrpc":"2.0","id":ident,"error":{"code":-32602,"message":"Tool name and object arguments required"}}
        response=api.call(params["name"],params.get("arguments",{}))
        result={"content":[{"type":"text","text":json.dumps(response)}],"structuredContent":response,"isError":not response["ok"]}
        # Explicit image request only; paths are created and validated by inspect_artifact.
        payload=response.get("result",{})
        if "response" in payload:
            payload=payload["response"].get("result",{})
        image_path=payload.get("image_path")
        if image_path:
            result["content"].append({"type":"image","mimeType":"image/png","data":base64.b64encode(Path(image_path).read_bytes()).decode()})
    else:
        return {"jsonrpc":"2.0","id":ident,"error":{"code":-32601,"message":"Method not supported"}}
    return {"jsonrpc":"2.0","id":ident,"result":result}


def serve(api):
    # stdout is protocol-only. Work is local and synchronous; no network transport.
    for line in sys.stdin:
        if len(line)>1_000_000:
            response={"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Request too large"}}
        else:
            try:
                response=dispatch(api,loads(line))
            except Exception as exc:
                response={"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":str(exc)}}
        if response is not None:
            print(json.dumps(response),flush=True)
