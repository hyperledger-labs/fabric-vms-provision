## Single peer/orderer

Prerequisites: add the following to `/etc/hosts`

```
127.0.0.1  orderer.example.com
127.0.0.1  peer0.org0.example.com
127.0.0.1  ca.org0.example.com
```


---


`./single-ca.sh` will,
- build peer/orderer binaries
- create required artifacts (config files, msp certs, tls certs) for running peer and orderer (`~/fabric/artifacts`)
- create scripts to run both peer and orderer (`~/fabric/pkg-orderer` and `~/fabric/pkg-peer0org0`)
- create scripts to create, join, update, install, and instantiate a chaincode (`fabric/examples/chaincode/go/example02`) (`~/fabric/pkg-cli`)
- create scripts to query and invoke chaincode (`~/fabric/pkg-cli`)
- create programs which leverage `fabric-sdk-go` to create users and invoke transactions


---


## To run
```
vagrant up
vagrant ssh
```

This will create a vm with various dependencies (`docker`, `git`, `golang`, `libltdl-dev`) installed

## Build and create artifacts
```
cd /vagrant/single-ca
./single-ca.sh
```

When this completes, it will create `~/fabric`

### Start the fabric-ca
```
# open a new terminal
vagrant ssh
cd ~/fabric/pkg-fabric-ca
./run
```

### Start the orderer
```
# open a new terminal
vagrant ssh
cd ~/fabric/pkg-orderer
./run
```

### Start the peer
```
# open a new terminal
vagrant ssh
cd ~/fabric/pkg-peer0org0
./run
```

### Create channel, install chaincode
```
# open a new terminal
vagrant ssh
cd ~/fabric/pkg-cli
./01-create
./02-join
./03-update
./04-install
./05-instantiate

# wait a minute or two
```

### query and invoke
```
cd ~/fabric/pkg-cli
./query a
./query b

./invoke  # transfer 10 from a to b

./query a
./query b
```


### use client based on fabric-sdk-go
code is in `/vagrant/single-ca/fabric-sdk-go` directory. There are two files in here. The first `caRegisterAndEnrol.go` will connect to the `fabric-ca` and create a new user. The second `invokeOrQuery.go` will use the user created by the first program to either query or invoke a transaction.


```
# connect to fabric-ca and create a new user
cd ~/fabric/pkg-cli
./caRegisterAndEnrol  --config connection-profile.yaml  --pass password  --user username
```

```
# use user to query or invoke transaction
./invokeOrQuery  --config connection-profile.yaml  --action invoke  --key a  --user username
# or
./invokeOrQuery  --config connection-profile.yaml  --action query  --key a  --user username
```


### watch chaincode logs
```
# open a new terminal
vagrant ssh
docker ps -a
docker logs -f dev-peer0.org0.example.com-mycc-1.0
