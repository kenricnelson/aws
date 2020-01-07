#!/usr/bin/env python
# coding: utf-8

# ## AWS AMI
# 
# 1. Import boto3 package 
# 2. Read *blockchain-nodes* profile found in ~.aws/credentials
# 3. Create a EC2 session for instance creation
# 4. Read aws details for name, node, datavoluem size and instance type

# In[ ]:


import boto3
import os
import pandas as pd


# ## Helper functions to find existing subnets and security group IDs.
# 
# See AWS VPC notebook for creation of these resources.

# In[ ]:


def get_subnet_id(AVZONE,
                  subnet_type='public'):
    
    for vpc in ec2.vpcs.all():
        for az in ec2.meta.client.describe_availability_zones()["AvailabilityZones"]:
            for subnet in vpc.subnets.filter(Filters=[{"Name": "availabilityZone", "Values": [az["ZoneName"]]}]):
                if (az["ZoneName"] == AVZONE) & (subnet_type in subnet.tags[0]['Value']):
                    return vpc.id, subnet.id

def get_security_group_id(session,VPC_ID,SECURITYGROUP_NAME):
    client = boto3.client("ec2", region_name=session.region_name)
    return client.describe_security_groups(Filters = [{"Name":"vpc-id",
                                               "Values":[VPC_ID]
                                               },{
                                                "Name":"group-name",
                                                "Values":[SECURITYGROUP_NAME]
                                              }])\
                ['SecurityGroups'][0]['GroupId']


# ## Launch Existing AMI
# 
# User data necessary for mounting blockchain data volume.  
# 
# **TO DO** create entry in /etc/fstab during EC2 node creation to remove USERDATA.
# 

# In[ ]:


def launch_ami(session, AMI_ID, DATAVOLUME_NAME, INSTANCE_TYPE, DATAVOLUME_SIZE):

    VPC_ID, SUBNET_ID = get_subnet_id(session.region_name+'b',"public")
    SECURITY_GROUP_ID = get_security_group_id(session, VPC_ID, "blockchain-nodes-sg")

    USERDATA = '''#!/bin/bash
    sudo mount /dev/xvdf /data

    sudo xfs_growfs -d /data
    '''

    instance = ec2.create_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        UserData=USERDATA,
        IamInstanceProfile={
            'Name': "blockchain-node-role"
        },
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvdf',
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': DATAVOLUME_SIZE,
                    'VolumeType': 'gp2'
                },
            },
        ],
        InstanceType=INSTANCE_TYPE,
        KeyName="blockchain-nodes-keypair",
        Placement={'AvailabilityZone':session.region_name+'b'},
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': DATAVOLUME_NAME
                    },
                ]
            },
        ],
        NetworkInterfaces=[{'SubnetId': SUBNET_ID, 
                         'DeviceIndex': 0, 
                         'AssociatePublicIpAddress': True, 
                         'Groups': [SECURITY_GROUP_ID]}])
    
    return instance


# In[ ]:


def get_images(session):

    client = boto3.client("ec2", region_name=session.region_name)
    images = client.describe_images(
        Owners=['230081908227'],
    )
    images = pd.DataFrame(images['Images'])      

    images['DataVolumeSize'] = None
    images['nameTag']        = None

    for image in range(len(images)):
        disks = images.iloc[image].BlockDeviceMappings
        for idx in range(len(disks)):
            if disks[idx]['DeviceName']=='/dev/xvdf':
                images.loc[image,'DataVolumeSize'] = images.iloc[image].BlockDeviceMappings[idx]['Ebs']['VolumeSize']

        tags = images.iloc[image].Tags
        for idx in range(len(tags)):
            if images.iloc[image].Tags[idx]['Key']=='Name':
                images.loc[image,'nameTag'] = images.iloc[image].Tags[idx]['Value']
                
    images.CreationDate=pd.to_datetime(images.CreationDate)
    
    selected_image_index = -1

    while True:
        try:
            selected_image_index=int(selected_image_index)
            mask = (selected_image_index>=0) & (selected_image_index<len(images))
            assert( mask )
            if mask:
                break
        except:
            print("\nAWS Available Images (AMI)")
            print(images[['Name','CreationDate','DataVolumeSize']])
            selected_image_index = input('Select a row number [0,'+str(len(images)-1)+'] from available images ')


    DATAVOLUME_NAME     =  images.Name[selected_image_index] + " Chain Data"
    DATAVOLUME_SIZE     =  int(images.DataVolumeSize[selected_image_index])
    AMI_ID              =  images.ImageId[selected_image_index]

    while True:
        try:
            if DATAVOLUME_SIZE=='':
                DATAVOLUME_SIZE = int(images.DataVolumeSize[selected_image_index])
                break
            DATAVOLUME_SIZE=int(DATAVOLUME_SIZE)
            mask = (DATAVOLUME_SIZE > int(images.DataVolumeSize[selected_image_index]))
            assert( mask )
            if mask:
                break
        except:
            DATAVOLUME_SIZE = input('Increase (disk) volume size to (input an integer >= '+                                    str(images.DataVolumeSize[selected_image_index])+                                    ' or press enter to leave unchanged) ')

    types = ['t2.micro','t2.small','t2.medium','t2.large','t2.xlarge','t2.2xlarge']
    while True:
        try:
            if INSTANCE_TYPE in types:
                break
            assert(INSTANCE_TYPE in types)
        except:
            INSTANCE_TYPE = input("Select instance type from "+str(types)+" ")


    #     return images[['Name','nameTag','Description','CreationDate','ImageId','DataVolumeSize']]
    return AMI_ID, DATAVOLUME_NAME, INSTANCE_TYPE, DATAVOLUME_SIZE


# In[ ]:


if __name__ == '__main__':
    
    try:
        session = boto3.Session(profile_name='blockchain-nodes')
    except:
        print('boto3 session profile not found')

    try:
        AMI_ID, DATAVOLUME_NAME, INSTANCE_TYPE, DATAVOLUME_SIZE = get_images(session)
    except:
        print('client not connected on ec2.  unable to get images')
        
    try:
        ec2 = session.resource('ec2')
    except:
        print('ec2 not connected, check aws api credentials')
        
    try:
        print('Loading...',
              '\nAMI_ID:',AMI_ID,
              '\nDATAVOLUME_NAME',DATAVOLUME_NAME,
              '\nINSTANCE_TYPE',INSTANCE_TYPE,
              '\nDATAVOLUME_SIZE',DATAVOLUME_SIZE,'GB')
        instance = launch_ami(session, AMI_ID, DATAVOLUME_NAME, INSTANCE_TYPE, DATAVOLUME_SIZE)
    except:
        print('Failure to launch')


# In[ ]:




