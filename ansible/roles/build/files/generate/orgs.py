ORGS_INTRO = '''#!/bin/bash

set -x
set -e

if [ -z "$BDIR" ]; then
  echo "env var BDIR not set. This variable contains the directory where all build artifacts are placed"
  exit 1
fi


'''

ORGS_MKDIR = '''
#
# mkdir org{org_id}
#
mkdir $BDIR/org{org_id}
'''

ORGS_MKDIR_FABRIC_CA = '''mkdir $BDIR/org{org_id}/pkg-fabric-ca{org_id}
'''

ORGS_MKDIR_CLI = '''mkdir $BDIR/org{org_id}/pkg-cli{org_id}
'''

ORGS_MKDIR_INVOKE = '''mkdir $BDIR/org{org_id}/pkg-invoke{org_id}
'''

ORGS_MKDIR_ORDERER = '''mkdir $BDIR/org{org_id}/pkg-orderer{org_id}
'''

ORGS_MKDIR_PEER_ORG = '''mkdir $BDIR/org{org_id}/pkg-peer{peer_id}org{org_id}
'''

ORGS_CA = '''
#
# org{org_id} ca
#
mkdir -p $BDIR/org{org_id}/pkg-fabric-ca{org_id}
cd $BDIR/org{org_id}/pkg-fabric-ca{org_id}
mkdir config
cp $BDIR/artifacts/crypto-config/peerOrganizations/org{org_id}.example.com/ca/ca.org{org_id}.example.com-cert.pem ./config
export SK=$(ls $BDIR/artifacts/crypto-config/peerOrganizations/org{org_id}.example.com/ca/ |grep "_sk")
cp $BDIR/artifacts/crypto-config/peerOrganizations/org{org_id}.example.com/ca/$SK ./config

cp $GOPATH/src/github.com/hyperledger/fabric-ca/bin/fabric-ca-server .

cd $BDIR/org{org_id}/pkg-fabric-ca{org_id}

cat << 'EOF' > run
#!/bin/bash

set -x

export FABRIC_CA_SERVER_CA_NAME=ca.org{org_id}.example.com
SK=$(ls config/ |grep _sk |head -n 1)

./fabric-ca-server  start  -b admin:adminpw  --ca.name ca.org{org_id}.example.com  --ca.certfile ./config/ca.org{org_id}.example.com-cert.pem  --ca.keyfile ./config/$SK

EOF

chmod 755 run

'''

ORGS_ORDERER = '''
#
# org{org_id} orderer
#
cd $BDIR/org{org_id}/pkg-orderer{org_id}
cp $GOPATH/src/github.com/hyperledger/fabric/.build/bin/orderer .
cp $BDIR/artifacts/orderer.yaml .
cp -r $BDIR/artifacts/channel-artifacts .
cp -r $BDIR/artifacts/crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/msp .
cp -r $BDIR/artifacts/crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/tls .

cd $BDIR/org{org_id}/pkg-orderer{org_id}
cat << 'EOF' > run
#!/bin/bash

set -x

if [ "$1" == "clean" ] ; then
  rm -rf ./hyperledger
  mkdir  ./hyperledger
fi

export FABRIC_CFG_PATH=.

export ORDERER_GENERAL_LOGLEVEL=critical
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

'''

ORGS_PEER = '''
#
# org{org_id} peer{peer_id}
#
mkdir -p $BDIR/org{org_id}/pkg-peer{peer_id}org{org_id}
cd $BDIR/org{org_id}/pkg-peer{peer_id}org{org_id}
cp $GOPATH/src/github.com/hyperledger/fabric/.build/bin/peer .
cp $BDIR/artifacts/core.yaml .
cp -r $BDIR/artifacts/crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer{peer_id}.org{org_id}.example.com/msp .
cp -r $BDIR/artifacts/crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer{peer_id}.org{org_id}.example.com/tls .

cd $BDIR/org{org_id}/pkg-peer{peer_id}org{org_id}
cat << 'EOF' > run
#!/bin/bash

set -x

if [ "$1" == "clean" ] ; then
  rm -rf ./hyperledger
  mkdir  ./hyperledger
fi

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=peer{peer_id}.org{org_id}.example.com
export CORE_PEER_ADDRESS=peer{peer_id}.org{org_id}.example.com:7051
export CORE_PEER_LOCALMSPID=Org{org_id}MSP

export CORE_LOGGING_LEVEL=critical
export CORE_PEER_ENDORSER_ENABLED=true
export CORE_PEER_PROFILE_ENABLED=true

export CORE_PEER_GOSSIP_USELEADERELECTION=true
export CORE_PEER_GOSSIP_ORGLEADER=false
export CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer{peer_id}.org{org_id}.example.com:7051
export CORE_PEER_GOSSIP_BOOTSTRAP=peer{boot_id}.org{org_id}.example.com:7051

export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_TLS_CERT_FILE=./tls/server.crt
export CORE_PEER_TLS_KEY_FILE=./tls/server.key
export CORE_PEER_TLS_ROOTCERT_FILE=./tls/ca.crt

export CORE_PEER_FILESYSTEMPATH=./hyperledger/production

./peer node start

EOF

chmod 755 run

'''

