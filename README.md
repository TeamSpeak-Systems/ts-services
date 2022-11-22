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
* routable ipv4/ipv6 setup
* dns entry (i.e. example.com)

## Installation/Setup

The ts-setup creates:
* creates *.env file* with the passwords/api-keys
* synapse: initial run with "generate" argument: creates homeserver.yaml; injects ts specific patch called teamspeakrules.py into the code-base; appserver config
* postgresql: creates users/databases used by the ts-services microservices

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

In the case you need to debug an issue, you can first list all current running Docker containers:

```sh
docker container ls --format "{{.Names}} -> {{.Image}}, named {{.ID}}, ({{.Status}})"
traefik -> traefik:v2.9.4, named f95a51320cc9, (Up 43 hours)
ts-services-discovery-1 -> gitlab.int.teamspeak.com:4567/teamspeak/ts-discovery:git-23e9735df2844ae4fe353e2e8ae67d1766eb998a, named 6e0a8995f134, (Up 43 hours)
ts-services-teamspeak-1 -> gitlab.int.teamspeak.com:4567/teamspeak/teamspeak_server:git-617029b6b5a328cc8c82194394a49d1c81bd66ac, named d5f909884097, (Up 43 hours)
ts-services-events-1 -> gitlab.int.teamspeak.com:4567/teamspeak/ts-events:git-aef7a22a98e0edaf8481854327e510f94386c556, named f1878a2dbb6a, (Up 43 hours)
ts-services-postgresql-1 -> postgres:13-alpine, named f33765fdc1b4, (Up 43 hours)
ts-services-appserver-1 -> gitlab.int.teamspeak.com:4567/teamspeak/ts-appserver:git-d4c585322ce7697e592099434ffe8dfb685714b1, named a01ded9df93e, (Up 43 hours)
ts-services-files-1 -> gitlab.int.teamspeak.com:4567/teamspeak/ts-files:git-60574e884bedfa0a076128ce99196cdcc8191cf0, named 522fee31f853, (Up 43 hours)
ts-services-feeder-1 -> gitlab.int.teamspeak.com:4567/teamspeak/ts-feeder:git-bc6d0d9f80bbd5bce79ce98fcfe5eb59199a20b7, named 6bed4b575f21, (Up 43 hours)
ts-services-minio-1 -> minio/minio:RELEASE.2021-09-18T18-09-59Z, named 2a4ef09c7030, (Up 43 hours)
ts-services-auth-1 -> gitlab.int.teamspeak.com:4567/teamspeak/ts-auth:git-3e0ef3df9bc7f287925732ea3aef3f8965fb53cd, named aa459f914d71, (Up 43 hours)
ts-services-synapse-1 -> matrixdotorg/synapse:v1.61.0, named 1b4d5ed9d79b, (Up 43 hours (healthy))`
```


Additional, you can check the logs of each individual Docker service by using the following command and the respective Docker container name:

```sh
docker container logs ts-services-teamspeak-1 -f
```

Using the key combination `Ctrl` and `C`, you can abort the log file follow.

## Server privilege key

To upgrade a normal login into an privileged, one can use a token, which can be obtained with this command:

```sh
docker exec -it ts-services-teamspeak-1 sh -c "grep 'token=' logs/*.log | cut -d '=' -f 2" | head -n 1
rQ5ouq5TanxJdIxihUsQeu9b4cVmlsld2eHjOlmf
```

In the TS 5 Client, right-click your server name and click on 'Use Privilege Key'. Insert your personal privilege key from the command above (in this example `rQ5ouq5TanxJdIxihUsQeu9b4cVmlsld2eHjOlmf`) and confirm the action to get administrative permissions.

Note: Teamspeak privilege keys work only once.

See also https://superuser.com/questions/491237/how-do-i-find-out-my-teamspeak-admin-key

## teamspeak_server license management

After you first start the `docker compose up` it will create a teamspeak_server folder or you can create it manually.

    ls teamspeak_server/
    query_ip_allowlist.txt
    query_ip_denylist.txt
    logs/

The teamspeak_server folder from the host, will be mapped into the teamspeak container, you should copy your license *licensekey.dat* into it.

Now you can restart the teamspeak service for it to read the new license:

    docker compose restart teamspeak

Note: If not restarted manually teamspeak service checks this location every 10 minutes and applies changes automatically without service interruption.

To see the logs you can also run:

    docker container logs ts-services-teamspeak-1 -f

This directory *teamspeak_server* on the host will also contain the logs.

## WebQuery (teamspeak_server administration)

In order to use the WebQuery API you need the API-KEY token which you can find in the *.env file*. It is called TEAMSPEAK_WEBQUERY_ADMIN_APIKEY.

```sh
curl -H "x-api-key: 5i7t1QEeqaNN7AnbvvvFlhE8xJvoqAsx" -X POST https://example.com/teamspeak/v1/serverinfo | jq -C '.'
```

WARNING: Don't share this TEAMSPEAK_WEBQUERY_ADMIN_APIKEY with anyone you don't fully trust!

### WebQuery API documentation

Open this in your webbrowser:

https://example.com/teamspeak/v1/help (or try http, depending on your setup)

Note: WebQuery documentation is served from your teamspeak_server container.

## Stopping the services

```sh
docker compose down
```

## Deleting all data and starting from scratch (for developers)

With docker-desktop v4.1x you can simply clear the clutter like this:

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
- 443 (tcp) - traefik serving discovery/teamspeak/files/minio/...
- 9987, 9988, ... (udp, for each virtual server, beginning with 9987 by default)
- 10011 raw (telnet support)
- 10022 ssh (ssh support)

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
