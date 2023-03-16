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
ts-services-discovery-1 -> teamspeaksystems/teamspeak_discovery:beta-58rc14, named 5fea456a1100, (Up 2 minutes)
ts-services-synapse-1 -> matrixdotorg/synapse:v1.61.0, named a8e29c03f129, (Up 2 minutes (healthy))
ts-services-teamspeak-1 -> teamspeaksystems/teamspeak_server:v5.0.0-beta14-rc2, named 28e9c6618e0c, (Up 2 minutes)
ts-services-auth-1 -> teamspeaksystems/teamspeak_auth:beta-58rc14, named 1554a8ebc19f, (Up 2 minutes)
ts-services-files-1 -> teamspeaksystems/teamspeak_files:beta-58rc14, named e5e36ef49577, (Up 2 minutes)
traefik -> traefik:v2.9.4, named 33dda4343c4a, (Up 2 minutes)
ts-services-minio-1 -> minio/minio:RELEASE.2021-09-18T18-09-59Z, named 408ab6fb0605, (Up 2 minutes)
ts-services-feeder-1 -> teamspeaksystems/teamspeak_feeder:beta-58rc14, named fa6cb337ea24, (Up 2 minutes)
ts-services-appserver-1 -> teamspeaksystems/teamspeak_appserver:beta-58rc14, named df8e347a9495, (Up 2 minutes)
ts-services-events-1 -> teamspeaksystems/teamspeak_events:beta-58rc14, named 92e0b2f6da88, (Up 2 minutes)
ts-services-postgresql-1 -> postgres:13-alpine, named 071f06faa138, (Up 2 minutes)
```


Additional, you can check the logs of each individual Docker service by using the following command and the respective Docker container name:

```sh
docker container logs ts-services-teamspeak-1 -f
```

Using the key combination `Ctrl` and `C`, you can abort the log file follow.

## Server privilege key

To upgrade a normal login into an privileged, one can use a token, which can be obtained with this command:

```sh
docker exec -it ts-services-teamspeak-1 sh -c "grep 'token=' logs/*.log | cut -d '=' -f 2" | tail -n 1
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

## ACME

The let's encrypt certificate is in the traefik volume and can be extracted or restored. This is important if you fear that the let's encrypt quota might be exceeded.

Backup:
```sh
docker container cp traefik:/acme/acme.json .
```

Restore:
```sh
docker container cp acme.json traefik:/acme/
docker exec -it traefik
-> chmod 0700 /acme/acme.json
-> chown root:root /acme/acme.json
docker container restart traefik
```

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
