import argparse
import ipaddress
import sys
from google.cloud import compute_v1

def get_taken_cidrs(gcp_project, region, vpc):
    # Create a client to interact with the Compute Engine API
    subnets_client = compute_v1.SubnetworksClient()

    # List subnets with the specified filter
    response = subnets_client.list(project=gcp_project, region=region)

    # Iterate over the response and print subnet information
    taken_subnets = []
    taken_secondary_subnets = []
    for subnet in response:
        gcp_region = subnet.region.split("/")[-1]
        gcp_network = subnet.network.split("/")[-1]
        if gcp_region == region and gcp_network == vpc:
            if subnet.secondary_ip_ranges:
                for secondary_ip_range in subnet.secondary_ip_ranges:
                    taken_secondary_subnets.append(
                        str(secondary_ip_range.ip_cidr_range)
                    )
            taken_subnets.append(str(subnet.ip_cidr_range))

    merged_taken_subnets = taken_subnets + taken_secondary_subnets
    print(
        f"\033[33mWarning: Current cidrs deployed in the region {region}:\n {merged_taken_subnets}"
    )
    return merged_taken_subnets

def get_taken_cidrs_for_regions(gcp_project, regions, vpc, ):
  
    all_taken_cidrs = []
    for region in regions.split(","):
        taken_cidrs = get_taken_cidrs(gcp_project, region, vpc )
        all_taken_cidrs.extend(taken_cidrs)
  
    return all_taken_cidrs

def create_subnets(max_subnets, mask, cidr_class):
    subnets = []
    # Define a list of IP addresses representing Class A, B, and C networks
    # Defining everything as /8 here since GCP doesn't have a range for main VPC,
    # ipaddress lib needs that to calculate the range, so the following is needed.
    ip_addresses_class = {"a": "10.0.0.0/8", "b": "172.0.0.0/8", "c": "192.0.0.0/8"}

    # Variable to choose the class
    chosen_class = (
        cidr_class  # You can change this to 'b' or 'c' to choose different classes
    )

    # Accessing the chosen class from the dictionary
    chosen_ip_address = ip_addresses_class.get(chosen_class)
    ip_addresses = ipaddress.IPv4Network(chosen_ip_address)

    # Counter to keep track of the number of subnets created
    subnet_count = 0

    for sn in ip_addresses.subnets(new_prefix=mask):
        if (
            subnet_count >= max_subnets
        ):  # Check if the maximum number of subnets is reached
            break  # Exit the loop if the maximum is reached
        subnets.append(str(sn))
        subnet_count += 1
    return subnets


def get_available_subnets(base_cidr_list, existent_subnets_gcp, available_length, mask):
    # Convert base ranges and taken subnets into ip_network objects
    base_networks = [ipaddress.IPv4Network(base_cidr) for base_cidr in base_cidr_list]
    taken_networks = [
        ipaddress.IPv4Network(taken_cidr) for taken_cidr in existent_subnets_gcp
    ]
    available_subnets = []

    # Iterate over each base network range
    for subnet in base_networks:
        # Check if the base network is smaller than the requested mask
        if subnet.prefixlen > mask:
            print(
                f"\033[31mError: Base network {subnet} has a smaller mask than the requested /{mask}."
            )
            sys.exit(1)
        if not any(subnet.overlaps(taken_network) for taken_network in taken_networks):
            available_subnets.append(str(subnet))
    return available_subnets


def main():
    parser = argparse.ArgumentParser(
        description="Find available subnets with a specified mask."
    )
    parser.add_argument(
        "-p", "--gcp-project", help="GCP Project id to featch the subnets."
    )
    parser.add_argument("-r", "--regions", help="Region to find the subnets.")
    parser.add_argument("-v", "--vpc-name", help="VPC name to find the subnets.")
    parser.add_argument(
        "-c",
        "--cidr-class",
        help="Cidr class to create the subnets. Valid values are: a, b, c",
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10,
        help="Number of available subnets to generate",
    )
    parser.add_argument(
        "-m",
        "--mask",
        type=int,
        default=20,
        help="Subnet mask for the generated CIDR ranges (e.g., 24 for /24)",
    )
    args = parser.parse_args()

    all_taken_cidrs = get_taken_cidrs_for_regions(args.gcp_project, args.regions, args.vpc_name)
    base_cidr_list_suggestion = create_subnets(args.number, args.mask, args.cidr_class)
    available = get_available_subnets(
        base_cidr_list_suggestion, all_taken_cidrs, args.number, args.mask
    )
    print(
        "\033[92m Cidrs availabe with no overlap:\n", available
    )  # Prints the specified number of available subnets with the provided mask


if __name__ == "__main__":
    main()
