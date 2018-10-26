'''generate scripts to set up fabric'''

import argparse
import os
import sys

from artifacts import *
from orgs import *
from invoke import *


def scripts_artifacts(dir_name, args):
    '''scripts to create contents of artifacts dir'''

    filename = dir_name + '/artifacts.sh' #TODO: path.join
    with open(filename, 'w') as afile:
        afile.write(ARTIFACTS_INTRO)


        # core
        afile.write(ARTIFACTS_CORE)


        # orderer
        afile.write(ARTIFACTS_ORDERER)


        # crypto
        afile.write(ARTIFACTS_CRYPTO)
        afile.write(ARTIFACTS_CRYPTO_ORG.format(org_count=args['org_count']))
        afile.write(ARTIFACTS_CRYPTO_PEERS)
        for i in range(0, args['org_count']):
            afile.write(ARTIFACTS_CRYPTO_PEER.format(org_id=i, peer_count=args['peer_count'][i]))
        afile.write(ARTIFACTS_CRYPTO_FINISH)


        # configtx.yml
        afile.write(ARTIFACTS_CONFIGTXGEN_INTRO)
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_INTRO)
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER)
        for org in range(0, args['org_count']):
            afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORGS.format(org_id=org))

        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_CAPABILITIES)
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_APPLICATION)
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_INTRO)
        for org in range(0, args['org_count']):
            afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_ADDRESSES.format(org_id=org))
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_KAFKA)
        for org in range(0, args['org_count']):
            afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_BROKERS.format(org_id=org))
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_ORGANIZATIONS_ORDERER_FINISH)
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_CHANNEL)
        
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_INTRO)
        for org in range(0, args['org_count']):
            afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_CONSORTIUMS.format(org_id=org))
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_CHANNEL)
        
        for org in range(0, args['org_count']):
            afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_PROFILES_ORGANIZATIONS.format(org_id=org))
        afile.write(ARTIFACTS_CONFIGTXGEN_CONFIGTX_FINISH)


        # configtxgen
        afile.write(ARTIFACTS_CONFIGTXGEN_GENESIS)
        afile.write(ARTIFACTS_CONFIGTXGEN_CHANNEL.format(channel_id=args['channel_id']))
        for i in range(0, args['org_count']):
            afile.write(ARTIFACTS_CONFIGTXGEN_ANCHOR.format(org_id=i, channel_id=args['channel_id']))
        afile.write(ARTIFACTS_CONFIGTXGEN_FINISH)

    os.chmod(filename, 0o755)


def scripts_dir(name):
    '''create a dir for scripts, backup existing dir if exists'''
    os.makedirs(name, exist_ok=True) #TODO: create backup and continue


def scripts_invoke(dir_name, args):
    ''' '''
    filename = dir_name + '/pkg-invoke' + '.sh'  #TODO: path.join
    with open(filename, 'w') as ifile:
        ifile.write(INVOKE_INTRO)
        for i in range(0, args['org_count']):
            ifile.write(CONNECTION_PROFILE_INTRO.format(org_id=i))
            ifile.write(CONNECTION_PROFILE_CA.format(org_id=i))
            ifile.write(CONNECTION_PROFILE_CLIENT.format(org_id=i))
            ifile.write(CONNECTION_PROFILE_ORDERERS.format(org_id=i))
            ifile.write(CONNECTION_PROFILE_PEERS)
            for j in range(0, args['peer_count'][i]):
                ifile.write(CONNECTION_PROFILE_PEERX.format(org_id=i, peer_id=j))
            ifile.write(CONNECTION_PROFILE_ORGANIZATIONS.format(org_id=i))
            for j in range(0, args['peer_count'][i]):
                ifile.write(CONNECTION_PROFILE_ORGANIZATIONS_PEERS.format(org_id=i, peer_id=j))
            ifile.write(CONNECTION_PROFILE_CHANNELS.format(org_id=i))
            for j in range(0, args['peer_count'][i]):
                ifile.write(CONNECTION_PROFILE_CHANNELS_PEERS.format(org_id=i, peer_id=j))
            ifile.write(CONNECTION_PROFILE_ENTITY.format(org_id=i))
            ifile.write(CONNECTION_PROFILE_FINISH)

    os.chmod(filename, 0o755)


