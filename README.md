# ts-services

The 'ts-services' repository is used for hosting the TeamSpeak 5 services as teamspeak_server, synapse, postgresql using docker compose.

    git clone https://github.com/TeamSpeak-Systems/ts-services
    cd ts-services
    
Use a tag as *beta-58* as this *master branch* is only here to guide you to a properly tagged release.

    git tag
    beta-57
    beta-57-rc1
    beta-57-rc2
    beta-57-rc3
    beta-58rc1
    beta-58rc2
    beta-58rc3
    beta-58rc4
    beta-58rc5
    beta-58rc6
    beta-58rc7
    ...
    
Note: You can get a list of tags here https://github.com/TeamSpeak-Systems/ts-services/tags (don't use the download feature, use git checkout as described below).

**Note: In general avoid using *rc* releases, i.e. something like beta-58rc7, as this indicates we still update things which might break your installation.**

And then use one of these with:

    git checkout tags/beta-57 -b beta-57
    
**Note: Also don't skip updates: if you have beta-55 and there is already a beta-57, you should update to beta-56 and *then* to beta-57.**
    
Once you have a checkout, follow the README.md coming with the release.
