#!/usr/bin/env python
# coding: utf-8

# ## AWS AMI
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
DATAVOLUME_SIZE     =  64

INSTANCE_NAME = 'YOUR BLOCKCHAIN Mainnet/PrivateNet/Testnet/Devnet'
Amazon_Ubuntu_AMI_18_04_LTS = 'ami-0d5d9d301c853a04a'
Instance_Type = 't2.micro' #micro=1GB, small=2GB, medium=4GB, large=8GB https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#LaunchInstanceWizard:

IAM_ROLE = "blockchain-node-role"

AVZONE = session.region_name+'b'
VPC_ID, SUBNET_ID = get_subnet_id(AVZONE,"public")
SECURITY_GROUP_ID = get_security_group_id(session,VPC_ID,SECURITYGROUP_NAME)


# ## Launch Existing AMI
# 
# User data necessary for mounting blockchain data volume.  
# 
# **TO DO** create entry in /etc/fstab during EC2 node creation to remove USERDATA.
# 

# In[ ]:


USERDATA = '''#!/bin/bash
sudo mount /dev/xvdf /data
'''

instances = ec2.create_instances(
    ImageId='ami-008978f48f0085bfd',
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
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': DATAVOLUME_NAME
                },
            ]
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

