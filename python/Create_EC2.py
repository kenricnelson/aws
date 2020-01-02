#!/usr/bin/env python
# coding: utf-8

# ## Create EC2 instance - generic
# 
# 1. Import boto3 package 
# 2. Read *blockchain-nodes* profile found in ~.aws/credentials
# 3. Create a EC2 session for instance creation
# 4. Read aws details for name, node, datavoluem size and instance type

# In[1]:


import boto3
import os
import pandas as pd


# ## Helper functions to find existing subnets and security group IDs.
# 
# See AWS VPC notebook for creation of these resources.

# In[2]:


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

# In[3]:


def launch_ec2(AMI_DIR, session, id, node):

    ami_details = pd.read_csv(AMI_DIR+'ami.txt',sep='\t')
    ami_details = ami_details[(ami_details.id==id)&(ami_details.node==node)].reset_index()

    VPC_ID, SUBNET_ID = get_subnet_id(session.region_name+'b',"public")
    SECURITY_GROUP_ID = get_security_group_id(session, VPC_ID, "blockchain-nodes-sg")

    DATAVOLUME_NAME     =  ami_details.name[0] + " " + ami_details.node[0] + " Chain Data"
    
    IAM_ROLE = "blockchain-nodes-role"

    USERDATA = '''#!/bin/bash
                    sudo apt-get update

                    sudo mkfs -t xfs /dev/xvdf
                    sudo mkdir /data
                    sudo mount /dev/xvdf /data
                    sudo chown -R ubuntu:ubuntu /data

                    export CHAIN_DATA=/data/{BLOCKCHAIN_ID}
                    echo 'export CHAIN_DATA=/data/{BLOCKCHAIN_ID}'  >> /home/ubuntu/.bashrc

                    export PATH=$PATH:$CHAIN_DATA
                    echo 'export PATH=$PATH:/data/{BLOCKCHAIN_ID}'  >> /home/ubuntu/.bashrc

                    source ~/.bashrc

                    mkdir $CHAIN_DATA
                    cd $CHAIN_DATA

                    sudo chown -R ubuntu:ubuntu /data

                    sudo apt-get update
                    sudo apt-get install -y python3-pip
        '''

instance = ec2.create_instances(
    ImageId=Amazon_Ubuntu_AMI_18_04_LTS,
    MinCount=1,
    MaxCount=1,
    UserData=USERDATA,
    IamInstanceProfile={
        'Name': IAM_ROLE
    },
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/xvdf',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': int(ami_details.datavolume_size[0]),
                'VolumeType': 'gp2'
            },
        },
    ],
    InstanceType=ami_details.type[0],
    KeyName=KEY_NAME,
    Placement={'AvailabilityZone':session.region_name+'b'},
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': ami_details.name[0] + " " + ami_details.node[0]
                },
            ]
        },
    ],
    NetworkInterfaces=[{'SubnetId': SUBNET_ID, 
                     'DeviceIndex': 0, 
                     'AssociatePublicIpAddress': True, 
                     'Groups': [SECURITY_GROUP_ID]}])

    return instance


# In[4]:


if __name__ == '__main__':
    AMI_DIR = '/data/code/aws/dadr/aws/'
    id   = 'ethereum.org'
    node = 'Parity Mainnet'

    try:
        session = boto3.Session(profile_name='blockchain-nodes')
    except:
        print('boto3 session profile not found')

    try:
        ec2 = session.resource('ec2')
    except:
        print('ec2 not connected, check aws api credentials')
        
    try:
        instance = launch_ec2(AMI_DIR, session, id, node)
    except:
        print('Failure to launch')


# In[ ]:




