import SoftLayer


def main():
    client = SoftLayer.create_client_from_env()

    vsmgr = SoftLayer.VSManager(client)
    insts = vsmgr.list_instances()

    hosts = {}
    for i in insts:
        ip = i['primaryIpAddress']
        host = i['hostname'].upper().replace('.', '').replace('-', '')

        print('export ' + host + '=' + ip)
    print('clear')
    print('')
    print('')

    for i in insts:
        host = i['hostname'].upper().replace('.', '').replace('-', '')

        print('ssh -i ~/.ssh/fabric fabric@$' + host)


if __name__ == '__main__':
    main()
