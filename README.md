# Frontend-Agnostic MCP Server

A Multi-Core Processing (MCP) server that can be used with any frontend, not just Claude Desktop.

## Changes Made

The original script was designed specifically for Claude Desktop, which automatically handles the server initialization. The updated script adds:

1. An explicit `mcp.serve()` call to start the server
2. Command-line argument parsing for host/port configuration
3. A proper `if __name__ == "__main__":` block to allow the script to be imported without starting the server

## Setup

1. Install dependencies:
   ```
   pip install mcp-server requests python-dotenv
   ```

2. Create a `.env` file with your Boomi token:
   ```
   BOOMI_TOKEN=your_token_here
   ```

3. Run the server:
   ```
   python mcp_server.py
   ```

   Optional arguments:
   - `--host`: Host to bind to (default: 0.0.0.0)
   - `--port`: Port to listen on (default: 8000)

## Usage

The server exposes an `add` tool that can be called from any frontend that supports the MCP protocol. The tool adds two numbers using a Boomi integration, with a local fallback.

## How It Works

This MCP server connects to a Boomi integration process for adding numbers. If the Boomi service fails, it falls back to calculating the sum locally.

## Using with Different Frontends

### With Python Client
```python
from mcp.client import Client

client = Client("http://localhost:8000")
result = client.add(a=5, b=10)
print(result)
```

### With HTTP Request
```
POST http://localhost:8000/v1/tools/add
Content-Type: application/json

{
  "a": 5,
  "b": 10
}
```