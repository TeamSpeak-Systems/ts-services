# ts-services

The 'ts-services' repository is used for hosting the TeamSpeak 5 services as teamspeak_server, synapse, postgresql using docker compose.

    git clone https://github.com/TeamSpeak-Systems/ts-services
    cd ts-services

# Versioning and updates

We started of with a **beta-58rc1** tag and currently have **beta-58rc12** but the scheme will change to **v5.58.0-beta-rc13** soon.

In order to checkout a tag list them using 'git tag' command:

    git tag
    beta-58rc1
    beta-58rc10
    beta-58rc11
    beta-58rc12
    v5.58.0-beta-rc13
    ...
    
Note: You can get a list of tags here https://github.com/TeamSpeak-Systems/ts-services/tags (don't use the download feature, use git checkout as described below).

* **Note: Use only tags with no rc in it unless told otherwise by TeamSpeak support.**
* **Note: the **-beta** tag means that this software still might break your installation, kill your cat or invert your mouse. However, if you want to have a peek into our current development you are welcome. We'll help you with problems but it is save to assume that we are just entering production.**
* **Note: Avoid using *rc* releases, i.e. something like v5.58.0-beta-rc13, as this indicates we still update things and qualify the software software stack and are not yet sure if there is breakage on updates.**
* **Note: You MUST NOT skip minor version updates, so always go from v5.58.0-beta to v5.59.0-beta to v5.60.0-beta and NEVER go from v5.58.0-beta to v5.60.0-beta.**
* **Note: Always shutdown your stack with 'docker compose down' before updating to a different git checkout.**

At a later point we might introduce a program which helps with managing updates and also feature a feed or manifest which lists all the updates so you can easily see if anything needs to be done.

For the upcoming version scheme v5.57.0rc13-beta use:

    git checkout tags/v5.57.0-beta-rc13 -b v5.57.0-beta-rc13
    
Or for the **beta-** version scheme:

    git checkout tags/beta-57 -b beta-57
        
Once you have a checkout, follow the README.md coming with the release.
