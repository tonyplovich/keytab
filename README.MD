# keytab
Salt forumula to provision Kerberos principals and keytab files securely.

## Usage
Configure these on your Salt master:
1. Add the following reactor:

>      reactor:
>       - 'princ/add':
>         - /srv/PATH/TO/YOUR/keytab/files/react/princ_add.sls

2. Add a PillarStack ext_pillar to hold the keytabs (do NOT make this available via the Salt fileserver):

>      ext_pillar:
>       - stack: /srv/pillar/keytabs/core.cfg

4. Create the PillarStack keytab directory and drop the cfg file in:

mkdir -p /srv/pillar/keytabs/id

/srv/pillar/keytabs/core.cfg:

>    id/{{ __grains__['id'] }}.yml

4. Add the contents of the keytab/files/_{runners,states,modules} directories to corresponding _runners, _states, or _modules directory within the root of one of your configured file_roots. (There are a few ways to tell Salt how to find custom extensions, check your master config).

5. Configure the "CONFIGURE THESE!" items in _runners/princ.py.

6. Create a keytab file on the salt master with the credentials of the user that will be used to provision principals:
````
ktutil
addent -password -p YOURUSER@EXAMPLE.COM -k 4 -e arcfour-hmac-md5
addent -password -p YOURUSER@EXAMPLE.COM -k 4 -e aes128-cts-hmac-sha1-96
addent -password -p YOURUSER@EXAMPLE.COM -k 4 -e aes256-cts-hmac-sha1-96 
wkt /root/ktprov.keytab
````

7. On your master, make sure kadmin (or msktutil / k5start for AD) is installed and /etc/krb5.conf is configured.

## Pillar Example
>     keytab:
>      princs:
>        - princ: host/SOME.HOST.HERE@EXAMPLE.COM
>          keytab: /etc/krb5.keytab
## How It Works:
1. The custom state checks if the specified principal exists in the specified keytab.
  If not, fire an event to the master and sleep for 5 seconds.
2. Master catches the event in a reactor which fires a runner.
3. Runner executes the mskutil / kadmin commands to provision a new principal.  Then it base64 encodes the keytab and puts it into pillar
4. Minion wakes up, refreshes its pillar, base64 decodes the keytab, and merges it with the final keytab.

## Stuff To Add:
* Write code for service principals that might exist on multiple hosts:
* Write code to verify if a specific minion is configured to have the principal it claims to have in the state.event.
* Figure out a way to see if principals are in sync with KDC.  Right now we just see if they exist.
