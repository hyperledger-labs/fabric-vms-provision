#!/bin/bash

set -x
set -e

CURRDIR=$(pwd)

go get github.com/hyperledger/fabric     || true
go get github.com/hyperledger/fabric-ca  || true


cd ${GOPATH}/src/github.com/hyperledger/fabric
make  configtxgen
make  cryptogen
make  native


export BDIR=${HOME}/fabric

rm  -rf ${BDIR}
mkdir  -p ${BDIR}/artifacts


cd ${BDIR}/artifacts
cat << EOF > crypto-config.yaml
OrdererOrgs:
  - Name: Orderer
    Domain: example.com
    CA:
        Country: US
        Province: California
        Locality: San Francisco
    Specs:
      - Hostname: orderer

PeerOrgs:
  - Name: Org0
    Domain: org0.example.com
    EnableNodeOUs: true
    CA:
        Country: US
        Province: California
        Locality: San Francisco
    Template:
      Count: 1
    Users:
      Count: 1
EOF


cd ${BDIR}/artifacts
cat << EOF > configtx.yaml
---
Organizations:
    - &OrdererOrg
        Name: OrdererOrg
        ID: OrdererMSP
        MSPDir: crypto-config/ordererOrganizations/example.com/msp

        Policies:
            Readers:
                Type: Signature
                Rule: "OR('OrdererMSP.member')"
            Writers:
                Type: Signature
                Rule: "OR('OrdererMSP.member')"
            Admins:
                Type: Signature
                Rule: "OR('OrdererMSP.admin')"

    - &Org0
        Name: Org0MSP
        ID: Org0MSP
        MSPDir: crypto-config/peerOrganizations/org0.example.com/msp
        Policies:
            Readers:
                Type: Signature
                Rule: "OR('Org0MSP.admin', 'Org0MSP.peer', 'Org0MSP.client')"
            Writers:
                Type: Signature
                Rule: "OR('Org0MSP.admin', 'Org0MSP.client')"
            Admins:
                Type: Signature
                Rule: "OR('Org0MSP.admin')"

        AnchorPeers:
            - Host: peer0.org0.example.com
              Port: 7051

Capabilities:
    Global: &ChannelCapabilities
        V1_1: true

    Orderer: &OrdererCapabilities
        V1_1: true

    Application: &ApplicationCapabilities
        V1_2: true

Application: &ApplicationDefaults
    Organizations:

    Policies:
        Readers:
            Type: ImplicitMeta
            Rule: "ANY Readers"
        Writers:
            Type: ImplicitMeta
            Rule: "ANY Writers"
        Admins:
            Type: ImplicitMeta
            Rule: "MAJORITY Admins"

    Capabilities:
        <<: *ApplicationCapabilities

Orderer: &OrdererDefaults
    OrdererType: solo
    Addresses:
        - orderer.example.com:7050

    BatchTimeout: 2s

    BatchSize:
        MaxMessageCount: 10
        AbsoluteMaxBytes: 98 MB
        PreferredMaxBytes: 512 KB

    Kafka:
        Brokers:
            - kafka0:9092
            - kafka1:9092
            - kafka2:9092
            - kafka3:9092

    Organizations:

    Policies:
        Readers:
            Type: ImplicitMeta
            Rule: "ANY Readers"
        Writers:
            Type: ImplicitMeta
            Rule: "ANY Writers"
        Admins:
            Type: ImplicitMeta
            Rule: "MAJORITY Admins"
        BlockValidation:
            Type: ImplicitMeta
            Rule: "ANY Writers"

    Capabilities:
        <<: *OrdererCapabilities

Channel: &ChannelDefaults
    Policies:
        Readers:
            Type: ImplicitMeta
            Rule: "ANY Readers"
        Writers:
            Type: ImplicitMeta
            Rule: "ANY Writers"
        Admins:
            Type: ImplicitMeta
            Rule: "MAJORITY Admins"

    Capabilities:
        <<: *ChannelCapabilities

Profiles:
    OneOrgOrdererGenesis:
        <<: *ChannelDefaults
        Orderer:
            <<: *OrdererDefaults
            Organizations:
                - *OrdererOrg
        Consortiums:
            SampleConsortium:
                Organizations:
                    - *Org0

    OneOrgChannel:
        Consortium: SampleConsortium
        Application:
            <<: *ApplicationDefaults
            Organizations:
                - *Org0
EOF


cd ${BDIR}/artifacts
cp ${GOPATH}/src/github.com/hyperledger/fabric/sampleconfig/orderer.yaml .


cd ${BDIR}/artifacts
cp ${GOPATH}/src/github.com/hyperledger/fabric/sampleconfig/core.yaml .


## cryptogen
cd ${BDIR}/artifacts
${GOPATH}/src/github.com/hyperledger/fabric/.build/bin/cryptogen generate --config=./crypto-config.yaml


