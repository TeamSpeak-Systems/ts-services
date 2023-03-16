import argparse
from pathlib import Path

import sys

from ts3fileimport import TS3Collector, TS3Query


def main():
    parser = argparse.ArgumentParser(prog="TeamSpeak 3 file collector")
    parser.add_argument("--path", help="Root path of the TeamSpeak 3 server", required=True)
    parser.add_argument("--webquery", help="WebQuery base URL (default: http://localhost:10080",
                        default="http://localhost:10080")
    parser.add_argument("--apikey", help="API Key for WebQuery", required=True)
    args = parser.parse_args()

    ts3_server_path = Path(args.path)
    webquery_url = args.webquery
    api_key = args.apikey

    if not ts3_server_path.exists():
        print(f'Error: Path "{ts3_server_path}" does not exist')
        sys.exit(1)

    # Collect files from TS3
    ts3_query = TS3Query(webquery_url, api_key)
    ts3_collector = TS3Collector(ts3_server_path, ts3_query)
    ts3_collector.collect()

    # Serialize collected files to file
    export_file = "collected.dat"
    f = open(export_file, "wb")
    f.write(ts3_collector.serialize())
    f.close()

    print(f'Collected {len(ts3_collector.file_entries)} entries.')
    print(f'Collection from TeamSpeak 3 server done and saved to "{export_file}".')
    print('You can now shutdown the TeamSpeak 3 server, start the TeamSpeak 5 server and run import.')


if __name__ == "__main__":
    main()
