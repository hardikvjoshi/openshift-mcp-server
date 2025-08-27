#!/usr/bin/env python3
"""
OpenShift MCP Client

A simple client for testing the OpenShift MCP server.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenShiftMCPClient:
    def __init__(self, server_command: str):
        """Initialize the MCP client.
        
        Args:
            server_command: Command to start the MCP server
        """
        self.server_command = server_command
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        """Connect to the MCP server."""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.server_command,
                args=[],
                env={}
            )
            
            # Connect to the server
            async with stdio_client(server_params) as (read_stream, write_stream):
                # Create a client session
                self.session = ClientSession(
                    read_stream,
                    write_stream,
                    "openshift-mcp-client",
                    "1.0.0"
                )
                
                # Initialize the session
                await self.session.initialize()
                logger.info("Connected to MCP server")
                
                # List available tools
                tools = await self.session.list_tools()
                logger.info(f"Available tools: {[tool['name'] for tool in tools]}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            return False
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        try:
            result = await self.session.call_tool(name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the client session."""
        if self.session:
            await self.session.close()

async def main():
    """Main function to run the MCP client."""
    # Check if environment variables are set
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    
    if not cluster_url or not token:
        print("Error: OPENSHIFT_CLUSTER_URL and OPENSHIFT_TOKEN environment variables must be set")
        print("Please set them in your .env file or export them")
        sys.exit(1)
    
    # Create client with shell command
    server_command = "bash -c '.venv/bin/python openshift_mcp_server.py'"
    client = OpenShiftMCPClient(server_command)
    
    try:
        # Connect to server
        if not await client.connect():
            print("Failed to connect to MCP server")
            sys.exit(1)
        
        print("Connected to OpenShift MCP Server!")
        print("Available commands:")
        print("  1. list_namespaces")
        print("  2. list_pods <namespace>")
        print("  3. list_services <namespace>")
        print("  4. list_routes <namespace>")
        print("  5. get_resource_usage <namespace>")
        print("  6. quit")
        print()
        
        # Interactive loop
        while True:
            try:
                command = input("mcp> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                
                if command == "list_namespaces":
                    result = await client.call_tool("list_namespaces", {})
                    if "error" in result:
                        print(f"Error: {result['error']}")
                    else:
                        print("Namespaces:")
                        for ns in result.get("namespaces", []):
                            print(f"  - {ns['name']} ({ns['status']})")
                
                elif command.startswith("list_pods "):
                    namespace = command.split(" ", 1)[1]
                    result = await client.call_tool("list_pods", {"namespace": namespace})
                    if "error" in result:
                        print(f"Error: {result['error']}")
                    else:
                        print(f"Pods in namespace '{namespace}':")
                        for pod in result.get("pods", []):
                            print(f"  - {pod['name']} ({pod['status']})")
                
                elif command.startswith("list_services "):
                    namespace = command.split(" ", 1)[1]
                    result = await client.call_tool("list_services", {"namespace": namespace})
                    if "error" in result:
                        print(f"Error: {result['error']}")
                    else:
                        print(f"Services in namespace '{namespace}':")
                        for svc in result.get("services", []):
                            print(f"  - {svc['name']} ({svc['type']})")
                
                elif command.startswith("list_routes "):
                    namespace = command.split(" ", 1)[1]
                    result = await client.call_tool("list_routes", {"namespace": namespace})
                    if "error" in result:
                        print(f"Error: {result['error']}")
                    else:
                        print(f"Routes in namespace '{namespace}':")
                        for route in result.get("routes", []):
                            print(f"  - {route['name']} -> {route['host']}")
                
                elif command.startswith("get_resource_usage "):
                    namespace = command.split(" ", 1)[1]
                    result = await client.call_tool("get_resource_usage", {"namespace": namespace})
                    if "error" in result:
                        print(f"Error: {result['error']}")
                    else:
                        usage = result.get("resource_usage", {})
                        print(f"Resource usage for namespace '{namespace}':")
                        if "total_cpu_request" in usage:
                            print(f"  CPU Request: {usage['total_cpu_request']:.2f} cores")
                        if "total_memory_request" in usage:
                            print(f"  Memory Request: {usage['total_memory_request']} bytes")
                        print(f"  Pods: {len(usage.get('pods', []))}")
                
                elif command == "help":
                    print("Available commands:")
                    print("  1. list_namespaces")
                    print("  2. list_pods <namespace>")
                    print("  3. list_services <namespace>")
                    print("  4. list_routes <namespace>")
                    print("  5. get_resource_usage <namespace>")
                    print("  6. quit")
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                
                print()
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break
    
    finally:
        await client.close()
        print("Disconnected from MCP server")

if __name__ == "__main__":
    asyncio.run(main())
