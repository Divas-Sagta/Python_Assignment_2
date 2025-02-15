import boto3

def get_active_regions():
    active_regions = set()
    ec2_client = boto3.client("ec2", "us-east-1")
    
    # Get all available AWS regions
    all_regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    # List of services to check for active resources
    services_to_check = {
        "ec2": {"method": "describe_instances", "key": "Reservations"},
        "rds": {"method": "describe_db_instances", "key": "DBInstances"},
        "lambda": {"method": "list_functions", "key": "Functions"},
        "s3": {"method": "list_buckets", "key": "Buckets"},
        "vpc": {"method": "describe_vpcs", "key": "Vpcs"}
    }
    
    # Check each region for active resources
    for region in all_regions:
        for service, details in services_to_check.items():
            try:
                client = boto3.client(service, region_name=region)
                response = getattr(client, details["method"])()
                
                # Ensure there are non-default, active resources
                if service == "ec2" and any(res["Instances"] for res in response.get("Reservations", [])):
                    active_regions.add(region)
                elif service == "rds" and response.get(details["key"]):
                    active_regions.add(region)
                elif service == "lambda" and response.get(details["key"]):
                    active_regions.add(region)
                elif service == "s3" and response.get(details["key"]):
                    # Ensure at least one bucket is in the region
                    s3_client = boto3.client("s3")
                    for bucket in response["Buckets"]:
                        bucket_location = s3_client.get_bucket_location(Bucket=bucket["Name"])["LocationConstraint"]
                        if bucket_location == region or (bucket_location is None and region == "us-east-1"):
                            active_regions.add(region)
                elif service == "vpc":
                    # Ensure there is a non-default VPC
                    if any(not vpc.get("IsDefault", True) for vpc in response.get("Vpcs", [])):
                        active_regions.add(region)

            except Exception as e:
                pass  # Ignore errors for services not available in a region
    
    return active_regions

def get_billed_regions():
    try:
        ce_client = boto3.client("ce", region_name="us-east-1")  # Cost Explorer is available only in us-east-1
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": "2024-01-01", "End": "2024-02-01"},  # Adjust date range as needed
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}]
        )
        billed_regions = {item["Keys"][0] for item in response["ResultsByTime"][0]["Groups"]}
        return billed_regions
    except Exception as e:
        return set()  # Return empty set if Cost Explorer is not enabled

if __name__ == "__main__":
    active_regions = get_active_regions()
    billed_regions = get_billed_regions()

    all_regions = active_regions.union(billed_regions)
    
    if all_regions:
        print("Regions where the customer has actively created resources or billing activity:")
        print(", ".join(sorted(all_regions)))
    else:
        print("No active resources or billing detected in any region.")
