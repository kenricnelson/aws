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
python command line or any your favorite IDE;
[Spyder](https://www.spyder-ide.org/), Idle,
[pyCharm](https://www.jetbrains.com/pycharm/) among
[others](https://realpython.com/python-ides-code-editors-guide/).


Configuration files
-------------------

[boto3](https://aws.amazon.com/sdk-for-python/) requires a [credentials](credentials) file with your aws access id and key as well as the selected region.

### VPC

The network for a Virtual Private Cloud only needs to be done once.
After the initial set-up you can create as many or as few EC2
instances as you want and launch as many blockchain images (AMIs) as
you want.

. [VPC](VPC.ipynb)  


### EC2 Instance  

An EC2 instance is only required for building a node from scratch.  We
provide the script and set-up instructions (implemented in the
"USER-DATA") for each node in their respective repository.

. [EC2](EC2.ipynb)


### AMI loader

The image can be launched using the VPC results and will automatically
create an ubuntu EC2 instance and appropriate volumes including a
checkpoint of the node through a certain blockheight, generally
recorded in the AMI name.  This is the typical way to launch a node.

. [AMI](AMI.ipynb)