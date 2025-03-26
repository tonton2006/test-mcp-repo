from mcp.server.fastmcp import FastMCP
import sys
import os
import requests
import traceback
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create an MCP server
mcp = FastMCP("Demo")

# Boomi endpoint and credentials
BOOMI_ENDPOINT = "https://c02-usa-east.integrate.boomi.com/ws/simple/executeMCPHelloWorld"
BOOMI_USERNAME = "mcp@solutionsteam-70I6P5.C3P9B2"
BOOMI_TOKEN = os.getenv("BOOMI_TOKEN")

# Print debug info to stderr
print(f"Boomi MCP server initialized", file=sys.stderr)
print(f"Boomi token loaded: {'Yes' if BOOMI_TOKEN else 'No'}", file=sys.stderr)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> dict:
    """Add two numbers using Boomi integration"""
    print(f"Add tool called with a={a}, b={b}", file=sys.stderr)

    # Calculate result locally as fallback
    local_result = a + b

    try:
        # Prepare the payload for Boomi
        payload = {
            "a": str(a),
            "b": str(b)
        }

        print(f"Making request to Boomi with payload: {payload}", file=sys.stderr)

        # Make the authenticated request to Boomi
        response = requests.post(
            BOOMI_ENDPOINT,
            auth=(BOOMI_USERNAME, BOOMI_TOKEN),
            json=payload,
            timeout=10
        )

        print(f"Boomi response status: {response.status_code}", file=sys.stderr)

        if response.status_code == 200:
            try:
                boomi_response = response.json()
                print(f"Boomi JSON response: {boomi_response}", file=sys.stderr)

                # Map the response fields correctly based on Boomi's actual response format
                return {
                    "sum": int(boomi_response.get("result", local_result)),
                    "runtime_name": boomi_response.get("atom_name", "Unknown"),
                    "execution_id": boomi_response.get("execution_id", "Unknown"),
                    "status": "success"
                }
            except Exception as e:
                print(f"Error parsing JSON: {e}, Raw response: {response.text}", file=sys.stderr)
                return {
                    "sum": local_result,
                    "status": "json_parse_error",
                    "error": f"Failed to parse Boomi response: {str(e)}"
                }
        else:
            print(f"HTTP error {response.status_code}: {response.text}", file=sys.stderr)
            return {
                "sum": local_result,
                "status": "http_error",
                "error": f"HTTP {response.status_code}: {response.text[:100]}"
            }

    except Exception as e:
        print(f"Request error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {
            "sum": local_result,
            "status": "request_error",
            "error": str(e)
        }

# Add explicit server start when script is run directly
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the MCP server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()
    
    # Start the server
    print(f"Starting MCP server on {args.host}:{args.port}", file=sys.stderr)
    mcp.serve(host=args.host, port=args.port)