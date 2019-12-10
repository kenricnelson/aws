Python Scripts for Cloud Rails - AWS
------------------------------------

These python scripts require two packages:

1. [jupyter](https://jupyter.org/install)

   ```bash
   pip install jupyterlab
   ```

2. [boto3](https://aws.amazon.com/sdk-for-python/)

   ```bash
   pip install boto3
   ```

The first package, [jupyter](https://jupyter.org/), is optional, since
the Jupyter notebooks included in this repo can be also run from the
python command line:

```bash
python3 VPC.py
```

or any your favorite IDE; [Spyder](https://www.spyder-ide.org/), Idle,
[PyCharm](https://www.jetbrains.com/pycharm/) among
[others](https://realpython.com/python-ides-code-editors-guide/).


Configuration files
-------------------

The AWS supplied [boto3](https://aws.amazon.com/sdk-for-python/) package requires [credentials](credentials) including your aws access id and key as well as the desired availability region.  **Change the credentials to your own id and key.** The credentials are found by default in your home directory; on ubuntu in:

```bash
~/.aws/credentials
```

See [boto3 credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for complete instructions and additional options.


### VPC Network

The network for a Virtual Private Cloud only needs to be done once.
After the initial VPC Network set-up you can create as many or as few EC2
instances as you want and launch multiple blockchain images (AMIs).

The [VPC notebook](VPC.ipynb) are short scripts that create:

1. Key Pair  
2. VPC  
3. InternetGateway  
4. Route Table  
5. Subnet  
6. Security Group  

The Key Pair is stored in a .pem file and provides for secure ssh. The
VPC, IGW, RT, subnet and security groups provide alternative resources
to default settings.  We will use these settings when launching EC2
instances or AMI images.


### EC2 Instance  

The [EC2 notebook](EC2.ipynb) is useful for building a pre-packaged
node.  We provide the script and set-up instructions (implemented in the
"USERDATA") for each node in their respective repositories.  Also, any
SDK that is supported by the project team can be loaded to the EC2
instance.

All AMI images of full nodes are created from EC2 instances created
with this script.  The Instance Type (#CPUs/RAM) and Volume Size (Gb)
differ between each blockchain, depending on the resources necessary
to replay all blocks and store full, archival nodes of the blockchain.

EC2 instance typical settings:

1. tags for security group and instance names
2. key pair pem file
3. vpc id
4. subnet id 
5. IAM role: "blockchain-node-role"
6. security group: "blockchain-nodes-sg" and id
7. availability zone: region_name (e.g. us-east-2) from credentials profile appended with 'a', 'b', 'c' or other
8. instance [type](https://us-east-2.console.aws.amazon.com/ec2/v2/home?region=us-east-2#LaunchInstanceWizard) .e.g. "micro"=1CPU/1G, "large"=4CPU/8Gb
9. node disk size (Gb): Bitcoin would be about 300 full node


### AMI Loader

The image can be launched using the [AMI notebook](AMI.ipynb).  The
notebook uses the [VPC](VPC.ipynb) resources and will automatically
create an ubuntu EC2 instance and appropriate volumes including a
checkpoint of the node through a certain blockheight, generally
recorded in the AMI name.  This is the typical way to launch a node or
update the node periodically.
