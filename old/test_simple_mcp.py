#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""

import asyncio
import subprocess
import sys
import time

async def test_mcp_server():
    """Test the MCP server with a simple subprocess approach."""
    
    print("🧪 Testing MCP Server...")
    
    # Start the server as a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "openshift_mcp_server_with_llm.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait a moment for server to start
        await asyncio.sleep(2)
        
        # Check if process is still running
        if server_process.poll() is None:
            print("✅ MCP Server is running")
            
            # Send a simple test message (this won't work with MCP protocol, but tests if server stays alive)
            print("📡 Server process status:", server_process.poll())
            
            # Wait a bit more
            await asyncio.sleep(3)
            
            if server_process.poll() is None:
                print("✅ MCP Server is stable and ready for connections")
            else:
                print("❌ MCP Server exited unexpectedly")
                stdout, stderr = server_process.communicate()
                print("STDOUT:", stdout)
                print("STDERR:", stderr)
        else:
            print("❌ MCP Server failed to start")
            stdout, stderr = server_process.communicate()
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
    
    finally:
        # Clean up
        if server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        print("🛑 Server process terminated")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
