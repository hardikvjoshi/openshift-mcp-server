#!/usr/bin/env python3
"""
Simple test script for the OpenShift MCP Server
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_server():
    """Test the MCP server by running it and checking its output."""
    
    # Check if environment variables are set
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    
    if not cluster_url or not token:
        print("Error: OPENSHIFT_CLUSTER_URL and OPENSHIFT_TOKEN environment variables must be set")
        return False
    
    print("Testing OpenShift MCP Server...")
    print(f"Cluster URL: {cluster_url}")
    print(f"Token: {token[:10]}...")
    print()
    
    try:
        # Start the server process
        cmd = [sys.executable, "openshift_mcp_server.py"]
        print(f"Starting server with command: {' '.join(cmd)}")
        
        # Run the server for a few seconds to see if it starts properly
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()
        )
        
        # Wait a bit for the server to start
        await asyncio.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully and is running")
            
            # Get any output
            try:
                stdout, stderr = process.communicate(timeout=2)
                if stdout:
                    print("Server stdout:", stdout)
                if stderr:
                    print("Server stderr:", stderr)
            except subprocess.TimeoutExpired:
                process.kill()
                print("Server process terminated for testing")
        else:
            # Process finished, get output
            stdout, stderr = process.communicate()
            print(f"❌ Server process exited with code {process.returncode}")
            if stdout:
                print("Server stdout:", stdout)
            if stderr:
                print("Server stderr:", stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

async def main():
    """Main function."""
    success = await test_mcp_server()
    
    if success:
        print("\n🎉 MCP Server test completed successfully!")
        print("\nTo use the server with an MCP client:")
        print("1. Start the server: python openshift_mcp_server.py")
        print("2. In another terminal, connect with an MCP client")
        print("3. The server exposes 15 OpenShift management tools")
    else:
        print("\n❌ MCP Server test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
