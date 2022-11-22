## Migration
It is possible to migrate existing TeamSpeak 3 databases to TeamSpeak 5. This
can be done during the Installation phase

### sqlite
To migrate a sqlite teamspeak database, copy the ts3server.sqlitedb file to the
same folder as the docker-compose.yaml file and run setup as

```sh
docker-compose run --rm setup --domain=example.com --email=admin@example.com --migrate_driver=sqlite3
```

### mariadb
To migrate a mariadb/mysql teamspeak database use --migrate_driver="mysql" and 
--migrate_connectionstring="username:password@protocol(address)/dbname?param=value".
See https://github.com/go-sql-driver/mysql#readme on how to format the connection
string exactly. For example

```sh
docker-compose run --rm setup --domain=example.com --email=admin@example.com --migrate_driver=mysql --migrate_connectionstring="tsuser:tspassword@tcp(localhost:3306)/teamspeak"
```

### postgres
To migrate a postgres teamspeak database use --migrate_driver="postgres" and 
--migrate_connectionstring="[postgres connection string]".
See https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING on how to format the connection
string exactly. For example

```sh
docker-compose run --rm setup --domain=example.com --email=admin@example.com --migrate_driver=postgres --migrate_connectionstring="postgresql://tsuser:tspassword@localhost/teamsspeak"
```

### Migration of avatars, icons and files
As additional step for migration, importing avatars, icon and files is available as an option. Please see the ts3-file-importer subdirectory for further information.
