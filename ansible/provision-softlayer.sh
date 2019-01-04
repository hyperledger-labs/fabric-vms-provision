#!/bin/bash

date

set -x
set -e

rm -rf ~/.ssh/known_hosts


PEER_COUNT=$@
export VARS_FILE=./vars/softlayer.yml

# autogenerate the role for creating the softlayer vms
python3 utils/softlayer/softlayer.py  -p $PEER_COUNT  >  roles/create/tasks/main.yml

ansible-playbook create.yml

set +x
while [[ ! -z "$(slcli vs list --columns id,hostname,primary_ip,backend_ip,datacenter,action,power_state | grep '^[0-9]' | awk '{print $2 "," $6}' | grep -v NULL)" ]]
do
	echo $(date) " - waiting for vms to provision"
	sleep 20
done

set -x
sleep 180

# autogenerate the ansible hosts file
python3 utils/softlayer/ans_hosts.py > hosts

# autogenerate a /etc/hosts file, to be included in each softlayer vm
python3 utils/softlayer/etc_hosts.py > roles/common/files/hosts


eval `ssh-agent`

ansible-playbook  --key-file "~/.ssh/fabric"  standardize-sl.yml
ansible-playbook  --key-file "~/.ssh/fabric"  common.yml
ansible-playbook  --key-file "~/.ssh/fabric"  --extra-vars "peer_count=\"$PEER_COUNT\""  build.yml


# autogenerate each playbook for packaging each fabric component, peerXorgY, ordererY, etc
python3 utils/package.py  -p $PEER_COUNT  -v $VARS_FILE

# autogenerate each playbook for starting (via systemd) each fabric component
python3 utils/start.py  -p $PEER_COUNT  -v $VARS_FILE


ssh-add ~/.ssh/fabric

# call each autogenerated ansible playbook for packaging each fabric component
./autogen_package.sh

# call each autogenerated ansible playbook for starting each fabric component
./autogen_start.sh


cat << 'EOF' > cancel.yml
---
- hosts: localhost
  gather_facts: False
  vars_files:
  - "{{ lookup('env','VARS_FILE') }}"
  tasks:
  - name: cancel vms
    sl_vm:
      state: absent
      tags: "{{ sl_tag }}"
EOF


date
