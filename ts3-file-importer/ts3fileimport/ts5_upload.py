import base64
import mimetypes
import tempfile
from pathlib import Path
from typing import Dict

import jwt
import requests
import sys
import time

from .ts3_file_types import FileEntry, FileEntryType


class TS5Upload:

    def __init__(self, root_path: Path, base_url: str):
        self.http_session = requests.Session()
        self._root_path = root_path.resolve()
        self._base_url = base_url
        filetransfer_secret = self._read_filetransfer_secret_from_env()
        self._decoded_secret = base64.decodebytes(filetransfer_secret.encode("ascii"))
        self._authentication_token = self._create_authorization_token()
        self._tsfolder = self._create_tsfolder_temp_file()

    def _read_filetransfer_secret_from_env(self) -> str:
        env_path = self._root_path / ".env"
        print(f"Reading env from: {env_path}")
        try:
            env = open(env_path, "rt")
        except FileNotFoundError:
            print(f'"{env_path}" not found. Invalid path specified or the TeamSpeak 5 server was not yet setup.')
            sys.exit(1)
        lines = env.readlines()
        marker = "FILETRANSFER_TOKEN_SECRET="
        for line in lines:
            if line.startswith(marker):
                return line[len(marker):].strip()
        raise Exception(f"Failed to read FILETRANSFER_TOKEN_SECRET from {env_path}")

    def _create_authorization_token(self) -> str:
        now = int(time.time())
        expires = now + 600  # 10 minutes
        key_name = "tsserver"
        payload = {
            "sub": "*,*,*",
            "aud": "TeamSpeak Filetransfer",
            "iat": now,
            "exp": expires,
            "http://v1.teamspeak.com/perm": {
                "upload": ".*",
            },
            "http://v1.teamspeak.com/sq": {
                "read": -1,
                "write": -1,
                "store": -1
            },
            "http://v1.teamspeak.com/cq": {
                "read": -1,
                "write": -1,
                "store": -1
            },
            "http://v1.teamspeak.com/uq": {
                "read": -1,
                "write": -1,
                "store": -1
            },
            "http://v1.teamspeak.com/fs": -1
        }
        res = jwt.encode(payload, self._decoded_secret, algorithm="HS512", headers={"kid": key_name})
        if type(res) is bytes:
            res = res.decode("ascii")
        return res

    def _create_headers(self, file_entry: FileEntry) -> Dict[str, str]:
        return {
            "Authorization": "Bearer " + self._authentication_token,
            "X-Upload-Content-Length": str(file_entry.path.stat().st_size),
            "X-Upload-Content-Type": self._get_content_type(file_entry)
        }

    @staticmethod
    def _get_content_type(file_entry: FileEntry) -> str:
        content_type, content_encoding = mimetypes.guess_type(file_entry.path)
        if content_type is None:
            return "application/octet-stream"
        else:
            if not (content_encoding is None):
                return content_type + "; encoding=" + content_encoding
            return content_type

    @staticmethod
    def _create_tsfolder_temp_file() -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="ts5_file_importer_")) / ".tsfolder"
        tmp.touch()
        return tmp

    def cleanup(self):
        self._tsfolder.unlink(missing_ok=True)
        try:
            self._tsfolder.parent.rmdir()
        except IOError:
            pass

    def upload(self, file_entry: FileEntry):
        if file_entry.type == FileEntryType.FOLDER:
            file_entry.path = self._tsfolder

        url = file_entry.to_url(self._base_url)
        if len(url) == 0:
            return
        # print(f"url: {url}")
        headers = self._create_headers(file_entry)
        # print(f"headers: {headers}")

        try:
            req = requests.post(url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Failed to connect to TeamSpeak 5. Is the server running?")
            sys.exit(1)
        if req.status_code != 200:
            print(f"Error {req.status_code}:{req.text}")
            return

        result = req.json()
        method = result["method"]

        if method == "s3v1":
            put_headers = result["headers"]
            if file_entry.path.stat().st_size == 0:
                req = requests.put(result["location"], headers=put_headers)
            else:
                file_data = open(file_entry.path, "rb")
                req = requests.put(result["location"], file_data, headers=put_headers)

            if req.status_code != 200:
                print(f"*** Error {req.status_code}:{req.text}")
            else:
                file_name = file_entry.path.name
                if file_name != ".tsfolder":  # Skip these in console output
                    print(f"Uploaded: {file_name}")
        else:
            print(f"unsupported method: {method}")