## configtxgen
cd ${BDIR}/artifacts
mkdir channel-artifacts
cp ${GOPATH}/src/github.com/hyperledger/fabric/.build/bin/configtxgen .
./configtxgen -profile OneOrgOrdererGenesis -channelID orderer-syschan -outputBlock ./channel-artifacts/genesis.block
./configtxgen -profile OneOrgChannel -outputCreateChannelTx ./channel-artifacts/channel.tx -channelID mychannel
./configtxgen -profile OneOrgChannel -outputAnchorPeersUpdate ./channel-artifacts/Org0MSPanchors.tx -channelID mychannel -asOrg Org0MSP


## orderer
mkdir ${BDIR}/pkg-orderer
cd ${BDIR}/pkg-orderer
cp ${GOPATH}/src/github.com/hyperledger/fabric/.build/bin/orderer .
cp ${BDIR}/artifacts/orderer.yaml .
cp -r ${BDIR}/artifacts/channel-artifacts .
cp -r ${BDIR}/artifacts/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp .
cp -r ${BDIR}/artifacts/crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/tls .

cd ${BDIR}/pkg-orderer
cat << EOF > run
#!/bin/bash

set -x

rm -rf ./hyperledger
mkdir  ./hyperledger

export FABRIC_CFG_PATH=.

export ORDERER_GENERAL_LOGLEVEL=debug
export ORDERER_GENERAL_LISTENADDRESS=0.0.0.0

export ORDERER_GENERAL_GENESISMETHOD=file
export ORDERER_GENERAL_GENESISFILE=./channel-artifacts/genesis.block

export ORDERER_GENERAL_LOCALMSPID=OrdererMSP
export ORDERER_GENERAL_LOCALMSPDIR=./msp

export ORDERER_GENERAL_TLS_ENABLED=true
export ORDERER_GENERAL_TLS_PRIVATEKEY=./tls/server.key
export ORDERER_GENERAL_TLS_CERTIFICATE=./tls/server.crt
export ORDERER_GENERAL_TLS_ROOTCAS=[./tls/ca.crt]

export ORDERER_FILELEDGER_LOCATION=./hyperledger/production/orderer

./orderer
EOF

chmod 755 run


## peer
mkdir ${BDIR}/pkg-peer0org0
cd ${BDIR}/pkg-peer0org0
cp ${GOPATH}/src/github.com/hyperledger/fabric/.build/bin/peer .
cp ${BDIR}/artifacts/core.yaml .
cp -r ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/msp .
cp -r ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls .

cd ${BDIR}/pkg-peer0org0
cat << EOF > run
#!/bin/bash

set -x

rm -rf ./hyperledger
mkdir  ./hyperledger

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=peer0.org0.example.com
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051
export CORE_PEER_LOCALMSPID=Org0MSP

export CORE_LOGGING_LEVEL=debug
export CORE_PEER_ENDORSER_ENABLED=true
export CORE_PEER_PROFILE_ENABLED=true

export CORE_PEER_GOSSIP_USELEADERELECTION=true
export CORE_PEER_GOSSIP_ORGLEADER=false
export CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0.org0.example.com:7051
export CORE_PEER_GOSSIP_BOOTSTRAP=peer0.org0.example.com:7051

export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_TLS_CERT_FILE=./tls/server.crt
export CORE_PEER_TLS_KEY_FILE=./tls/server.key
export CORE_PEER_TLS_ROOTCERT_FILE=./tls/ca.crt

export CORE_PEER_FILESYSTEMPATH=./hyperledger/production

./peer node start

EOF

chmod 755 run


## cli
mkdir ${BDIR}/pkg-cli
cd ${BDIR}/pkg-cli
cp ${GOPATH}/src/github.com/hyperledger/fabric/.build/bin/peer .
cp ${BDIR}/artifacts/core.yaml .
cp -r ${BDIR}/artifacts/crypto-config .
cp -r ${BDIR}/artifacts/channel-artifacts .


## cli create
cd ${BDIR}/pkg-cli
cat << EOF > 01-create
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer channel create  -o orderer.example.com:7050  -c mychannel  -f ./channel-artifacts/channel.tx  --tls true  --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

EOF

chmod 755 01-create


## cli join
cd ${BDIR}/pkg-cli
cat << EOF > 02-join
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer channel join  -b mychannel.block

EOF

chmod 755 02-join


## cli update
cd ${BDIR}/pkg-cli
cat << EOF > 03-update
#!/bin/bash
set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer channel update  -o orderer.example.com:7050  -c mychannel  -f ./channel-artifacts/Org0MSPanchors.tx  --tls true  --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

EOF

chmod 755 03-update


## cli install
cd ${BDIR}/pkg-cli
cat << EOF > 04-install
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer chaincode install  -n mycc  -v 1.0  -p github.com/hyperledger/fabric/examples/chaincode/go/example02/cmd

EOF

chmod 755 04-install


