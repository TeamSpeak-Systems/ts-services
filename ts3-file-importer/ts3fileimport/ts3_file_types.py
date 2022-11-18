import urllib
import uuid
from enum import Enum
from pathlib import Path
from urllib.parse import quote

from .ts3_query import TS3Query

AVATAR_CHANNEL = "40d14a76-4337-5323-95f2-4c62fce1e5b6"
ICONS_CHANNEL = "cc5a2932-034e-554f-b74b-8fdfdaba1099"


class FileEntryType(Enum):
    INVALID = 0
    CHANNEL = 1
    FOLDER = 2
    ICON = 3
    AVATAR = 4


class FileEntry:
    type: FileEntryType = FileEntryType.INVALID

    def __init__(self, query: TS3Query, path: Path, virtual_server_id: int):
        self.folder_path = None
        self.path = path
        self.virtual_server_id = virtual_server_id
        self.virtual_server_unique_identifier = query.query_virtual_server_unique_identifier(self.virtual_server_id)

    def to_string(self) -> str:
        return f"type={self.type} virtual_server_id={self.virtual_server_id} " \
               f"virtual_server_unique_identifier={self.virtual_server_unique_identifier} " \
               f"path={self.path}"

    @staticmethod
    def virtual_server_unique_identifier_to_uuid(virtual_server_unique_identifier: str) -> str:
        namespace = uuid.UUID(hex="be19ddb5-09e8-4d1c-9c99-26e654be6879")
        return str(uuid.uuid5(namespace, virtual_server_unique_identifier))

    @staticmethod
    def _safe_name(filename: str) -> str:
        return urllib.parse.quote(filename, safe=".-_~!$&'()*+,;=:@")

    def channel_uid(self) -> str:
        return ""

    def to_url(self, base_url: str) -> str:
        safe_name = self._safe_name(self.path.name)
        virtual_server_uuid = self.virtual_server_unique_identifier_to_uuid(self.virtual_server_unique_identifier)
        return f"{base_url}/files/v1/upload/{virtual_server_uuid}/chan/{self.channel_uid()}/{safe_name}"


class ChannelFileEntry(FileEntry):
    type: FileEntryType = FileEntryType.CHANNEL

    def __init__(self, query: TS3Query, path: Path, virtual_server_id: int, channel_id: int, folder_path: str):
        super().__init__(query, path, virtual_server_id)
        self.channel_unique_identifier = query.query_channel_unique_identifier(self.virtual_server_id, channel_id)
        self.folder_path = folder_path

    def to_string(self) -> str:
        return super().to_string() + \
               f" channel_unique_identifier={self.channel_unique_identifier} folder_path={self.folder_path}"

    def channel_uid(self) -> str:
        return self.channel_unique_identifier

    def to_url(self, base_url: str) -> str:
        safe_name = self._safe_name(self.path.name)
        virtual_server_uuid = self.virtual_server_unique_identifier_to_uuid(self.virtual_server_unique_identifier)
        if self.folder_path == ".":
            path = safe_name
        else:
            path = f"{self.folder_path}/{safe_name}"
        return f"{base_url}/files/v1/upload/{virtual_server_uuid}/chan/{self.channel_unique_identifier}/{path}"


class FolderFileEntry(FileEntry):
    type: FileEntryType = FileEntryType.FOLDER

    def __init__(self, query: TS3Query, folder_path: str, virtual_server_id: int, channel_id: int):
        super().__init__(query, Path(), virtual_server_id)
        self.channel_unique_identifier = query.query_channel_unique_identifier(self.virtual_server_id, channel_id)
        self.folder_path = folder_path

    def to_string(self) -> str:
        return super().to_string() + \
               f" channel_unique_identifier={self.channel_unique_identifier} folder_path={self.folder_path}"

    def channel_uid(self) -> str:
        return self.channel_unique_identifier

    def to_url(self, base_url: str) -> str:
        vs_uuid = self.virtual_server_unique_identifier_to_uuid(self.virtual_server_unique_identifier)
        return f"{base_url}/files/v1/upload/{vs_uuid}/chan/{self.channel_uid()}/{self.folder_path}/.tsfolder"


class IconFileEntry(FileEntry):
    type: FileEntryType = FileEntryType.ICON

    def __init__(self, query: TS3Query, path: Path, virtual_server_id: int):
        super().__init__(query, path, virtual_server_id)
        self.path = path

    def channel_uid(self) -> str:
        return ICONS_CHANNEL

    def to_url(self, base_url: str) -> str:
        safe_name = self._safe_name(self.path.name)
        virtual_server_uuid = self.virtual_server_unique_identifier_to_uuid(self.virtual_server_unique_identifier)
        return f"{base_url}/files/v1/upload/{virtual_server_uuid}/chan/{self.channel_uid()}/icons/{safe_name}"


class AvatarFileEntry(FileEntry):
    type: FileEntryType = FileEntryType.AVATAR

    def __init__(self, query: TS3Query, path: Path, virtual_server_id: int):
        super().__init__(query, path, virtual_server_id)
        self.path = path

    def channel_uid(self) -> str:
        return AVATAR_CHANNEL
