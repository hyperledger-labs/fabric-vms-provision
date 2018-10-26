## Single peer/orderer

Prerequisites: add the following to `/etc/hosts`

```
127.0.0.1  orderer.example.com
127.0.0.1  peer0.org0.example.com
```


---


`./single.sh` will,
- build peer/orderer binaries
- create required artifacts (config files, msp certs, tls certs) for running peer and orderer (`~/fabric/artifacts`)
- create scripts to run both peer and orderer (`~/fabric/pkg-orderer` and `~/fabric/pkg-peer0org0`)
- create scripts to create, join, update, install, and instantiate a chaincode (`fabric/examples/chaincode/go/example02`) (`~/fabric/pkg-cli`)
- create scripts to query and invoke chaincode (`~/fabric/pkg-cli`)


---


## To run
```
vagrant up
vagrant ssh
```

This will create a vm with various dependencies (`docker`, `git`, `golang`, `libltdl-dev`) installed

## Build and create artifacts
```
cd /vagrant/single
./single.sh
```

When this completes, it will create `~/fabric`

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
code is in `./client` directory
```
cd ~/fabric/pkg-cli
./client  --config connection-profile.yaml  --action invoke  --key a
./client  --config connection-profile.yaml  --action query  --key b
```

`./client ...` can query the ledger, or transfer `5` from `a` to `b`.

### watch chaincode logs
```
# open a new terminal
vagrant ssh
docker ps -a
docker logs -f dev-peer0.org0.example.com-mycc-1.0
