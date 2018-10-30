'''fetch internal ec2 private ip for each vm'''

import boto3


def main():
    ec2 = boto3.resource('ec2')

    filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}]
    instances = ec2.instances.filter(Filters=filters)

    hosts_ips = []
    for instance in instances:
        has_fabric_tag = False
        for tags in instance.tags:
            if tags['Value'] == 'fabric':
                has_fabric_tag = True

        if has_fabric_tag == False:
            continue

        for tags in instance.tags:
            if tags['Key'] == 'FQDN':
                fqdn = tags['Value']

        for tags in instance.tags:
            if tags['Key'] == 'Host':
                host = tags['Value']

        ip = instance.public_ip_address
        host = host.replace('.', '')

        hosts_ips.append([host, ip])

    hosts_ips.sort()
    for hip in hosts_ips:
        print('export ' + hip[0].upper() + '=' + hip[1])

    print('')
    print('')

    for hip in hosts_ips:
        print('ssh  -i ~/.ssh/fabric  fabric@$' + hip[0].upper())


if __name__ == '__main__':
    main()
