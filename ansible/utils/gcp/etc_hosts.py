'''fetch internal ips of vms, output to stdout in /etc/hosts format'''
import googleapiclient.discovery
import os


def instance_list(compute, project, zone):
    instance = compute.instances().list(project=project, zone=zone).execute()
    return instance['items'] if 'items' in instance else None


def main():
    project_id = os.environ['GOOGLE_PROJECT_ID']
    zone = os.environ['GOOGLE_COMPUTE_ZONE']

    compute = googleapiclient.discovery.build('compute', 'v1')
    instances = instance_list(compute, project_id, zone)

    for instance in instances:
        tag = instance['tags']['items'][0]
        fqdn = tag.replace('-', '.')
        
        ip = instance['networkInterfaces'][0]['networkIP']

        etc_hosts_line = ip.ljust(24) + ' ' + fqdn.rjust(32)

        print(etc_hosts_line)


if __name__ == '__main__':
    main()
