import os
import pickle
from enum import Enum
from pathlib import Path
from typing import List

from .ts3_file_types import FileEntry, ChannelFileEntry, AvatarFileEntry, IconFileEntry, FolderFileEntry
from .ts3_query import TS3Query


class _ParseState(Enum):
    NONE = 0
    CHANNELS = 1,
    INTERNAL = 2,
    INTERNAL_ICONS = 3


class TS3Collector:

    def __init__(self, root_path: Path, query: TS3Query):
        self._root_path = root_path.resolve()
        self._files_path = self._root_path / "files"
        print(f"teamspeak3_server_path={self._root_path}")
        self._query = query
        self.file_entries: List[FileEntry] = []

    def collect(self):
        print(f"Collecting files from {self._files_path}")
        virtual_server_id: int = 0
        channel_id: int = 0
        current_virtual_server: str = ""
        current_channel: str = ""
        state: _ParseState = _ParseState.NONE

        for root, dirs, files in os.walk(self._files_path):
            root_path = Path(root)
            rb = root_path.name
            if root_path.is_dir():
                rs = root_path.as_posix().split("/")
                if rb.startswith("virtualserver_") and rs[len(rs) - 2] == "files":
                    rbs = rb.split("_")
                    virtual_server_id = int(rbs[1])
                    current_virtual_server = rb
                elif rb.startswith("channel_") and rs[len(rs) - 2] == current_virtual_server:
                    rbs = rb.split("_")
                    channel_id = int(rbs[1])
                    current_channel = rb
                    state = _ParseState.CHANNELS
                elif rb == "internal" and rs[len(rs) - 2] == current_virtual_server:
                    state = _ParseState.INTERNAL
                elif rb == "icons" and state == _ParseState.INTERNAL:
                    state = _ParseState.INTERNAL_ICONS

                if state == _ParseState.CHANNELS and rb != current_channel:
                    base_path = self._files_path / current_virtual_server / current_channel
                    folder_path = root_path.relative_to(base_path).as_posix()
                    self.file_entries.append(
                        FolderFileEntry(
                            self._query,
                            folder_path,
                            virtual_server_id,
                            channel_id
                        )
                    )

            for file in files:
                path = root_path / file
                if state == _ParseState.CHANNELS:
                    base_path = self._files_path / current_virtual_server / current_channel
                    folder_path = path.relative_to(base_path).parent.as_posix()
                    self.file_entries.append(ChannelFileEntry(
                        self._query,
                        path,
                        virtual_server_id,
                        channel_id,
                        folder_path))
                elif state == _ParseState.INTERNAL:
                    if file.startswith("avatar_"):
                        self.file_entries.append(
                            AvatarFileEntry(
                                self._query,
                                path,
                                virtual_server_id))
                    else:
                        print(f"*** Unexpected file in internal: {file}")
                elif state == _ParseState.INTERNAL_ICONS:
                    self.file_entries.append(
                        IconFileEntry(
                            self._query,
                            path,
                            virtual_server_id))
                elif state == _ParseState.NONE:
                    print("*** Invalid parse state")

    def serialize(self) -> bytes:
        return pickle.dumps(self)


def create_ts3_collector(data: bytes) -> TS3Collector:
    return pickle.loads(data)
