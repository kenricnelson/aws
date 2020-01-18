Blockchain Resources Cloud Rails - AWS
======================================

https://aws.amazon.com

What are Cloud Rails?
---------------------

Cloud Rails is the minimal set-up of network, server and checkpoint
blockchain data required to spin-up a fully functioning node.  Cloud
Rails provides a common framework for developers across all blockchain
platforms and projects.

**Cloud Rails - AWS** is the Amazon Web Services version and includes
scripts in [python](python), [node](node), [go](go) and [java](java)
creating a Virtual Private Cloud (VPC) with all networking, an EC2
instance (server) running the ubuntu operating system, a loader for an
image file (AMI) contained in two volumes (disks). One disk, typically
8Gb, for the operating system, blockchain software and project's
Software Development Kits (SDK).  The other volume (8Gb - 1T) includes
a synched image of the blockchain at a point in time that is
periodically updated. Each language includes the necessary packages
and configuration files to run the scripts.


License
-------

Cloud Rails is released under the terms of the MIT license. See
[COPYING](COPYING.md) for more information or see
https://opensource.org/licenses/MIT.


Getting Started on AWS
----------------------

The steps below outline creating an AWS account, creating some users,
generating access keys and the importance of selecting a region.  Amazon has extensive tutorials on using their cloud services including using their UI to [launch a server.](https://aws.amazon.com/getting-started/tutorials/launch-a-virtual-machine)  Below are the minimum required steps to use Cloud Rails - AWS.  **Note that AWS accounts require a valid credit card**.

1. [Create an AWS account.](https://portal.aws.amazon.com/billing/signup)  
  
2. [Create users]()

3. [Generate api access id and key]()

4. Select region to use; e.g. us-east-2


Scripts  
-------

We currently support four scripting languages;
[Python](python/README.md), [Node](node), [Go](go) and [Java](java).
Feel free to add more!  Each directory contains the set-up
instructions for that langauge, packages, configurations and jupyter
notebooks to initially set up the network (once), create a node from
scratch and launch a pre-existing image with a checkpoint node.





  
