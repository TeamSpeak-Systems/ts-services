# TeamSpeak 5 Service Overview

Starting with version 5, the TeamSpeak Server is a collection of services. At the time of
writing this document, it consists of the following services.

* **Discovery**: This informs the outside world of the location of servicves.
* **Voice**: This handles all the voice chat traffic.
* **Chat**: This handles all the text chat traffic.
* **Files**: This handles all files and images for chat and file browser.
* **Auth**: This handles access to services.
* **Events**: This can be configured to do actions on certain TeamSpeak events.
* **Public Listing**: This keeps the teamspeak server list up-to-date about the local teamspeak server voice servers and chats.

All these services run in one or more domains. To run a TeamSpeak Server that can chat with users on other servers, a unique domain name is required, and it is required that http traffic to it is secured with TLS (https).

---

## Services in Detail

In this section the services listed in the overview will be discussed in more detail.

### Discovery

Discovery is used by the TeamSpeak Client and other external services to find the right location for the services of this TeamSpeak Server. This is done using the `/.well-known/` namespace of your domain. This namespace is further subdivided into **matrix** and **teamspeak**.

The Matrix namespace handles discovery for Matrix chat. More information on that can be found in the Matrix [client](https://matrix.org/docs/spec/client_server/latest#well-known-uri) and [server](https://matrix.org/docs/spec/server_server/latest#resolving-server-names) documentation.

The teamspeak namespace handles discovery for the TeamSpeak Client. When the client wants to know for example the location of the media server it will check `teamspeak/UUID-of-the-server`. A concrete example is:

`https://example.com/.well-known/teamspeak/09ac35cc-e69f-5112-ba73-7e3d5d027050`

The response is a JSON object with the locations of the known TeamSpeak services. An example is:

``` JSON
{
  "teamspeak.server": {
    "base_url": "https://example.com/teamspeak"
  },
  "teamspeak.serverUUID": {
    "34203423-234v2342k-23v4234k-233452": "https://example.com/teamspeak1"
    "234-456n4567-ghjmgasdfasdfasd-45n7": "https://example.com/teamspeak1"
  },
  "chat" : {
    "domain": "https://example.com"
  },
  "files" : {
    "base_url": "https://example.com/files"
  },
  "authorization" : {
    "base_url": "https://example.com/authorization"
  },
  "invites" : {
    "base_url": "https://example.com/invites"
  }
}
```

* **teamspeak.server.base_url**: is the url to the TeamSpeak server web query
* **chat.domain**: is the domain name used by the Matrix server that handles chat for this virtual server. Note that this does not need to be the same as the domain the Teamspeak server is running on.
* **files.base_url**: is the url to the files service.
* **autorization.base_url**: is the url to the auth service.
* **invites**: this is the url to the short url service.

The domain where this TeamSpeak `.well-known` information is hosted, is stored in the virtual server property `virtualserver_administrative_domain`. After a TeamSpeak Client has connected to a server it will read this virtual server property so it can locate the associated services.

Server administrators have to set this property or else the client can not function properly. This can currently only be done by setting the TeamSpeak Server commandline parameter `administrative_domain` to the right domain. Alternatively, this can be set with the same parameter name in a yaml config file.

### Voice

The voice service handles the voice chats. This is implemented by the TeamSpeak 5 core server. The voice part works the same as TeamSpeak 3. It is assumed that the audience of this document knows enough about TeamSpeak 3.

### Chat

TeamSpeak 3 handled a limited form of chat over the TeamSpeak Server. In TeamSpeak 5 all text chats go over the Matrix protocol. At the moment TeamSpeak 5 assumes this is done by [Synapse](https://matrix.org/docs/projects/server/synapse), although the only real dependency is that the Matrix server supports the JWT login method.

A TeamSpeak Client connected to a TeamSpeak Server can request a chat login token. The server will return a JWT which the client can then use to login to Matrix.

The TeamSpeak server an be configured with a yaml config file which includes a section like this:

``` yaml
chat:
  token duration seconds: 60
  jwt shared secret: NgeC1q8Qd7aF0kaXd3O5vBoN7vfiOKYh
```

The `token duration seconds` parameter specifies how long the login token is valid for. The `jwt shared secret` parameter is the shared secret that also has to be configures in the Matrix server.

Every client that connects to a TeamSpeak Server will login to Matrix using this method, in order for it to participate in channel chats. Clients can also request a TeamSpeak Server to be its **Homebase**. When set, the client will also use the Matrix server for other (non-channel) chats, like public group chats.

### Files

This service is responsible or storing and serving files. This ranges from icons and avatars for the TeamSpeak server, to just files in the TeamSpeak file browser, to media (images etc.) in chat.

Clients that want to upload or download a file from this service, first get a token from the TeamSpeak Server which specifies the access rights and quota for a specific storage location. The client then does a http request to the files service using this token.

### Auth

This service currenlty does just one thing. It is planned that in the future it will take care of autentication and authorization for all the TeamSpeak 5 services that require it.

For now, it will hand out access tokens for the **files** service in order for TeamSpeak users from different virtual servers or domains to download chat media.

### Events

This service receives events from the TeamSpeak Server only at the moment, but in the future this can be expanded to the other serivices as well. It can be configured to post certain events to a URL. An example is that when a client is deleted on the TeamSpeak Server, the event service will notify the files service so it can delete user related files like avatar images.

This service can be used to let al sorts of services react to evens happening in teamspeak.

### Public Listing

This service makes a list of public text chats and TeamSpeak voice services and publishes that periodically to TeamSpeak. Users on can then search for chats on the myTeamSpeak website.

## Services in the Docker-Compose reference implementation

Starting with TeamSpeak 5, TeamSpeak will distribute its services in the form of docker images on **Docker Hub**. To show how these services can be configured to work together, and to provide home users with an easy way to setup a teamspeak server, TeamSpeak will distribute an archive which contains a docker-compose reference implementation. With a few simple commands all the services can be setup. The requirements for this to work is that docker is setup and running. This might be difficult for the non-technical enthusiast.

The archive provided by TeamSpeak contains a **docker-compose.yaml** file which is used by docker-compose to setup and run all the services. Additionally it contains some extra configuration files.

The image below attempts to convey the services that are running in the docker-comopse stack and how they are connected.

<img src="teamspeak-services-diagram/teamspeak-services-diagram.svg">

Note: Please see [teamspeak-services-diagram/README.md](teamspeak-services-diagram/README.md) how to update this diagram!

### Traefik

For HTTPS all network traffic is passed to [Traefik](https://traefik.io/traefik/). This service is a reverse HTTP proxy. It first decrypts the HTTPS traffic to HTTP. It will then look at the URL that is requested and then send the request to the proper service unencrypted.

As mentioned, Traefik handles HTTPS traffic. By default, Traefik is configured to use [Let's Encrypt](https://letsencrypt.org/) to obtain and use an SSL certificate for your domain. This default should ensure that the administrator does not need to do any additional steps to setup encryption besides running our setup utility which is discussed later.

Interactions:

* TeamSpeak WebQuery
* Synapse
* Filetransfer
* MinIO (actual file upload/download)
* Invites
* Auth
* Central-Search-Feeder
* discovery

### TeamSpeak

This is the TeamSpeak Server which takes care of the voice service. By default only UDP port **9987** is forwarded from the outside to the TeamSpeak Server inside docker.

Interactions:

* PostrgreSQL for database.
* The raw and SSH query ports are not opened to the internet.
* The HTTP query port is open to the internet. The prefix to contact it should be https://domain/teamspeak/v1 . An example query could be https://example.com/teamspeak/v1/d98879f9-9a83-53d4-8a93-2ee22a345eaf/serverinfo .
* Events to export events, although technically, TeamSpeak puts events into a PostrgreSQL table which the Events service then reads.
* TeamSpeak is configured with shared secrets so it can create access tokens for chat (Synapse) and file (Filetransfer) which the TeamSpeak Client can use.
* Virtual TeamSpeak voice servers can be configured with "file tranfer classes" which specify the file size limits and quota for clients.

### Synapse

[Synapse](https://matrix.org/docs/projects/server/synapse) service takes care of text chat.

Interactions:

* TeamSpeak creates jwt login tokens that clients use to log into Synapse
* Synapse loads a module with custom rules from TeamSpeak at startup
* Synapse sends events concerting TeamSpeak users and rooms to the Matrix-Appserver
* The Matrix-Appserver can send commands to Synaps en reaction to Synapse and TeamSpeak events
* Synapse uses PostgreSQL for its data storage
* Auth servers from this or remote servers can query Synapse for Authentication (OpenID)
* Central Search Feeder queries Synapse for public rooms

### (Matrix-)Appserver

This service is a Matrix Application Server. It receives events from Matrix(Synapse) and acts on them to enforce TeamSpeak rules. In addition, this service receives events from TeamSpeak through the events service and also acts on those.

#### Interactions:

* Gets events from Synapse
* Gets events from TeamSpeak
* Sends commands to Synapse

### Discovery

[nginx](https://www.nginx.com) is a webserver component to provide discovery. It hosts the .well-known files described in [Discovery](###Discovery). In the reference implementation the .well-known/teamspeak location cheats a bit and returns the same information for any virtual server UUID, regardless of whether it exists or not.

This service does not interact with any other service, besides Traefik.

### Filetransfer

The filetransfer server takes care of media, or more specifically files. The TeamSpeak Client will upload and download images and other files used by the TeamSpeak Server and text chats. It will do this by redirecting upload and download requests to an S3 compatible bucket using signed urls. This has the advantage that if the S3 bucket is hosted off-site, there is no traffik for the uploaded and downloaded files from the filetransfer server and the bucket. Instead, the TeamSpeak Client will send or get the files directly from the S3 bucket. By default the reference implementation includes a minio server which is used as the S3 compatible bucket.

#### Interactions:

* Send delete commands to the S3 bucket.
* Receives events from Event service, for example when a user, channel or virtual server is deleted.
* Gets callbacks (webhook) from minio when files are uploaded or removed.

### MinIO

[MinIO](https://min.io) MinIO offers high-performance, S3 compatible object storage. It is used by the filetransfer service to store and serve files and media. Note that TeamSpeak Client ultimately do the uploading and downloading of files to and from this server. The filetransfer server points to this service for the actual uploading and downloading. Files are stored to a docker volume also called minio on your local machine.

#### Interactions:

* Sends events to filetransferserver when an object(file) is uploaded or deleted
* Filetransfer server gives delete object commands to MinIO.

### PostgreSQL

[PostgreSQL](https://www.postgresql.org) is a relational database which is used by some services to persist data.

#### The following services use postgresql to persist data:

* TeamSpeak
* Events
* Synapse
* Filetransfer
* Invites

### Auth

This service currently only has one taks. Hand out filetransfer access tokens to chat users who want to download media from chats hosted on this domain.

#### Interations:

* Consults Synapse to see if requesting user is part of the desired chat.

### Invites

This services can create and update short urls.

#### Interactions:

* Checks TeamSpeak for permissions

### Events

This service reacts to events which TeamSpeak stores in Postgresql. It then sends the events out to registered webhooks. Currently there is no API to register new webhooks and there are just two webhooks by default. One to the matrix-appserver and one to filetransfer.

#### Interactions:

* Receives signals from postgresql when TeamSpeak writes an event
* Sends events to registered webhooks, currently only filetransferserver and appserver

### Central-Search-Feeder

Implements the public listing service. This service send TeamSpeak server summary info and public chat room info to a public listing service hosted by TeamSpeak Systems GmbH.

##### Interactions:

* Queries TeamSpeak servers for virtual server info
* Queries Synapse for public room (chat) info

## Client-Server Interaction

In this section a brief overview is given on how certain actions make the client interact with the different services.

### TeamSpeak Voice

This is the same as with TeamSpeak 3. The TeamSpeak Client connects to the TeamSpeak Server over a UDP port. A TeamSpeak Server can be found by several methods. The client specifies a server name to connect to, or a raw ip and port. In the case of a raw ip, the client connects to that. In the case of a name, these are the things that it could be, and the priority on how its handled.

 1. A [TeamSpeak Server nickname](https://forum.teamspeak.com/threads/132595-How-to-register-a-Server-Nickname)
 2. A [SRV DNS entry](https://support.teamspeak.com/hc/en-us/articles/360002711418-Does-TeamSpeak-3-support-DNS-SRV-records-)
 3. TSDNS which is depricated
 4. Regular DNS name

Once a client has connected to the TeamSpeak Server it reads the `virtualserver_administrative_domain` variable which holds the domain name to search for the `.well-known` URLs. It also reads the `virtualserver_uuid` variable which holds the identifier for the virtual server. This way the client can now query `https://“*value of virtualserver_administrative_domain*”/.well-known/teamspeak/“*value of virtualserver_uuid*”` which returns the teamspeak well-known document described in [Discovery](###Discovery)

### TeamSpeak Text Chat

The first time the client asks the TeamSpeak Server for a login token to the Matrix chat. It can also ask for a login token when it has lost the access token for Matrix, or when it somehow expired.

Using chat.domain JSON entry in the TeamSpeak `.well-known` document retrieved when connecting to the TeamSpeak server, the client can now retrieve the Matrix client `.well-kown` URL and connect to that service using either the login token, or an existing access token.

### Files

The client will upload and download files from TeamSpeak for different use-cases. Most notably the channel files in TeamSpeak, and media in text chats. Other uses are for avatars and server icons.

In general the client will ask the server for an access token for a specific part. For example getting icons or avatars, or getting files of a channel. The client will then use the files.base_url JSON entry in the TeamSpeak `.well-known` document to locate the filetransfer server. It will then send the upload or download request to the filetransferserver. In the case of an upload, the filetransfer server will send back instructions on how to contact the actual S3 bucket that will do the storing. In the case of a download, the filetransfer server might send back the file directly, but in our reference implementation, the server sends back a http redirect to the S3 bucket.

Files in text chats behave differently. Files (images etc.) that users place in chat mesages are uploaded to that users personal space for the chat. To access them, a client will contact the auth service of the domain of the user that uploaded the file. That service will check if the requesting user/client and the user that uploaded the file are both in the specified chat. If so, the auth service will return a token which can be used on the filetransfer server on the domain of the uploading user to retrieve the files of that user in that chat.

### Short URLs

When the client want to create or modify a short url, it first request a identity token from the TeamSpeak Server. It will then do a request to the invites service with this token.
