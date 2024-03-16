# Subnet cidr generation for non overlapping ranges

The intention here is to facilitate the generation of cidr ranges subnets, it could be vm subnets, k8s subnets and so on.

The script is done to execute on Google Cloud, but it can be also easily adapted to execute on other Cloud providers.


## Overview

This script is able to fetch the cidrs already deployed in the cloud for a target region(s), in addition, is able to exclude the overlapping and lastly, it suggests cidrs for you.

## Installation

### Prerequisites

- Python 3.x
- Pip (Python package manager)
- Have gcloud installed and configured or the env var GOOGLE_APPLICATION_CREDENTIALS pointing to your credentials file.

### Setup

1. **Clone the repository:**

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


2. **Usage**
  
```
python auto_gen_cidr.py  -p $your-gcp-project-id -r us-central1,us-east1 -v $my-vpc -n 20 -m 20 -c a
```

If you want to create also the secondary cidrs, execute again the commands specifying the new mask.

### Example

Example for k8s nodes with /20 mask:
```
python auto_gen_cidr.py  -p my-project -r us-central1,us-east1 -v vpc-dev -n 20 -m 20 -c a
Warning: Current cidrs deployed in the region us-central1:
 ['10.10.0.0/20', '10.128.0.0/20', '10.40.0.0/16', '10.46.0.0/16', '10.41.0.0/18', '10.44.0.0/18']
Warning: Current cidrs deployed in the region us-east1:
 ['10.142.0.0/20']
 Cidrs availabe with no overlap:
 ['10.0.0.0/20', '10.0.16.0/20', '10.0.32.0/20', '10.0.48.0/20', '10.0.64.0/20', '10.0.80.0/20', '10.0.96.0/20', '10.0.112.0/20', '10.0.128.0/20', '10.0.144.0/20', '10.0.160.0/20', '10.0.176.0/20', '10.0.192.0/20', '10.0.208.0/20', '10.0.224.0/20', '10.0.240.0/20', '10.1.0.0/20', '10.1.16.0/20', '10.1.32.0/20', '10.1.48.0/20']
```


### Arguments

- `-p, --gcp-project`: GCP project id to fetch the subnets already created for a vpc. eg: kgct-dna-matchmaker-dev
- `-r, --regions`: GCP region to fetch the subnets. e.g: us-central1
- `-v, --vpc-name`: VPC name to fetch the subnets, generally the format is: vpc-$environment, e.g: vpc-dev
- `-n, --number`: Number of available subnets to generate.
- `-m, --mask`: Subnet mask for the generated CIDR ranges.
- `-c, --cidr-class`: Subnet class for the generated CIDR ranges. Valid inputs are: a, b, c.

## Notes

- VPC subnet cidrs should be unique and not overlapping
- Ensure the provided CIDR ranges are valid and correctly formatted.
