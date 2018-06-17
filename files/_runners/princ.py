#!/usr/bin/python

import base64
import os
import re
import subprocess
import time

from salt.serializers import yaml

def add(princ,
        minion_id,
        tmp_keytab_dir='/root', 
        # CONFIGURE THESE!
        pillarstack_dir='/srv/pillar/keytabs/id/',
        keytab_prov_user='ktprov@EXAMPLE.COM', 
        keytab_prov_creds='/root/ktprov.keytab',
        kdc_type = 'mit',
        ad_dir = 'OU=Comps,OU=SomeOrg'):

  tmp_keytab = re.sub('[/@]', '_', princ) + '.keytab'
  fqdn = princ.split('/')[1].split('@')[0]
  # AD computer account name can only be 16 chars, select the last 14 of the principal
  ad_comp_name = "h-" + fqdn.split('.')[0][-14:]
  princ_type = princ.split('/')[0]
  krbDict = {'keytabs' : {tmp_keytab : ''}}
  id_yml = '{0}.yml'.format(minion_id)
  

  # Provision the principal
  if kdc_type == 'ad':
    subprocess.call('k5start {2} -f {3} -k /tmp/krbcc_keytab_state -- msktutil -b "{4}" -k {0}/{{1} -h {5} -s {6} --computer-name {7}'.format(tmp_keytab_dir, tmp_keytab, keytab_prov_user, keytab_prov_creds, ad_dir, fqdn, princ_type, ad_comp_name), shell=True)
  else:
    subprocess.call('echo -e "ank -randkey {4}\nktadd -k {0}/{1} {4}" | kadmin -p {2} -k -t {3}'.format(tmp_keytab_dir, tmp_keytab, keytab_prov_user, keytab_prov_creds, princ), shell=True)

  # Add the principal to the minion's pillar
  with open('{0}/{1}'.format(tmp_keytab_dir, tmp_keytab), 'rb') as krbFile:
    krbDict['keytabs'][tmp_keytab] = base64.b64encode(krbFile.read())
  fh = open('{0}/{1}'.format(pillarstack_dir, id_yml), 'wb')
  fh.write(yaml.serialize(krbDict))
  fh.close()
  
  # Clean up temp keytab file
  os.remove('{0}/{1}'.format(tmp_keytab_dir, tmp_keytab))
  
  # Wait for the minion to grab the keytab, then remove it from pillar
  time.sleep(20)
  os.remove('{0}/{1}'.format(pillarstack_dir, id_yml))