ORGS_CLI_INTRO = '''
#
# org{org_id} cli
#
mkdir -p $BDIR/org{org_id}/pkg-cli{org_id}
cd $BDIR/org{org_id}/pkg-cli{org_id}
cp $GOPATH/src/github.com/hyperledger/fabric/.build/bin/peer .
cp $BDIR/artifacts/core.yaml .
cp -r $BDIR/artifacts/crypto-config .
cp -r $BDIR/artifacts/channel-artifacts .


'''

ORGS_CLI_CREATE = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > 01-create
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer0.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org{org_id}.example.com:7051


./peer channel create -t 20s -o orderer{org_id}.example.com:7050 -c mychannel -f ./channel-artifacts/channel.tx --tls true --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

EOF

chmod 755 01-create

'''

ORGS_CLI_FETCH = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > 01-fetch
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer0.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org{org_id}.example.com:7051


./peer channel fetch 0 mychannel.block  -o orderer{org_id}.example.com:7050 -c mychannel --tls --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

EOF

chmod 755 01-fetch

'''


ORGS_CLI_JOIN_INTRO = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > 02-join
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true
'''

ORGS_CLI_JOIN_PEER = '''
export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer{peer_id}.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer{peer_id}.org{org_id}.example.com:7051


./peer channel join -b mychannel.block
'''

ORGS_CLI_JOIN_FINISH = '''
EOF

chmod 755 02-join


'''

ORGS_CLI_UPDATE = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > 03-update
#!/bin/bash
set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer0.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org{org_id}.example.com:7051


./peer channel update -o orderer{org_id}.example.com:7050 -c mychannel -f ./channel-artifacts/Org{org_id}MSPanchors.tx --tls true --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

EOF

chmod 755 03-update

'''

ORGS_CLI_INSTALL_INTRO = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > 04-install
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true
'''

ORGS_CLI_INSTALL_PEER = '''
export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer{peer_id}.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer{peer_id}.org{org_id}.example.com:7051

./peer chaincode install -n mycc -v 1.0 -p localhost/chaincodes/go/kv


'''

ORGS_CLI_INSTALL_FINISH = '''
EOF

chmod 755 04-install
'''

ORGS_CLI_INSTANTIATE = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > 05-instantiate
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true

export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer0.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer0.org{org_id}.example.com:7051


./peer chaincode instantiate -o orderer{org_id}.example.com:7050 --tls true --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc -v 1.0 -c '{{"Args":["init","a","100"]}}'  -P "OR ('Org0MSP.member','Org1MSP.member','Org2MSP.member')"

EOF

chmod 755 05-instantiate
'''

ORGS_CLI_INVOKE_INTRO = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > invoke
#!/bin/bash

set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=debug
export CORE_PEER_TLS_ENABLED=true
'''

ORGS_CLI_INVOKE_PEER = '''
export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer{peer_id}.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer{peer_id}.org{org_id}.example.com:7051


./peer chaincode invoke -o orderer{org_id}.example.com:7050 --tls true --cafile ./crypto-config/ordererOrganizations/example.com/orderers/orderer{org_id}.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc -c '{{"Args":["invoke","peer{peer_id}org{org_id}","---> peer{peer_id}org{org_id}"]}}'

'''

ORGS_CLI_INVOKE_FINISH = '''
EOF

chmod 755 invoke
'''

ORGS_CLI_QUERY_INTRO = '''
cd $BDIR/org{org_id}/pkg-cli{org_id}
cat << EOF > query
#!/bin/bash

#set -x

export FABRIC_CFG_PATH=.

export CORE_PEER_ID=cli
export CORE_LOGGING_LEVEL=critical
export CORE_PEER_TLS_ENABLED=true
'''

ORGS_CLI_QUERY_PEER = '''
export CORE_PEER_LOCALMSPID=Org{org_id}MSP
export CORE_PEER_MSPCONFIGPATH=./crypto-config/peerOrganizations/org{org_id}.example.com/users/Admin@org{org_id}.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=./crypto-config/peerOrganizations/org{org_id}.example.com/peers/peer{peer_id}.org{org_id}.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=peer{peer_id}.org{org_id}.example.com:7051


./peer chaincode query -C mychannel -n mycc -c '{{"Args":["query","peer{peer_id}org{org_id}"]}}'
'''

ORGS_CLI_QUERY_FINISH = '''
EOF

chmod 755 query
'''
