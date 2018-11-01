'''fetch the primary ip addresses'''
import SoftLayer


def main():
    '''fetch the primary ip addresses'''
    client = SoftLayer.create_client_from_env()

    vsmgr = SoftLayer.VSManager(client)
    insts = vsmgr.list_instances()

    print('[all]')
    for inst in insts:
        print(inst['primaryIpAddress'])

    print('')

    for inst in insts:
        print('[' + inst['hostname'] + ']')
        print(inst['primaryIpAddress'])
        print('')


if __name__ == '__main__':
    main()
