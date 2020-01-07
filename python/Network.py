#!/usr/bin/env python
# coding: utf-8

# ## AWS Create Network
# 
# One time execution for creating VPC, network, keypair and IAM role in a specified AWS region.
# 
# 1. Import boto3 package 
# 2. Read *blockchain-nodes* profile found in ~.aws/credentials
# 3. Create a EC2 session for instance creation
# 4. IAM Role
# 5. Keypair
# 6. VPC
# 7. InternetGateway
# 8. Route Table
# 9. Subnet
# 10. Security Group

# In[ ]:


import boto3
import os

session = boto3.Session(profile_name='blockchain-nodes')
ec2 = session.resource('ec2')

KEY_DIRECTORY = "/YOUR/KEY/DIRECTORY/"
PREFIX = "blockchain-nodes-"


# ## Create IAM Role
# 

# In[ ]:


# Create IAM client
iam = boto3.client('iam')
policy = { 
    "Version": "2012-10-17", "Statement":
    [ 
        { 
            "Effect": "Allow", 
            "Principal": { "Service": "ec2.amazonaws.com" }, 
            "Action": "sts:AssumeRole" 
        } 
    ]
}

tags = [
        {
            'Key': 'Name',
            'Value': PREFIX + 'role'
        },
    ]

response = iam.create_role(
    Path='/',
    RoleName=PREFIX + 'role',
    AssumeRolePolicyDocument=json.dumps(policy),
    Description='Minimal IAm role for EC2 create_instance profile',
    MaxSessionDuration=3600,
    Tags=tags
)


response = iam.attach_role_policy(
    RoleName=PREFIX + 'role', PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')

print(response)


# ## Create Key Pair for ssh into EC2 instances
# 
# * key pem files can be used multiple times; just create on for all EC2 instances

# In[ ]:


file = KEY_DIRECTORY + PREFIX + 'keypair.pem'
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

vpc.create_tags(Tags=[{"Key": "Name", "Value": PREFIX + 'vpc'}])

vpc.wait_until_available()
print(vpc.id)


# ## Create and Attach Internet Gateway

# In[ ]:


# create then attach internet gateway
ig = ec2.create_internet_gateway()
ig.create_tags(Tags=[{"Key": "Name", "Value": PREFIX + 'igw'}])
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)


# ## Create a Route Table and a Public Route

# In[ ]:


# create a route table and a public route
route_table = vpc.create_route_table()
route_table.create_tags(Tags=[{"Key": "Name", "Value": PREFIX + 'rt'}])

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
    GroupName = PREFIX + 'sg', 
    Description = 'Allow SSH, HTTP and HTTPS', 
    VpcId = vpc.id)

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

sec_group.create_tags(Tags=[{"Key": "Name", "Value": PREFIX + 'sg'}])

instance_security_group_id=sec_group.id

print(sec_group.id)

