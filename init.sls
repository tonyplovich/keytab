{% from "keytab/map.jinja" import keytab with context %}

install_krb_tools:
  pkg.installed:
    - name: {{ keytab['krb_package'] }}

{% for princ in keytab['princs'] %}
# Send an event if we don't find the principle in the specified keytab file
provision_{{ princ['princ'] }}:
  princ.provisioned:
    - name: {{ princ['princ'] }}
    - keytab: {{ princ['keytab'] }}
    - require:
      - pkg: install_krb_tools
    - reload_pillar: true

add_{{ princ['princ'] }}:
  princ.managed:
    - name: {{ princ['princ'] }}
    - keytab: {{ princ['keytab'] }}
    - require:
      - princ: provision_{{ princ['princ'] }}
{% endfor %}
