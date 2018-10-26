#!/bin/bash

source ~/.bashrc

set -x

export GOROOT=${HOME}/local/go
export GOPATH=${HOME}/golang
export PATH=${GOROOT}/bin:${GOPATH}/bin:${HOME}/local/bin:${PATH}

cd

go get github.com/hyperledger/fabric-ca
cd ${GOPATH}/src/github.com/hyperledger/fabric-ca
make fabric-ca-server

cd

go get github.com/hyperledger/fabric  || true
cd ${GOPATH}/src/github.com/hyperledger/fabric
make cryptogen configtxgen
make native

cd

cd ${GOPATH}/src/localhost/fabric-sdk-go/caRegisterAndEnrol
go get
go build

cd

cd ${GOPATH}/src/localhost/fabric-sdk-go/invoke
go get
go build

cd

cd ${GOPATH}/src/localhost/fabric-sdk-go/query
go get
go build

cd

cd ${HOME}/build/generate

mkdir -p ${HOME}/build/fabric
export BDIR=${HOME}/build/fabric

python3 gen.py -p {{ peer_count }} -c mychannel

cd ./scripts
./artifacts.sh
./org0.sh
./org1.sh
./org2.sh
./pkg-invoke.sh
