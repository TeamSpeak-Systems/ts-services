import argparse
from pathlib import Path

import sys

from ts3fileimport import TS5Upload, create_ts3_collector


def main():
    parser = argparse.ArgumentParser(prog="TeamSpeak 5 file importer")
    parser.add_argument("--path",
                        help='Root path of the TeamSpeak 5 server with the docker-compose.yaml file (default: ".."',
                        default="..")
    parser.add_argument("--url", help='TeamSpeak 5 server base domain, e.g. "https://example.com"', required=True)
    args = parser.parse_args()

    ts5_server_path = Path(args.path)
    ts5_base_url = args.url

    if not ts5_server_path.exists():
        print(f'Error: Path "{ts5_server_path}" does not exist')
        sys.exit(1)

    ts5_upload = TS5Upload(ts5_server_path, ts5_base_url)

    # Read collected files from serialized file
    export_file = "collected.dat"
    export_path = Path(export_file)
    if not export_path.exists():
        print(f'Error: "{export_file}" does not exist')
        sys.exit(1)
    f = open(export_file, "rb")
    data = f.read()
    f.close()
    ts3_collector = create_ts3_collector(data)

    # Upload files to TS5 via upload API
    for file_entry in ts3_collector.file_entries:
        ts5_upload.upload(file_entry)

    ts5_upload.cleanup()

    print(f'Imported {len(ts3_collector.file_entries)} files')
    print(f'Import done. You can delete "{export_file}" unless you want to run import again')


if __name__ == "__main__":
    main()
