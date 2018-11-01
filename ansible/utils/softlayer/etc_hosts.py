'''fetch internal softlayer private ip for each vm'''
import SoftLayer


def main():
    client = SoftLayer.create_client_from_env()

    vsmgr = SoftLayer.VSManager(client)
    insts = vsmgr.list_instances()

    hosts = {}
    for inst in insts:
        pbip = inst['primaryBackendIpAddress'].ljust(24)
        fqdn = inst['fullyQualifiedDomainName'].rjust(32)
        host = inst['hostname'].rjust(16)

        print('      ' + pbip + ' ' + fqdn + ' ' + host)


if __name__ == '__main__':
    main()
