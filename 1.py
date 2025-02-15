# Write a python program using boto3 to list all available types of ec2 instances in each region. 
# Make sure the instance type won’t repeat in a region. Put it in a csv with these columns.
# bo(region, instance_type.)



import boto3
import csv

def get_regions():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.describe_regions()
    return [region["RegionName"] for region in response["Regions"]]

def get_instance_types(region):
    ec2_client = boto3.client("ec2", region_name=region)
    instance_types = set()
    paginator = ec2_client.get_paginator("describe_instance_type_offerings")
    
    for page in paginator.paginate(LocationType="region"):
        for offering in page["InstanceTypeOfferings"]:
            instance_types.add(offering["InstanceType"])
    
    return instance_types

def write_to_csv(data, filename="ec2_instance_types.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["region", "instance_type"])
        for region, instance_types in data.items():
            for instance_type in instance_types:
                writer.writerow([region, instance_type])

def main():
    regions = get_regions()
    ec2_data = {}
    
    for region in regions:
        print(f"Fetching instance types for region: {region}")
        ec2_data[region] = get_instance_types(region)
    
    write_to_csv(ec2_data)
    print("EC2 instance types have been written to ec2_instance_types.csv")

if __name__ == "__main__":
    main()
