# TeamSpeak-Services - ts-services

The 'ts-services' repository is used for hosting the TeamSpeak 5 services as teamspeak_server, synapse, postgresql using docker compose.

    git clone https://github.com/TeamSpeak-Systems/ts-services

See also the documentation: 
* [ARCHITECTURE.md](ARCHITECTURE.md)
* [DEVELOPMENT.md](DEVELOPMENT.md)
* [MIGRATION.md](MIGRATION.md)

Note: Beginning with TeamSpeak 5 we run all server related programs in Linux using docker containers and docker compose.

## Requirements
* ts-services repository clone
* docker or docker desktop (Installation: https://docs.docker.com/desktop/install/windows-install/)
* routable ipv4/ipv6 setup and a working dns entry (i.e. myexample.com)

## Installation/Setup

The teamspeak_server_setup creates:
* creates the .env file with the passwords/api-keys from various services
* synapse: initial run with "generate" argument: creates homeserver.yaml; injects ts specific patch called teamspeakrules.py into the code-base; appserver config
* nginx: creates static json files which are generated from go template
* traefik: copies tsdynamic.yaml into volume

To run it type:
```sh
docker compose --profile setup pull
docker compose run --rm setup --domain=example.com --email=admin@example.com
```

## Starting the services

```sh
docker compose up -d
```

If you want to start it with http only:
```sh
docker compose -f docker-compose.yaml -f docker-compose.http.yaml up -d
```

## Reading the logs

Often one needs to see the output of the services to debug problems, this can be done with:

```sh
docker container ls --format "{{.Names}} -> {{.Image}}, named {{.ID}}, ({{.Status}})"
ts-services-feeder-1 -> teamspeaksystems/teamspeak_feeder:56-rc17, named 514a608b31d4, (Up 18 minutes)
ts-services-files-1 -> teamspeaksystems/teamspeak_files:56-rc17, named 17c126486a15, (Up 18 minutes)
ts-services-synapse-1 -> matrixdotorg/synapse:v1.61.0, named 37f9d40f1a90, (Up 18 minutes (healthy))
ts-services-events-1 -> teamspeaksystems/teamspeak_events:56-rc17, named 9a3076638cc3, (Up 18 minutes)
ts-services-auth-1 -> teamspeaksystems/teamspeak_auth:56-rc17, named 45889ef0d054, (Up 18 minutes)
ts-services-minio-1 -> minio/minio:RELEASE.2021-09-18T18-09-59Z, named 060fa3c98bce, (Up 18 minutes)
ts-services-postgresql-1 -> postgres:13-alpine, named 0202d83c3337, (Up 18 minutes)
ts-services-teamspeak-1 -> teamspeaksystems/teamspeak_server:56-rc17, named 82b7f960c8ac, (Up 18 minutes)
ts-services-appserver-1 -> teamspeaksystems/teamspeak_appserver:56-rc17, named 454612fb9603, (Up 17 minutes)
ts-services-discovery-1 -> teamspeaksystems/teamspeak_discovery:56-rc17, named 844e0ccd231d, (Up 18 minutes)
traefik -> traefik:v2.4.11, named 58969db9790c, (Up 18 minutes)
```

Then using the docker compose name:
```sh
docker container logs ts-services-teamspeak-1 -f -n 200
```

## Server admin token

To upgrade a normal login into an admin one can use a token, which can be obtained with this command:

```sh
docker exec -it ts-services-teamspeak-1 sh -c "cat logs/*|grep -o token=.* | sed 's/token=//g'"
rQ5ouq5TanxJdIxihUsQeu9b4cVmlsld2eHjOlmf
```

In the TS 5 Client you can 'use the privilege key', the _rQ5ouq5TanxJdIxihUsQeu9b4cVmlsld2eHjOlmf_,  to get administrative permissions.

Note: Teamspeak privilege keys work only once.

See also https://superuser.com/questions/491237/how-do-i-find-out-my-teamspeak-admin-key

## teamspeak_server license management

After you first start the `docker compose up` it will create a teamspeak_server folder or you can create it manually.

    ls teamspeak_server/
      query_ip_allowlist.txt
      query_ip_denylist.txt
      logs/

The teamspeak_server folder from the host, will be mapped into the teamspeak container and you should copy your license *licensekey.dat* into it.

Now you should probably restart the teamspeak service for it to read the new license. If not restarted it will check this location all 10 minutes and then update the running teamspeak service automatically.

This directory will also contain the logs from the teamspeak_server and you can use it to see what is going on inside without having to run:

    docker container logs ts-services-teamspeak-1 -f

## WebQuery (teamspeak_server administration)

In order to use the WebQuery API you need the API-KEY token which you can find in the .env file after running the setup.
It is called TEAMSPEAK_WEBQUERY_ADMIN_APIKEY.

```sh
curl -H "x-api-key: 5i7t1QEeqaNN7AnbvvvFlhE8xJvoqAsx " -X POST dev-ts-test.teamspeak.com:10080/119/serverstop
```

WARNING: Don't share this API-KEY with anyone you don't fully trust!

### WebQuery API documentation

Open this in your webbrowser:

https://example.com/teamspeak/v1/help (or try http, depending on your setup)

Note: WebQuery documentation is served from your teamspeak_server container.

## Stopping the services

```sh
docker compose down
```

## Deleting all data and starting from scratch (for developers)

With docker-desktop v4.11 you can simply clear the clutter like this:

WARNING: This will remove EVERYTHING -> all users, chat logs, settings, channels and so on.

```sh
rm .env
docker compose down -v --remove-orphans --rmi local
```

Now you have to run the pull/setup/up steap again.

Note: see also `docker compose down --help`


## Firewall Setup
These ports need to be opened in the firewall:
- 80 (tcp) - Only used by let's encrypt
- 443 (tcp)
- 9987, 9988, ... (udp, for each virtual server, beginning with 9987 by default)

## TeamSpeak vServer port forwarding
In order to use the docker compose setup with additonal TeamSpeak vServers you have to modify the following ports of the TeamSpeak service in the docker compose.yaml
```yaml
  teamspeak:
    image: teamspeaksystems/teamspeak_server:latest
    restart: on-failure
    ports:
      - "9987:9987/udp"
      #- "10022:10022/tcp"  # SSH serverquery
```
to
```yaml
  teamspeak:
    image: teamspeaksystems/teamspeak_server:latest
    restart: on-failure
    ports:
      - "9987-9997:9987-9997/udp"
      #- "10022:10022/tcp"  # SSH serverquery
```
The first port range refers to the machine itself, these are the public ports. The port range after the colon (:) specifies the inner ports that the various vServers provide. Here it is important that the internal ports match the ports of the vServers. The public ports can be changed according to availability and desire.

To use the SSH query the SSH query port must be enabled in docker compose.yaml. This can be achieved by uncommenting the port entry in the docker compose.yaml (shown above). It is also possible to map ports only to the local machine. For more information, see: https://docs.docker.com/compose/compose-file/compose-file-v3/#ports
