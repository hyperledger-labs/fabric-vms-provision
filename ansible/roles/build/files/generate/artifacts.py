ARTIFACTS_INTRO = '''#!/bin/bash

set -x
set -e

if [ -z "$BDIR" ]; then
  echo "env var BDIR not set. This variable contains the directory where all build artifacts are placed"
  exit 1
fi

mkdir -p $BDIR/artifacts
cd $BDIR/artifacts
'''

ARTIFACTS_ORDERER = '''
cd $BDIR/artifacts
cp ${GOPATH}/src/github.com/hyperledger/fabric/sampleconfig/orderer.yaml .
'''

ARTIFACTS_CORE = '''
cd $BDIR/artifacts
cp ${GOPATH}/src/github.com/hyperledger/fabric/sampleconfig/core.yaml .
'''

ARTIFACTS_CRYPTO = '''
cd $BDIR/artifacts
cp $GOPATH/src/github.com/hyperledger/fabric/.build/bin/cryptogen .
cat << EOF > crypto-config.yaml
'''

ARTIFACTS_CRYPTO_ORG = '''
OrdererOrgs:
  - Name: Orderer
    Domain: example.com
    Template:
        Count: {org_count}
'''

ARTIFACTS_CRYPTO_PEERS = '''
PeerOrgs:
'''

ARTIFACTS_CRYPTO_PEER = '''
  - Name: Org{org_id}
    Domain: org{org_id}.example.com
    EnableNodeOUs: true
    Template:
      Count: {peer_count}
    Users:
      Count: 1
'''

ARTIFACTS_CRYPTO_FINISH = '''

EOF

./cryptogen generate --config=crypto-config.yaml

'''

ARTIFACTS_CONFIGTXGEN_INTRO = '''
cd $BDIR/artifacts
cp $GOPATH/src/github.com/hyperledger/fabric/.build/bin/configtxgen .
mkdir channel-artifacts

'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_INTRO = '''
cat << EOF > configtx.yaml
---'''


ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER = '''
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
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORGS = '''
    - &Org{org_id}
        Name: Org{org_id}MSP
        ID: Org{org_id}MSP
        MSPDir: crypto-config/peerOrganizations/org{org_id}.example.com/msp
        Policies:
            Readers:
                Type: Signature
                Rule: "OR('Org{org_id}MSP.admin', 'Org{org_id}MSP.peer', 'Org{org_id}MSP.client')"
            Writers:
                Type: Signature
                Rule: "OR('Org{org_id}MSP.admin', 'Org{org_id}MSP.client')"
            Admins:
                Type: Signature
                Rule: "OR('Org{org_id}MSP.admin')"

        AnchorPeers:
            - Host: peer0.org{org_id}.example.com
              Port: 7051

'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_CAPABILITIES = '''
Capabilities:
    Global: &ChannelCapabilities
        V1_1: true

    Orderer: &OrdererCapabilities
        V1_1: true

    Application: &ApplicationCapabilities
        V1_2: true
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_APPLICATION = '''
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
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_INTRO = '''
Orderer: &OrdererDefaults
    OrdererType: kafka
    Addresses:
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_ADDRESSES = '''        - orderer{org_id}.example.com:7050
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_KAFKA = '''
    Kafka:
        Brokers:
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_BROKERS = '''            - k{org_id}:9092
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_FINISH = '''
    BatchTimeout: 2s

    BatchSize:
        MaxMessageCount: 10
        AbsoluteMaxBytes: 98 MB
        PreferredMaxBytes: 512 KB

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
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_CHANNEL = '''
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
'''


ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_INTRO = '''
Profiles:
    MultiOrgOrdererGenesis:
        <<: *ChannelDefaults
        Orderer:
            <<: *OrdererDefaults
            Organizations:
                - *OrdererOrg
        Consortiums:
            SampleConsortium:
                Organizations:
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_CONSORTIUMS = '''                    - *Org{org_id}
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_CHANNEL = '''
    MultiOrgChannel:
        Consortium: SampleConsortium
        Application:
            <<: *ApplicationDefaults
            Organizations:
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_ORGANIZATIONS = '''                - *Org{org_id}
'''

ARTIFACTS_CONFIGTXGEN_CONFIGTX_FINISH = '''
EOF

'''

ARTIFACTS_CONFIGTXGEN_GENESIS = '''
./configtxgen -profile MultiOrgOrdererGenesis -channelID orderer-syschan -outputBlock ./channel-artifacts/genesis.block'''

ARTIFACTS_CONFIGTXGEN_CHANNEL = '''
./configtxgen  -profile MultiOrgChannel  -outputCreateChannelTx ./channel-artifacts/channel.tx  -channelID {channel_id}'''

ARTIFACTS_CONFIGTXGEN_ANCHOR = '''
./configtxgen  -profile MultiOrgChannel  -outputAnchorPeersUpdate ./channel-artifacts/Org{org_id}MSPanchors.tx  -asOrg Org{org_id}MSP  -channelID {channel_id}'''

ARTIFACTS_CONFIGTXGEN_FINISH = '''
'''