## cli instantiate
cd ${BDIR}/pkg-cli
cat << EOF > 05-instantiate
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer chaincode instantiate  -o orderer.example.com:7050  --tls true  --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem  -C mychannel  -n mycc  -v 1.0  -c '{"Args":["init","a","100","b","200"]}'  -P 'OR('\''Org0MSP.member'\'')'

EOF

chmod 755 05-instantiate


## query
cd ${BDIR}/pkg-cli
cat << 'EOF' > query
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer chaincode query  -C mychannel  -n mycc  -c "{\"Args\":[\"query\",\"$1\"]}"

EOF

chmod 755 query


## invoke
cd ${BDIR}/pkg-cli
cat << 'EOF' > invoke
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org0MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org0.example.com/users/Admin@org0.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org0.example.com/peers/peer0.org0.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org0.example.com:7051


./peer chaincode invoke  -o orderer.example.com:7050  --tls true  --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem  -C mychannel  -n mycc  -c "{\"Args\":[\"invoke\",\"a\",\"b\",\"10\"]}"

EOF

chmod 755 invoke


## fabric-ca
cd ${GOPATH}/src/github.com/hyperledger/fabric-ca
make fabric-ca-server

mkdir ${BDIR}/pkg-fabric-ca
cd ${BDIR}/pkg-fabric-ca
mkdir config
cp ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/ca/ca.org0.example.com-cert.pem  ./config
SK=$(ls ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/ca/ |grep _sk |head -n 1)
cp ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/ca/$SK  ./config
cp ${GOPATH}/src/github.com/hyperledger/fabric-ca/bin/fabric-ca-server  .
./fabric-ca-server init  -b admin:adminpw

cat << EOF > run
#!/bin/bash

set -x

./fabric-ca-server start  --ca.name ca.org0.example.com  --ca.certfile ./config/ca.org0.example.com-cert.pem  --ca.keyfile ./config/$SK  -b admin:adminpw

EOF

chmod 755 ./run


## client
mkdir -p ${GOPATH}/src/localhost/single-ca/caRegisterAndEnrol
cp ${CURRDIR}/fabric-sdk-go/caRegisterAndEnrol.go  ${GOPATH}/src/localhost/single-ca/caRegisterAndEnrol
cd ${GOPATH}/src/localhost/single-ca/caRegisterAndEnrol
go get
go build
cp caRegisterAndEnrol  ${BDIR}/pkg-cli

mkdir -p ${GOPATH}/src/localhost/single-ca/invokeOrQuery
cp ${CURRDIR}/fabric-sdk-go/invokeOrQuery.go  ${GOPATH}/src/localhost/single-ca/invokeOrQuery
cd ${GOPATH}/src/localhost/single-ca/invokeOrQuery
go get
go build
cp invokeOrQuery  ${BDIR}/pkg-cli


cd ${BDIR}/pkg-cli
cat << EOF > connection-profile.yaml
version: 1.0.0


certificateAuthorities:
  ca.org0.example.com:
    url: http://localhost:7054
    httpOptions:
      verify: false
    registrar:
      enrollId: admin
      enrollSecret: adminpw
    caName: ca.org0.example.com
    tlsCACerts:
      path: ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/ca/ca.org0.example.com-cert.pem


client:
  organization: org0

  BCCSP:
    security:
      enabled: true
      default:
        provider: "SW"
      hashAlgorithm: "SHA2"
      softVerify: true
      level: 256

  tlsCerts:
    systemCertPool: false

  credentialStore:
    path: "./kvs"
    cryptoStore:
      path: "./msp"


orderers:
  orderer.example.com:
    url: orderer.example.com:7050
    grpcOptions:
      ssl-target-name-override: orderer.example.com
      allow-insecure: false
    tlsCACerts:
      path: ${BDIR}/artifacts/crypto-config/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem


peers:
  peer0.org0.example.com:
    url: peer0.org0.example.com:7051
    grpcOptions:
      ssl-target-name-override: peer0.org0.example.com
      allow-insecure: false
    tlsCACerts:
      path: ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/tlsca/tlsca.org0.example.com-cert.pem


organizations:
  org0:
    mspid: Org0MSP
    cryptoPath: ${BDIR}/artifacts/crypto-config/peerOrganizations/org0.example.com/users/User1@org0.example.com/msp
    peers:
      - peer0.org0.example.com
    certificateAuthorities:
      - ca.org0.example.com

  ordererorg:
    mspID: "OrdererOrg"
    cryptoPath: ${BDIR}/artifacts/crypto-config/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem


channels:
  mychannel:
    peers:
      peer0.org0.example.com:
        eventSource: true


entityMatchers:
  orderer:
    - pattern: orderer.example.com
      urlSubstitutionExp: localhost:7050
      sslTargetOverrideUrlSubstitutionExp: orderer.example.com
      mappedHost: orderer.example.com
EOF
