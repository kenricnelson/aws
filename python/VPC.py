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


# ## Create Network
# 1. VPC
# 2. InternetGateway
# 3. Route Table
# 4. Subnet
# 5. Security Group

# In[ ]:


KEY_NAME  =  "blockchain-nodes-keypair"
KEY_DIRECTORY = "/YOUR/KEY/DIRECTORY/"

SECURITYGROUP_NAME  =  "blockchain-nodes-sg"

DATAVOLUME_NAME     =  "YOUR BLOCKCHAIN Mainnet/PrivateNet/Testnet/Devnet Chain Data"
DATAVOLUME_SIZE     =  64

INSTANCE_NAME = 'YOUR BLOCKCHAIN Mainnet/PrivateNet/Testnet/Devnet'
Amazon_Ubuntu_AMI_18_04_LTS = 'ami-0d5d9d301c853a04a'  #ubuntu 18.04
Instance_Type = 't2.micro' #micro=1GB, small=2GB, medium=4GB, large=8GB https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#LaunchInstanceWizard:

AVZONE = session.region_name+'b'
VPC_ID, SUBNET_ID = get_subnet_id(AVZONE,"public")
SECURITY_GROUP_ID = get_security_group_id(session,VPC_ID,SECURITYGROUP_NAME)


# ## Create Key Pair for EC2 Instance
# 
# * key pem files can be used multiple times; just create on for all EC2 instances

# In[ ]:


file = KEY_DIRECTORY + KEY_NAME + '.pem'
outfile = open(file,'w')

# call the boto ec2 function to create a key pair
key_pair = ec2.create_key_pair(KeyName=KEY_NAME)

# capture the key and store it in a file
KeyPairOut = str(key_pair.key_material)
print(KeyPairOut)
outfile.write(KeyPairOut)
outfile.close()

os.chmod(file,0o400)


# ## Create Virtual Private Cloud (VPC)

# In[ ]:


vpc = ec2.create_vpc(CidrBlock='10.1.0.0/16')

vpc.create_tags(Tags=[{"Key": "Name", "Value": VPC_NAME}])

vpc.wait_until_available()
print(vpc.id)


# ## Create and Attach Internet Gateway

# In[ ]:


# create then attach internet gateway
ig = ec2.create_internet_gateway()
ig.create_tags(Tags=[{"Key": "Name", "Value": IGW_NAME}])
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)


# ## Create a Route Table and a Public Route

# In[ ]:


# create a route table and a public route
route_table = vpc.create_route_table()
route_table.create_tags(Tags=[{"Key": "Name", "Value": ROUTETABLE_NAME}])

route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id
)

print(route_table.id)


# ## Create subnets
# 

# In[ ]:


# create subnet
# only associate public nets with route table

subnet = ec2.create_subnet(CidrBlock='10.1.1.0/24', VpcId=vpc.id, AvailabilityZone=SUBNET+'a')
subnet.create_tags(Tags=[{"Key": "Name", "Value": SUBNET_NAME + "public"}])
# associate the route table with the subnet
route_table.associate_with_subnet(SubnetId=subnet.id)

print('subnet',subnet.id)


# ## Create Security Group

# In[ ]:


# Create security group
sec_group = ec2.create_security_group(
    GroupName=SECURITYGROUP_NAME, Description='Allow SSH, HTTP and HTTPS', VpcId=vpc.id)

sec_group.authorize_ingress(
    GroupId=sec_group.id,
    IpPermissions=[
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
         'FromPort': 443,
         'ToPort': 443,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
         'FromPort': 22,
         'ToPort': 22,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ])

sec_group.create_tags(Tags=[{"Key": "Name", "Value": SECURITYGROUP_NAME}])

instance_security_group_id=sec_group.id

print(sec_group.id)

