## About

Most Hyperledger Fabric examples focus on provisioning it with `docker-compose`, which means if the machine on which docker-compose is running goes down, the whole fabric network goes with it. This example shows how to provision fabric on multiple virtual machines (vms), with each fabric component (each peer, orderer, fabric-ca) residing on its own virtual machine (vm).

**Note:**
- **This is not a production ready example.**
- **It will also incur the financial costs of running aws vms.**

The example leverages `ansible` and `aws ec2` to provision a network.

<p align="center">
  <img src="../orgs.svg">
</p>


## Quickstart

### Prerequisites:
- aws account
- aws api key
- an ssh key registered with aws
- vagrant
- virtualbox

### Initial steps

```
vagrant up
vagrant ssh
```

On the vagrant vm, create `~/.aws`, and populate `~/.aws/config, ~/.aws/credentials`. See aws (iam) for more details
```
# cat ~/.aws/config 
[default]
output = json
region = 

# cat ~/.aws/credentials
[default]
aws_access_key_id =
aws_secret_access_key =
```

On the vagrant vm, create an ssh public/private keypair (called `/home/vagrant/.ssh/fabric`) and copy the public key to aws. See `EC2 Dashboard -> Key Pairs` in aws web console.

### In general

Open a terminal
```
vagrant up
vagrant ssh
cd /vagrant/ansible


export AWS_ACCESS_KEY='REPLACE ME'
export AWS_SECRET_KEY='REPLACE ME'


# create password for vms
# http://docs.ansible.com/ansible/latest/reference_appendices/faq.html#how-do-i-generate-crypted-passwords-for-the-user-module
mkpasswd --method=sha-512
export AWSPASS='REPLACE ME'

eval `ssh-agent`

./provision-aws.sh <number of peers in org0> <number of peers in org1> ... <number of peers in org N>
# for example to create to create 3 orgs, org0 with 2 peers, org1 with 1 peer, and org2 with 3 peers
# ./provision-aws.sh 2 1 3

# once complete, there is a utility to list ssh connection details for each vm
python3 utils/aws/env_hosts.py
```

### Notes
It might be worthwhile adding 
```
export AWS_ACCESS_KEY='REPLACE ME'
export AWS_SECRET_KEY='REPLACE ME'
eval `ssh-agent` 
```
to the vagrant vm `/home/vagrant/.bashrc`

**This creates a lot of vms**

For example, with `./provision-aws.sh 2 1 3`, each org has a seperate vm for zookeeper, kafka, fabric-ca, orderer, cli, and a seperate vm for each peer. In the example `./provision-aws.sh 2 1 3` this equates to **21 vms** _[1(zk) + 1(kafka) + 1(fca) + 1(orderer) + 1(cli) + 2(peer)] + [1(zk) + 1(kafka) + 1(fca) + 1(orderer) + 1(cli) + 1(peer)] + [1(zk) + 1(kafka) + 1(fca) + 1(orderer) + 1(cli) + 3(peer)]_

|           |  org0 |  org1 |  org2 |  total |
| :-------- | ----: | ----: | ----: | -----: |
| zk        |     1 |     1 |     1 |        |
| kafka     |     1 |     1 |     1 |        |
| fabric-ca |     1 |     1 |     1 |        |
| orderer   |     1 |     1 |     1 |        |
| cli       |     1 |     1 |     1 |        |
| peer      |     2 |     1 |     3 |        |
|           |     7 |     6 |     8 | **21** |

## Next steps

Once the network is up, a channel can be added and chaincode installed. A simple key/value chaincode is included.

Open a new terminal and connect to `cli0`

```
vagrant ssh
# note: $CLI0 comes from cd /vagrant/ansible ; python3 utils/aws/env_hosts.py 
ssh -i ~/.ssh/fabric fabric@$CLI0
cd pkg-cli0

# this contains a set of scripts (which leverage the peer binary) to create, join, and update a channel as well as install and instantiate a chaincode on the channel
./01-create
./02-join
./03-update
./04-install
./05-instantiate
```

Open a new terminal and connect to `cli1`
```
vagrant ssh
ssh -i ~/.ssh/fabric fabric@$CLI1
cd pkg-cli1

# this contains a set of scripts (which leverage the peer binary) to fetch, join, and update a channel as well as install a chaincode on the channel
./01-fetch
./02-join
./03-update
./04-install
```

Open a new terminal and connect to `cli2`
```
vagrant ssh
ssh -i ~/.ssh/fabric fabric@$CLI2
cd pkg-cli2

# this contains a set of scripts (which leverage the peer binary) to fetch, join, and update a channel as well as install a chaincode on the channel
./01-fetch
./02-join
./03-update
./04-install
```

Now that the channel is created and chaincode instantiated, the `./invoke` and `./query` scripts can be used to append data to the ledger.


## use a client to invoke/query transactions

On the `CLI0` terminal/vm
```
cd ~/pkg-invoke/fabric-sdk-go

# first contact fabric-ca0 and create a user
./caRegisterAndEnrol  --help
./caRegisterAndEnrol  --config connection-profile-org0.yaml   --pass p0  --user u0

# use this new user to invoke (this will send a key/value [uuid/timestamp] for duration seconds)
./invoke  --help
./invoke  --config connection-profile-org0.yaml   --duration 20  --org org0  --peer peer1.org0.example.com  --user u0

# use this new user to query a transaction
./query  --help
./query  --config connection-profile-org0.yaml  --org org0  --peer peer0.org0.example.com  --user u0  --key <INSERT VALID KEY>
```

Likewise, on the `CLI1` terminal/vm
```
cd ~/pkg-invoke/fabric-sdk-go

# first contact fabric-ca1 and create a user
./caRegisterAndEnrol  --config connection-profile-org1.yaml   --pass p1  --user u1

# use this new user to invoke (this will send a key/value [uuid/timestamp] for duration seconds)
./invoke  --config connection-profile-org1.yaml   --duration 20  --org org1  --peer peer1.org1.example.com  --user u1

# use this new user to query a transaction
./query  --config connection-profile-org1.yaml  --org org1  --peer peer0.org1.example.com  --user u1  --key <INSERT VALID KEY>
```

Likewise, on the `CLI2` terminal/vm, ensuring to use the correct `connection-profileX.yaml`, `orgX`, and `peerY.orgX.example.com`
```
cd ~/pkg-invoke/fabric-sdk-go

# first contact fabric-ca2 and create a user
./caRegisterAndEnrol  --config connection-profile-org2.yaml   --pass p2  --user u2

# use this new user to invoke (this will send a key/value [uuid/timestamp] for duration seconds)
./invoke  --config connection-profile-org2.yaml   --duration 20  --org org2  --peer peer1.org2.example.com  --user u2

# use this new user to query a transaction
./query  --config connection-profile-org2.yaml  --org org2  --peer peer0.org2.example.com  --user u2  --key <INSERT VALID KEY>
```


### Notes
- connecting to the `peerYorgX` vm and running `docker logs -f <chaincode-container>` will show chaincode being executed.
- on the build vm `~/build/fabric/orgX` shows the files required for an org


## Tear down

Open a terminal
```
vargrant ssh
cd /vagrant/ansible
VARS_FILE=./vars/aws.yml ansible-playbook --key-file "~/.ssh/fabric"  cancel.yml
```
