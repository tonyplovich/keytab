import os
import re
import subprocess
import time

def find(name, keytab='/etc/krb5.keytab'):
    '''
    See if a certian Kerberos principal exists in a specified keytab file

    name
        The principal, for example: host/somehost.example.com@EXAMPLE.COM
    keytab
        The location of the keytab file on the minion (default: /etc/krb5.keytab)
    '''

    # See if keytab file exists
    if not os.path.isfile(keytab):
      ret = False
      return ret

    # List principals within the specified keytab file
    princs = subprocess.check_output(['k5srvutil', 'list', '-f', keytab])    
    # Search the results for the specified principal
    m = re.search(name, princs)

    if m:
      ret = True
    else:
      ret = False

    return ret

def add(name):
    '''
    Fire an event to the salt master telling it to provision a new principal, then wait for the master to tell us it's ready.

    name
        The principal, for example: host/somehost.example.com@EXAMPLE.COM
    '''
    
    ret = True

    __salt__['event.send']('princ/add', {
        'princ': name
    })

    time.sleep(5)
    return ret

def retrieve(name, tmp_keytab_dir='/root'):
    '''
    Pull a base64 encoded keytab from pillar and place it on the minion

    name
        The principal, for example: host/somehost.example.com@EXAMPLE.COM
    '''
    
    ret = False
    name_file = re.sub('[/@]', '_', name) + '.keytab'

    # Does our base64 encoded keytab exist in pillar?
    if __salt__['pillar.get']('keytabs:{0}'.format(name_file), ""):
      # Decode it into our temp keytab directory
      fh = open('{0}/{1}'.format(tmp_keytab_dir, name_file), 'wb')
      fh.write(__salt__['pillar.get']('keytabs:{0}'.format(name_file), "").decode('base64'))
      fh.close()
      os.chmod('{0}/{1}'.format(tmp_keytab_dir, name_file), 0400)
      ret = True

    return ret

def merge(name, keytab='/etc/krb5.keytab', tmp_keytab_dir='/root'):
    '''
    Merge a temp keytab containing with an existing one

    name
        The principal, for example: host/somehost.example.com@EXAMPLE.COM
    keytab
        The location of the keytab file on the minion to merge the new principal into (default: /etc/krb5.keytab)
    '''
    
    tmp_keytab = re.sub('[/@]', '_', name) + '.keytab'

    r = subprocess.call('echo -e "rkt {0}/{1}\nrkt {2}\nwkt {2}" | ktutil'.format(tmp_keytab_dir, tmp_keytab, keytab), shell=True) 
    os.remove('{0}/{1}'.format(tmp_keytab_dir, tmp_keytab))
    
    if r == 0:
      ret = True
    else:
      ret = False

    return ret
