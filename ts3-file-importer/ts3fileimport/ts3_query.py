from typing import Dict

import requests
import sys

JsonIntParam = Dict[str, int]
JsonBody = Dict[str, str]


class TS3Query:
    def __init__(self, webquery_url: str, api_key: str):
        self.http_session = requests.Session()
        self.webquery_url = webquery_url
        self.api_key = api_key
        self._virtual_server_uid_cache: Dict[int, str] = {}
        self._channel_uid_cache: Dict[int, Dict[int, str]] = {}

    def query_ts3(self, query: str, params: JsonIntParam = None) -> JsonBody:
        url = f"{self.webquery_url}/{query}"
        req = requests.Request(
            'POST',
            url,
            headers={'x-api-key': self.api_key},
            json=params
        )
        try:
            response = self.http_session.send(req.prepare())
        except requests.exceptions.ConnectionError:
            print("Failed to connect to TeamSpeak 3 webquery. Is the server running?")
            sys.exit(1)
        if response.status_code != 200:
            raise requests.HTTPError(f"unexpected status code: {response.status_code}")
        json = response.json()
        status = json["status"]
        if status["code"] != 0:
            raise requests.HTTPError(status["message"])
        return json["body"][0]

    def query_virtual_server_unique_identifier(self, virtual_server_id: int) -> str:
        try:
            # Look into cache first to avoid spamming the TeamSpeak 3 server with the same request
            virtual_server_unique_identifier = self._virtual_server_uid_cache[virtual_server_id]
            # Cache hit
            return virtual_server_unique_identifier
        except KeyError:
            # Cache miss, query TeamSpeak 3 server
            try:
                json = self.query_ts3(f"{virtual_server_id}/serverinfo")
                virtual_server_unique_identifier = json["virtualserver_unique_identifier"]
                self._virtual_server_uid_cache[virtual_server_id] = virtual_server_unique_identifier
                return virtual_server_unique_identifier
            except requests.HTTPError as error:
                print(f"Failed to query virtual server unique identifier for virtual_server_id={virtual_server_id}: "
                      f"{error}")
                return ""

    def query_channel_unique_identifier(self, virtual_server_id: int, channel_id: int) -> str:
        try:
            # Look into cache as we might query the same channel id multiple times if there are folders inside
            channel_unique_identifier = self._channel_uid_cache[virtual_server_id][channel_id]
            # Cache hit
            return channel_unique_identifier
        except KeyError:
            try:
                json = self.query_ts3(f"{virtual_server_id}/channelinfo", {"cid": channel_id})
                channel_unique_identifier = json["channel_unique_identifier"]
                if virtual_server_id in self._channel_uid_cache:
                    self._channel_uid_cache[virtual_server_id][channel_id] = channel_unique_identifier
                else:
                    self._channel_uid_cache[virtual_server_id] = {channel_id: channel_unique_identifier}
                return channel_unique_identifier
            except requests.HTTPError as error:
                print(f"Failed to query channel unique identifier for channel_id={channel_id}: {error}")
                return ""
