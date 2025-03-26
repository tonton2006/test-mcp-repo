from mcp.server.fastmcp import FastMCP
import sys
import os
import json
import argparse
from google.oauth2 import service_account
from google.cloud import compute_v1
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create an MCP server
mcp = FastMCP("GCP Manager")

# Path to GCP service account credentials
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "credentials.json")

# Get GCP credentials
def get_credentials():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GCP_CREDENTIALS_PATH, 
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return credentials
    except Exception as e:
        print(f"Error loading credentials: {str(e)}", file=sys.stderr)
        return None

# List VM instances
@mcp.tool()
def list_instances(project: str, zone: str) -> dict:
    """List VM instances in a GCP project and zone"""
    print(f"Listing instances in project={project}, zone={zone}", file=sys.stderr)
    
    try:
        credentials = get_credentials()
        if not credentials:
            return {"error": "Failed to load GCP credentials"}
        
        instance_client = compute_v1.InstancesClient(credentials=credentials)
        request = compute_v1.ListInstancesRequest(
            project=project,
            zone=zone
        )
        
        # Get all instances and convert to serializable format
        instances = []
        for instance in instance_client.list(request=request):
            instances.append({
                "id": instance.id,
                "name": instance.name,
                "machine_type": instance.machine_type,
                "status": instance.status,
                "zone": instance.zone,
                "creation_timestamp": instance.creation_timestamp
            })
        
        return {
            "instances": instances,
            "count": len(instances),
            "status": "success"
        }
    except Exception as e:
        print(f"Error listing instances: {str(e)}", file=sys.stderr)
        return {
            "error": str(e),
            "status": "error"
        }

# Start an instance
@mcp.tool()
def start_instance(project: str, zone: str, instance_name: str) -> dict:
    """Start a VM instance in GCP"""
    print(f"Starting instance {instance_name} in project={project}, zone={zone}", file=sys.stderr)
    
    try:
        credentials = get_credentials()
        if not credentials:
            return {"error": "Failed to load GCP credentials"}
        
        instance_client = compute_v1.InstancesClient(credentials=credentials)
        operation = instance_client.start(
            project=project,
            zone=zone,
            instance=instance_name
        )
        
        return {
            "operation_id": operation.name,
            "status": "pending",
            "message": f"Start operation initiated for {instance_name}"
        }
    except Exception as e:
        print(f"Error starting instance: {str(e)}", file=sys.stderr)
        return {
            "error": str(e),
            "status": "error"
        }

# Stop an instance
@mcp.tool()
def stop_instance(project: str, zone: str, instance_name: str) -> dict:
    """Stop a VM instance in GCP"""
    print(f"Stopping instance {instance_name} in project={project}, zone={zone}", file=sys.stderr)
    
    try:
        credentials = get_credentials()
        if not credentials:
            return {"error": "Failed to load GCP credentials"}
        
        instance_client = compute_v1.InstancesClient(credentials=credentials)
        operation = instance_client.stop(
            project=project,
            zone=zone,
            instance=instance_name
        )
        
        return {
            "operation_id": operation.name,
            "status": "pending",
            "message": f"Stop operation initiated for {instance_name}"
        }
    except Exception as e:
        print(f"Error stopping instance: {str(e)}", file=sys.stderr)
        return {
            "error": str(e),
            "status": "error"
        }

# Get instance details
@mcp.tool()
def get_instance(project: str, zone: str, instance_name: str) -> dict:
    """Get details of a specific VM instance"""
    print(f"Getting instance details for {instance_name} in project={project}, zone={zone}", file=sys.stderr)
    
    try:
        credentials = get_credentials()
        if not credentials:
            return {"error": "Failed to load GCP credentials"}
        
        instance_client = compute_v1.InstancesClient(credentials=credentials)
        instance = instance_client.get(
            project=project,
            zone=zone,
            instance=instance_name
        )
        
        # Convert to serializable format
        instance_data = {
            "id": instance.id,
            "name": instance.name,
            "machine_type": instance.machine_type,
            "status": instance.status,
            "zone": instance.zone,
            "creation_timestamp": instance.creation_timestamp,
            "network_interfaces": [],
            "disks": []
        }
        
        # Add network interfaces
        for nic in instance.network_interfaces:
            nic_data = {
                "name": nic.name,
                "network": nic.network,
                "network_ip": nic.network_ip,
                "access_configs": []
            }
            for ac in nic.access_configs:
                nic_data["access_configs"].append({
                    "name": ac.name,
                    "type": ac.type_,
                    "nat_ip": ac.nat_ip
                })
            instance_data["network_interfaces"].append(nic_data)
        
        # Add disks
        for disk in instance.disks:
            instance_data["disks"].append({
                "boot": disk.boot,
                "auto_delete": disk.auto_delete,
                "source": disk.source
            })
        
        return {
            "instance": instance_data,
            "status": "success"
        }
    except Exception as e:
        print(f"Error getting instance details: {str(e)}", file=sys.stderr)
        return {
            "error": str(e),
            "status": "error"
        }

# Add explicit server start when script is run directly
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the GCP MCP server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()
    
    # Start the server
    print(f"Starting GCP MCP server on {args.host}:{args.port}", file=sys.stderr)
    mcp.serve(host=args.host, port=args.port)