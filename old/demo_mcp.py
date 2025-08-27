#!/usr/bin/env python3
"""
OpenShift MCP Server Demo

This script demonstrates how to use the OpenShift MCP server.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMCPDemo:
    """Simple demonstration of MCP server functionality."""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
    
    async def start_server(self) -> bool:
        """Start the MCP server."""
        try:
            cmd = [sys.executable, "openshift_mcp_server.py"]
            print(f"Starting MCP server: {' '.join(cmd)}")
            
            # Start the server process
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            # Wait for server to start
            await asyncio.sleep(2)
            
            if self.server_process.poll() is None:
                print("✅ MCP Server started successfully")
                return True
            else:
                print("❌ MCP Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server."""
        if self.server_process and self.server_process.poll() is None:
            print("Stopping MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("MCP Server stopped")
    
    def show_server_info(self):
        """Show information about the MCP server."""
        print("\n" + "="*60)
        print("🚀 OpenShift MCP Server Demo")
        print("="*60)
        print()
        print("The MCP server provides the following OpenShift tools:")
        print()
        
        tools = [
            ("connect_cluster", "Connect to OpenShift cluster"),
            ("list_namespaces", "List all namespaces/projects"),
            ("list_applications", "List applications in a namespace"),
            ("list_pods", "List pods in a namespace"),
            ("list_services", "List services in a namespace"),
            ("list_routes", "List routes in a namespace"),
            ("list_configmaps", "List configmaps in a namespace"),
            ("list_secrets", "List secrets in a namespace"),
            ("get_pod_logs", "Get logs from a specific pod"),
            ("get_resource_usage", "Get resource usage for a namespace"),
            ("scale_deployment", "Scale a deployment"),
            ("delete_pod", "Delete a specific pod"),
            ("create_namespace", "Create a new namespace"),
            ("delete_namespace", "Delete a namespace")
        ]
        
        for i, (name, description) in enumerate(tools, 1):
            print(f"{i:2d}. {name:<20} - {description}")
        
        print()
        print("The server is now running and ready to accept MCP client connections.")
        print()
        print("To connect with an MCP client:")
        print("1. Use an MCP-compatible client (like Claude Desktop, etc.)")
        print("2. Connect to: openshift_mcp_server.py")
        print("3. The server will auto-connect to your OpenShift cluster")
        print("4. You can then use any of the tools listed above")
        print()
        print("Press Ctrl+C to stop the server")
        print("="*60)
    
    async def run_demo(self):
        """Run the MCP server demo."""
        try:
            # Start the server
            if not await self.start_server():
                return
            
            # Show server information
            self.show_server_info()
            
            # Keep the server running
            while True:
                await asyncio.sleep(1)
                if self.server_process and self.server_process.poll() is not None:
                    print("❌ Server process stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal")
        finally:
            self.stop_server()

async def main():
    """Main function."""
    # Check environment variables
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    
    if not cluster_url or not token:
        print("Error: OPENSHIFT_CLUSTER_URL and OPENSHIFT_TOKEN environment variables must be set")
        print("Please set them in your .env file or export them")
        sys.exit(1)
    
    print(f"OpenShift Cluster: {cluster_url}")
    print(f"Token: {token[:10]}...")
    print()
    
    # Run the demo
    demo = SimpleMCPDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
