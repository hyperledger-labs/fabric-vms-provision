INVOKE_INTRO = '''#!/bin/bash

set -x
set -e

if [ -z "$BDIR" ]; then
  echo "env var BDIR not set. This variable contains the directory where all build artifacts are placed"
  exit 1
fi

mkdir -p $BDIR/pkg-invoke/fabric-sdk-go
cd $BDIR/pkg-invoke/fabric-sdk-go

cp $GOPATH/src/localhost/fabric-sdk-go/caRegisterAndEnrol/caRegisterAndEnrol  .
cp $GOPATH/src/localhost/fabric-sdk-go/caRegisterAndEnrol/caRegisterAndEnrol.go  .

cp $GOPATH/src/localhost/fabric-sdk-go/invoke/invoke  .
cp $GOPATH/src/localhost/fabric-sdk-go/invoke/invoke.go  .

cp $GOPATH/src/localhost/fabric-sdk-go/query/query  .
cp $GOPATH/src/localhost/fabric-sdk-go/query/query.go  .

cp -r $BDIR/artifacts/crypto-config .
'''

CONNECTION_PROFILE_INTRO = '''
cat << EOF > connection-profile-org{org_id}.yaml
version: 1.0.0

'''

CONNECTION_PROFILE_CA = '''
certificateAuthorities:
  ca.org{org_id}.example.com:
    url: http://fabric-ca{org_id}.example.com:7054
    httpOptions:
      verify: false
    registrar:
      enrollId: admin
      enrollSecret: adminpw
    caName: ca.org{org_id}.example.com
    tlsCACerts:
      path: /home/fabric/pkg-invoke/fabric-sdk-go/crypto-config/peerOrganizations/org{org_id}.example.com/ca/ca.org{org_id}.example.com-cert.pem

'''

CONNECTION_PROFILE_CLIENT = '''
client:
  organization: org{org_id}

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

'''

CONNECTION_PROFILE_ORDERERS = '''
orderers:
  orderer{org_id}.example.com:
    url: orderer{org_id}.example.com:7050
    grpcOptions:
      ssl-target-name-override: orderer{org_id}.example.com
      allow-insecure: false
    tlsCACerts:
      path: /home/fabric/pkg-invoke/fabric-sdk-go/crypto-config/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem

'''

CONNECTION_PROFILE_PEERS = '''
peers:'''

CONNECTION_PROFILE_PEERX = '''
  peer{peer_id}.org{org_id}.example.com:
    url: peer{peer_id}.org{org_id}.example.com:7051
    grpcOptions:
      ssl-target-name-override: peer{peer_id}.org{org_id}.example.com
      allow-insecure: false
    tlsCACerts:
      path: /home/fabric/pkg-invoke/fabric-sdk-go/crypto-config/peerOrganizations/org{org_id}.example.com/tlsca/tlsca.org{org_id}.example.com-cert.pem
'''

CONNECTION_PROFILE_ORGANIZATIONS = '''
organizations:
  ordererorg:
    mspID: "OrdererOrg"
    cryptoPath: /home/fabric/pkg-invoke/fabric-sdk-go/crypto-config/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem

  org{org_id}:
    mspid: Org{org_id}MSP
    cryptoPath: /home/fabric/pkg-invoke/fabric-sdk-go/crypto-config/peerOrganizations/org{org_id}.example.com/users/User1@org{org_id}.example.com/msp
    certificateAuthorities:
      - ca.org{org_id}.example.com
    peers:'''

CONNECTION_PROFILE_ORGANIZATIONS_PEERS = '''
      - peer{peer_id}.org{org_id}.example.com'''

CONNECTION_PROFILE_CHANNELS = '''
channels:
  mychannel:
    peers:'''

CONNECTION_PROFILE_CHANNELS_PEERS = '''
      peer{peer_id}.org{org_id}.example.com:
        eventSource: true'''

CONNECTION_PROFILE_ENTITY = '''
entityMatchers:
  orderer{org_id}:
    - pattern: orderer{org_id}.example.com
      urlSubstitutionExp: orderer{org_id}.example.com:7050
      sslTargetOverrideUrlSubstitutionExp: orderer{org_id}.example.com
      mappedHost: orderer{org_id}.example.com
'''

CONNECTION_PROFILE_FINISH = '''
EOF
'''
