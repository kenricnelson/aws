Blockchain Resources Cloud Rails - AWS
======================================

https://aws.amazon.com

What are Cloud Rails?
---------------------

Cloud Rails is the minimal set-up of network, server and checkpoint
blockchain data required to spin-up a fully functioning node.  Cloud
Rails provides a common hosting framework for developers across all
blockchain platforms and projects.

**Cloud Rails - AWS** is the Amazon Web Services version and includes
scripts in [python](python), [node](node), [go](go) and [java](java)
creating a Virtual Private Cloud (VPC) with all networking and
credentials, an EC2 instance (server) running the ubuntu operating
system, a loader (and creator) for an image file (AMI) contained in
two volumes (disks).

One volume, typically 8Gb, is reserved for the operating system,
blockchain software and project's Software Development Kits (SDK).
The data storage volume (8Gb - 2T) (local server variable $CHAIN_DATA)
includes a synched image of the blockchain at a point in time that is
periodically updated; see table below. 

There are repos for each coin with specific settings (AMI ID, instance
type and volume size) and configuration options.  For example
[bitcoin](../bitcoin/README.md)


License
-------

Cloud Rails is released under the terms of the MIT license. See
[COPYING](COPYING.md) for more information or see
https://opensource.org/licenses/MIT.


Getting Started on AWS
----------------------

The steps below outline creating an AWS account, creating some users,
generating access keys and the importance of selecting a region.
Amazon has extensive tutorials on using their cloud services including
using their UI to [launch a
server.](https://aws.amazon.com/getting-started/tutorials/launch-a-virtual-machine)
Below are the minimum required steps to use Cloud Rails - AWS.  **Note
that AWS accounts require a valid credit card**.

1. [Create an AWS account.](https://portal.aws.amazon.com/billing/signup)  
  
2. [Create users](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html)

3. [Generate api access id and key](https://console.aws.amazon.com/iam/home?#/security_credentials)

4. Select region to use.  We use us-east-2 to store the AMIs

5. Step thru the [Network notebook](python/Network.ipynb) ***once***
filling in the appropriate local directory to store the generated
keypair .pem file.

6. Step thru the [AMI notebook](python/AMI.ipynb) selecting the **ID**
(e.g. ethereum.org) and **node** (e.g. Go Mainnet) for the desired
blockchain from the table below.  This will launch an EC2 instance and
start syncing the blockchain from the previous block height.

7. ssh into the launched instance using the generated keypair in step 5 and the IP address.


Scripts  
-------

We currently support four scripting languages;
[Python](python/README.md), [Node](node), [Go](go) and [Java](java).
Read [contributing](CONTRIBUTING.md) to add more support.

Each directory contains the set-up instructions for that langauge,
packages, configurations and jupyter notebooks to:

1. [Set up the network](python/Network.ipynb) and credentials (once)
2. [Create a node](python/Create_EC2.ipynb) from source
3. [Launch a pre-existing image](python/AMI.ipynb) with a checkpoint node
4. (optionally) [Create an image](python/CREATE_AMI.ipynb) at the current block height

This repo will have the common structure to generate a node; chain
specific scripts are found in the corresponding coin repo;
e.g. [launch a bitcoin mainnet image](https://github.com/Digital-Asset-Developer-Resources/bitcoin/blob/master/AMI.ipynb).


Resources
---------

The table below details the latest coin specific resources for each
node type and is updated periodically as resource requirements change
(increase).

| ID           | Node           | Date                | Block   | AMI ID                | Name     | Type       | DATAVOLUME_SIZE (GB) |
|--------------|----------------|---------------------|---------|-----------------------|----------|------------|----------------------|
| bitcoin.org  | Mainnet        | 2019-12-28 21:24:00 |  610208 | ami-0106f83c9203e626f | Bitcoin  | t2.2xlarge |                  350 |
| ethereum.org | Go Mainnet     | 2019-12-30 00:11:00 | 9183290 | ami-0004031a4ee8254c0 | Ethereum | t2.2xlarge |                  250 |
| ethereum.org | Parity Mainnet | 2020-01-01 13:42:00 | 9196049 | ami-05c08969541b3500b | Ethereum | t2.medium  |                  200 |
| algorand.com | Mainnet        | 2019-12-31 18:24:00 | 4002414 | ami-021305cee8b57d1bb | Algorand | t2.medium  |                  100 |
| algorand.com | Testnet        | 2019-12-32 00:00:00 |       0 |                       | Algorand | t2.medium  |                   50 |


All public images can be [searched](https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#Images:visibility=public-images;tag:Name=SRP;sort=desc:creationDate) using the "Public Images" dropdown and filtering on the "Name Tag" with "SRP", see below.

![public AMI search](https://github.com/Digital-Asset-Developer-Resources/aws/blob/master/images/AMI_search.png) 