import salt.exceptions

def provisioned(name, keytab='/etc/krb5.keytab'):
    '''
    Provision Kerberos principals on the KDC and places them into pillar

    name
        The principal, for example: host/somehost.example.com@EXAMPLE.COM
    keytab
        The location of the keytab file on the minion
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': '',
        'pchanges': {},
        }

    # Check if the principal already exists in the specified keytab
    current_state = __salt__['princ.find'](name, keytab)

    if current_state:
       ret['result'] = True
       ret['comment'] = '{0} already exists in {1}'.format(name, keytab)
       return ret

    # The state of the system does need to be changed. Check if we're running
    # in ``test=true`` mode.
    if __opts__['test'] == True:
       ret['comment'] = '"{0}" will be provisioned on the KDC'.format(name)
       ret['pchanges'] = {
           'old': '{0} missing from {1}'.format(name, keytab),
           'new': '{0} will be added to the KDC'.format(name),
       }

       # Return ``None`` when running with ``test=true``.
       ret['result'] = None

       return ret

    # Finally, make the actual change and return the result.
    princ_add_state = __salt__['princ.add'](name)
    if not princ_add_state:
      ret['comment'] = 'Adding the principal failed'
      ret['result'] = False

      return ret

    ret['comment'] = '"{0}" was created on the KDC"'.format(name)

    ret['changes'] = {
        'old': '{0} was missing from {1}'.format(name, keytab),
        'new': '{0} was added to the KDC'.format(name),
    }

    ret['result'] = True

    return ret

def managed(name, keytab='/etc/krb5.keytab'):
    '''
    Retrieves principals from pillar and merges them into the minion's keytab

    name
        The principal, for example: host/somehost.example.com@EXAMPLE.COM
    keytab
        The location of the keytab file on the minion
    '''

    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': '',
        'pchanges': {},
        }

    current_state = __salt__['princ.find'](name, keytab)

    if current_state:
       ret['result'] = True
       ret['comment'] = '{0} already exists in {1}'.format(name, keytab)
       return ret

    # The state of the system does need to be changed. Check if we're running
    # in ``test=true`` mode.
    if __opts__['test'] == True:
       ret['comment'] = '"{0}" will be merged into {1}'.format(name, keytab)
       ret['pchanges'] = {
           'old': '{0} missing from {1}'.format(name, keytab),
           'new': '{0} will be added to {1}'.format(name, keytab),
       }

       # Return ``None`` when running with ``test=true``.
       ret['result'] = None

       return ret

    princ_retrieve_state = __salt__['princ.retrieve'](name)
    if not princ_retrieve_state:
      ret['comment'] = 'Retrieving the principal failed'
      ret['result'] = False

      return ret
   
    princ_merge_state = __salt__['princ.merge'](name, keytab)
    if not princ_merge_state:
      ret['comment'] = 'merging the principal failed'
      ret['result'] = False

      return ret
 
    ret['comment'] = '"{0}" was added to "{1}"'.format(name, keytab)

    ret['changes'] = {
        'old': '{0} was missing from {1}'.format(name, keytab),
        'new': '{0} was added to {1}'.format(name, keytab),
    }

    ret['result'] = True

    return ret
