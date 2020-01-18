#!/usr/bin/env python
# coding: utf-8

# ## AWS EC2
# 
# 1. Import boto3 package 
# 2. Read *blockchain-nodes* profile found in ~.aws/credentials
# 3. Create a EC2 session for instance creation

# In[ ]:


import boto3
import os

session = boto3.Session(profile_name='blockchain-nodes')
ec2 = session.resource('ec2')


# ## Helper functions to find existing subnets and security group IDs.
# 
# See AWS VPC notebook for creation of these resources.

# In[ ]:


def get_subnet_id(AVZONE=session.region_name+'b',
                  subnet_type='public'):
    
    for vpc in ec2.vpcs.all():
        for az in ec2.meta.client.describe_availability_zones()["AvailabilityZones"]:
            for subnet in vpc.subnets.filter(Filters=[{"Name": "availabilityZone", "Values": [az["ZoneName"]]}]):
                #print(vpc.id, az["ZoneName"], subnet.id, subnet.tags[0]['Value'])
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


# ## Set Variables
# 
# 1. tags
# 2. selecting key pair pem file
# 3. vpc
# 4. subnet
# 5. IAM role
# 6. security group
# 7. availability zone
# 8. instance type
# 9. node disk size (Gb)
# 

# In[ ]:


BLOCKCHAIN_ID = "YOUR_BLOCKCHAIN"

KEY_NAME  =  "blockchain-nodes-keypair"
KEY_DIRECTORY = "/YOUR/KEY/DIRECTORY/"


SECURITYGROUP_NAME  =  "blockchain-nodes-sg"

DATAVOLUME_NAME     =  "YOUR BLOCKCHAIN Mainnet/PrivateNet/Testnet/Devnet Chain Data"
DATAVOLUME_SIZE     =  100

INSTANCE_NAME = 'YOUR BLOCKCHAIN Mainnet/PrivateNet/Testnet/Devnet'
Amazon_Ubuntu_AMI_18_04_LTS = 'ami-0d5d9d301c853a04a'
Instance_Type = 't2.micro' #micro=1GB, small=2GB, medium=4GB, large=8GB https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#LaunchInstanceWizard:

IAM_ROLE = "blockchain-node-role"

AVZONE = session.region_name+'b'
VPC_ID, SUBNET_ID = get_subnet_id(AVZONE,"public")
SECURITY_GROUP_ID = get_security_group_id(session,VPC_ID,SECURITYGROUP_NAME)


# ## Create EC2 Instance
# 
# User data for ubuntu server initialization, see each blockchain repo for USERDATA specific to each node.
# 

# In[ ]:


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
sudo chown -R ubuntu:ubuntu /data

sudo apt-get update
sudo apt-get install -y python3-pip

'''.format(BLOCKCHAIN_ID=BLOCKCHAIN_ID)

instances = ec2.create_instances(
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
                'VolumeSize': DATAVOLUME_SIZE,
                'VolumeType': 'gp2'
            },
        },
    ],
    InstanceType=Instance_Type,
    KeyName=KEY_NAME,
    Placement={'AvailabilityZone':AVZONE},
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': INSTANCE_NAME
                },
            ]
        },
    ],
    NetworkInterfaces=[{'SubnetId': SUBNET_ID, 
                     'DeviceIndex': 0, 
                     'AssociatePublicIpAddress': True, 
                     'Groups': [SECURITY_GROUP_ID]}])

