"""Atomic immutable snapshots and optimistic revision transactions."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .contracts import KitError, read_json, require_valid


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(value,stream,indent=2,allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def project(self, project_id):
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,47}",project_id):
            raise KitError("invalid_id","Use a lowercase project ID of up to 48 letters/digits/_/-.")
        path = (self.root/project_id).resolve()
        if not path.is_relative_to(self.root):
            raise KitError("path_escape","Project must stay within the configured workspace.")
        for name in ("snapshots","renders"):
            if not (path/name).resolve().is_relative_to(self.root):
                raise KitError("path_escape","Project subdirectory escapes the workspace.")
        return path

    @contextmanager
    def lock(self, project_id):
        path = self.project(project_id)
        path.mkdir(parents=True,exist_ok=True)
        lock = path/".write-lock"
        try:
            descriptor = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        except FileExistsError as exc:
            raise KitError("busy","Project is being written. Retry later; investigate a stale lock after a crash.") from exc
        try:
            os.write(descriptor,str(os.getpid()).encode())
            yield path
        finally:
            os.close(descriptor)
            lock.unlink(missing_ok=True)

    def load(self, project_id, revision=None):
        path = self.project(project_id)
        try:
            pointer = read_json(path/"current.json")
            revision = pointer["revision"] if revision is None else revision
            if not isinstance(revision,int) or revision<0:
                raise KitError("invalid_revision","Revision must be a nonnegative integer.")
            snapshot_path=(path/"snapshots"/f"{revision:06d}.json").resolve()
            if not snapshot_path.is_relative_to(self.root):
                raise KitError("path_escape","Snapshot escapes workspace.")
            snapshot = read_json(snapshot_path)
            if digest(snapshot["scene"]) != snapshot["scene_hash"]:
                raise KitError("corrupt_snapshot","Snapshot content hash does not match.")
            if revision==pointer["revision"] and snapshot["scene_hash"]!=pointer["scene_hash"]:
                raise KitError("corrupt_pointer","Current pointer does not match snapshot.")
            require_valid(snapshot["scene"])
            return snapshot
        except FileNotFoundError as exc:
            raise KitError("not_found",f"Project/revision does not exist: {project_id}/{revision}") from exc

    def _publish(self,path,scene,revision,parent,operations):
        value={"revision":revision,"parent":parent,"scene":scene,"scene_hash":digest(scene),"operations":operations,"created_at":time.time()}
        atomic_json(path/"snapshots"/f"{revision:06d}.json",value)
        atomic_json(path/"current.json",{"revision":revision,"scene_hash":value["scene_hash"]})
        return {"revision":revision,"scene_hash":value["scene_hash"],"invalidated":["frames","trace","contact_sheet","video","review"]}

    def create(self,project_id,scene):
        require_valid(scene)
        with self.lock(project_id) as path:
            if (path/"current.json").exists():
                raise KitError("exists","Project already exists; use a revision or a new ID.")
            return self._publish(path,scene,0,None,[{"type":"create"}])

    def revise(self,project_id,expected_revision,operations):
        with self.lock(project_id) as path:
            current=self.load(project_id)
            if current["revision"] != expected_revision:
                raise KitError("stale_revision",f"Expected {expected_revision}; current is {current['revision']}.",hint="Inspect the project before proposing a new revision.")
            scene=copy.deepcopy(current["scene"])
            for operation in operations:
                kind=operation["type"]
                def find(items,ident):
                    item=next((item for item in items if item["id"]==ident),None)
                    if item is None:
                        raise KitError("missing_id",f"Unknown ID: {ident}")
                    return item
                if kind=="replace_action":
                    old=find(scene["actions"],operation["action"]["id"])
                    scene["actions"][scene["actions"].index(old)]=copy.deepcopy(operation["action"])
                elif kind=="add_action":
                    scene["actions"].append(copy.deepcopy(operation["action"]))
                elif kind=="remove_action":
                    scene["actions"].remove(find(scene["actions"],operation["action_id"]))
                elif kind=="shift_action":
                    action=find(scene["actions"],operation["action_id"])
                    action["start"]+=operation["delta"]
                    action["end"]+=operation["delta"]
                elif kind=="set_camera":
                    find(scene["shots"],operation["shot_id"])["camera"]=copy.deepcopy(operation["camera"])
                elif kind=="set_actor":
                    find(scene["actors"],operation["actor"]["id"]).update(operation["actor"])
                elif kind=="set_title":
                    scene["title"],scene["subtitle"]=operation["title"],operation["subtitle"]
                else:
                    raise KitError("unsupported_operation",f"Unknown operation: {kind}")
            require_valid(scene)
            return self._publish(path,scene,current["revision"]+1,current["revision"],operations)

    def undo(self,project_id,expected_revision,target_revision):
        with self.lock(project_id) as path:
            current=self.load(project_id)
            if current["revision"]!=expected_revision:
                raise KitError("stale_revision","Current revision changed.")
            if target_revision>=current["revision"]:
                raise KitError("invalid_undo","Undo must target an earlier immutable revision.")
            target=self.load(project_id,target_revision)
            return self._publish(path,target["scene"],current["revision"]+1,current["revision"],[{"type":"undo","target_revision":target_revision}])
