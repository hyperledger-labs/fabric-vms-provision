'''fetch internal ec2 private ip for each vm'''

import boto3


def main():
    ec2 = boto3.resource('ec2')

    filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}]
    instances = ec2.instances.filter(Filters=filters)

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

        ip = instance.private_ip_address
        etc_hosts_line = ip.ljust(24) + ' ' + fqdn.rjust(32) + " " + host.rjust(16)

        print(etc_hosts_line)


if __name__ == '__main__':
    main()
