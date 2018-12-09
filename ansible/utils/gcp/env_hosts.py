'''fetch external ip of each vm, output to stdout with ssh'''
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

    names = []
    for instance in instances:
        ip = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
        name = instance['name'].upper()

        print('export ' + name + '=' + ip)

        names.append(name)

    print('')
    print('')

    for name in names:
        print('ssh  -i ~/.ssh/fabric  fabric@$' + name)


if __name__ == '__main__':
    main()