def scripts_orgs(dir_name, org_id, args):
    '''scripts to create contents for orgs'''
    filename = dir_name + '/org' + str(org_id) + '.sh'  #TODO: path.join
    with open(filename, 'w') as sfile:
        # mkdir
        sfile.write(ORGS_INTRO)
        sfile.write(ORGS_MKDIR.format(org_id=org_id))
        sfile.write(ORGS_MKDIR_FABRIC_CA.format(org_id=org_id))
        sfile.write(ORGS_MKDIR_CLI.format(org_id=org_id))
        sfile.write(ORGS_MKDIR_INVOKE.format(org_id=org_id))
        sfile.write(ORGS_MKDIR_ORDERER.format(org_id=org_id))
        for i in range(0, args['peer_count'][org_id]):
            sfile.write(ORGS_MKDIR_PEER_ORG.format(org_id=org_id, peer_id=i))

        # fabricCA
        sfile.write(ORGS_CA.format(org_id=org_id))

        # orderer
        sfile.write(ORGS_ORDERER.format(org_id=org_id))

        # peers
        for i in range(0, args['peer_count'][org_id]):
            sfile.write(ORGS_PEER.format(org_id=org_id, peer_id=i, boot_id=((i + 1) % args['peer_count'][org_id])))

        #cli
        sfile.write(ORGS_CLI_INTRO.format(org_id=org_id))
        if org_id == 0:
            sfile.write(ORGS_CLI_CREATE.format(org_id=org_id))
        else:
            sfile.write(ORGS_CLI_FETCH.format(org_id=org_id))
        
        sfile.write(ORGS_CLI_JOIN_INTRO.format(org_id=org_id))
        for i in range(0, args['peer_count'][org_id]):
            sfile.write(ORGS_CLI_JOIN_PEER.format(org_id=org_id, peer_id=i))
        sfile.write(ORGS_CLI_JOIN_FINISH)

        sfile.write(ORGS_CLI_UPDATE.format(org_id=org_id))

        sfile.write(ORGS_CLI_INSTALL_INTRO.format(org_id=org_id))
        for i in range(0, args['peer_count'][org_id]):
            sfile.write(ORGS_CLI_INSTALL_PEER.format(org_id=org_id, peer_id=i))
        sfile.write(ORGS_CLI_INSTALL_FINISH)

        if org_id == 0:
            sfile.write(ORGS_CLI_INSTANTIATE.format(org_id=org_id))

        sfile.write(ORGS_CLI_INVOKE_INTRO.format(org_id=org_id))
        for i in range(0, args['peer_count'][org_id]):
            sfile.write(ORGS_CLI_INVOKE_PEER.format(org_id=org_id, peer_id=i))
        sfile.write(ORGS_CLI_INVOKE_FINISH)

        sfile.write(ORGS_CLI_QUERY_INTRO.format(org_id=org_id))
        for i in range(0, args['peer_count'][org_id]):
            sfile.write(ORGS_CLI_QUERY_PEER.format(org_id=org_id, peer_id=i))
        sfile.write(ORGS_CLI_QUERY_FINISH)

    os.chmod(filename, 0o755)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peer_count',
                        nargs='+',
                        type=int,
                        help='number of peers per org')
    parser.add_argument('-c', '--channel_id',
                        help='channel name')
    parsed_args = parser.parse_args()

    args = {}
    args['org_count'] = len(parsed_args.peer_count)
    args['peer_count'] = parsed_args.peer_count
    args['channel_id'] = parsed_args.channel_id

    dir_name = './scripts'
    scripts_dir(dir_name)
    scripts_artifacts(dir_name, args)

    for i in range(0, args['org_count']):
        scripts_orgs(dir_name, i, args)

    scripts_invoke(dir_name, args)


if __name__ == '__main__':
    main()
