import boto3

def get_billed_regions():
    try:
        ce_client = boto3.client("ce") 
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": "2025-01-01", "End": "2025-02-02"},  # Adjust date range as needed
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "REGION"}]
        )
        billed_regions = {item["Keys"][0] for item in response["ResultsByTime"][0]["Groups"]}
        return billed_regions
    except Exception as e:
        return set()  # Return empty set if Cost Explorer is not enabled

if __name__ == "__main__":
    
    billed_regions = get_billed_regions()
    
    if billed_regions:
        print("Regions where the customer has resources or billing activity:")
        print(", ".join(sorted(billed_regions)))
    else:
        print("No active resources or billing detected in any region.")
