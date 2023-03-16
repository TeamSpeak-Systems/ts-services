# ts3-file-importer

Utility script to import files from a TeamSpeak 3 Server.

Supported file types for import:

- Files and folders in channels
- Avatars
- Server icons

This utility needs to be run in two steps:

1) Import files from a running TeamSpeak 3 server, stores the serialized result in a file "collected.dat"
2) Upload previously collected files to a running TeamSpeak 5 server

As it may be difficult to run two servers on the same machine at the same time, the two-step import assists to start a
TeamSpeak 3 server, collect, shut it down, then start a migrated TeamSpeak 5 server, start it and upload the files to
it.

### Requirements

- Python >= 3.10.0
- Pip packages: requests, PyJWT

You might want to use a virtual environment to avoid polluting your global pip installation:

```sh
$ python -m venv env
$ env\Scripts\activate
$ pip install requests PyJWT
$ pip install PyJWT
```

### Howto

- Start your TeamSpeak 3 server which you want to migrate to TeamSpeak 5
- Have webapi key with admin scope for this TeamSpeak 3 server
- Run the collect.py script:
  ```sh
  $ python collect.py --path=<teamspeak-3-root-path> --webquery=<webquery-url> --apikey=<webquery-api-key>
  ```
- Shutdown TeamSpeak 3 server
- Prepare a TeamSpeak 5 installation migrated from the TeamSpeak 3 server from which we collected the files. See the
  Migration section in the top-level Readme.
- Import the collected files:
  ```sh
  $ python import.py --path=.. --url=https://example.com
  ```
- Delete collected.dat in the working directory

### Example

```sh
$ python collect.py --path=~/teamspeak-3-server --webquery=http://localhost:10080 --apikey=SECRET
$ python import.py --path=.. --url=https://example.com
```

### Note

If your TeamSpeak 5 Server is using a self-signed https certificate, the import process will fail. As a workaround,
temporarily start the TeamSpeak 5 server in http mode, see the top-level Readme.
