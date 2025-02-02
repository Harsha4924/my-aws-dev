import boto3
from awsconfig import  Myaws
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)


access_key = os.getenv('access_key')
secret_access_key = os.getenv('secret_access_key')




def lambda_handler():
    get_ec2_api = Myaws()
    connect = get_ec2_api.get_connection_to_aws('ec2', access_key, secret_access_key)
    response = connect.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    # print(response)
    all_instances = set()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            all_instances.add(instance['InstanceId'])
    # print(all_instances)

    all_snapshots = connect.describe_snapshots(OwnerIds=['self'])
    # print(all_snapshots)
    for snapshot in all_snapshots['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot['VolumeId']
        # print(snapshot_id, volume_id)
        if not volume_id:
            connect.delete_snapshot(SnapshotId=snapshot_id)
            print(f"Deleted snapshot id - {snapshot_id} as its not attached to any volumes")
        else:
            try:
                get_volume = connect.describe_volumes(VolumeIds = [volume_id])
                # print("get_volume", get_volume)
                if not get_volume['Volumes'][0]['Attachments']:
                    connect.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"deleted snapshot successfully snapshot_id - {snapshot_id} because the volume - {volume_id} is not connected to any of the instances")
            except connect.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    connect.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"Deleted EBS snapshot {snapshot_id} as its associated volume was not found.")



lambda_handler()


def delete_volume():
    my_connect = Myaws()
    my_ec2_connect = my_connect.get_connection_to_aws('ec2', access_key, secret_access_key)
    # all_instances = my_ec2_connect.describe_instances()
    my_volumes = my_ec2_connect.describe_volumes()
    print(my_volumes)
    # if not my_vol
    for volumes in my_volumes['Volumes']:
        volume_id = volumes['VolumeId']
        # print(volume_id)
        if not volumes['Attachments'] and volumes['State'] == 'available':
            my_ec2_connect.delete_volume(VolumeId=volume_id)
            print(f'deleted volume id successfully because volume id - {volume_id} is not connected to any instances')
    

delete_volume()