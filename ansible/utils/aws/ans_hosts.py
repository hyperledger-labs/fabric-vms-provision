'''fetch ec2 public ips'''
import boto3

ec2 = boto3.resource('ec2')

def main():
    filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']}]
    instances = ec2.instances.filter(Filters=filters)

    instance_ips = []
    for instance in instances:
        has_fabric_tag = False
        for tags in instance.tags:
            if tags['Value'] == 'fabric':
                has_fabric_tag = True

        if has_fabric_tag == False:
            continue

        for tags in instance.tags:
            if tags['Key'] == 'Host':
                instance_host = tags['Value']

        ip = instance.public_ip_address
        print('[' + instance_host +']')
        print(ip)
        print()
    
        instance_ips.append(instance.public_ip_address)

    print('[all]')
    for ip in instance_ips:
        print(ip)


if __name__ == '__main__':
    main()
