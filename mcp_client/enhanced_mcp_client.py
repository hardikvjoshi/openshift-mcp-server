#!/usr/bin/env python3
"""
Enhanced MCP Client for OpenShift MCP Server with LLM Integration

This client provides a clean interface to connect to the OpenShift MCP server
and execute tools for both OpenShift management and LLM-powered features.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from mcp import stdio_client, StdioServerParameters
from mcp.client import session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Standardized result from tool execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class EnhancedOpenShiftMCPClient:
    """Enhanced MCP client for OpenShift management with LLM integration."""
    
    def __init__(self, server_command: str):
        self.server_command = server_command
        self.session: Optional[session.ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            logger.info(f"Connecting to MCP server: {self.server_command}")
            
            # Parse server command into command and args
            if " " in self.server_command:
                command_parts = self.server_command.split()
                command = command_parts[0]
                args = command_parts[1:]
            else:
                command = self.server_command
                args = []
            
            # Create stdio client parameters
            params = StdioServerParameters(
                command=command,
                args=args,
                env={}
            )
            
            # Connect to the server
            async with stdio_client(params) as (read, write):
                self.session = session.ClientSession(read, write)
                
                # Initialize the session
                await self.session.initialize(
                    client_name="enhanced-openshift-mcp-client",
                    client_version="1.0.0",
                    capabilities={}
                )
                
                # Get available tools
                await self._load_tools()
                
                self.is_connected = True
                logger.info("Successfully connected to MCP server")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.is_connected = False
            return False
    
    async def _load_tools(self):
        """Load available tools from the server."""
        try:
            tools = await self.session.list_tools()
            self.available_tools = tools
            logger.info(f"Loaded {len(tools)} tools from server")
        except Exception as e:
            logger.error(f"Failed to load tools: {e}")
            self.available_tools = []
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            # Session is managed by context manager, no need to call close
            self.session = None
        self.is_connected = False
        logger.info("Disconnected from MCP server")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool on the MCP server."""
        if not self.is_connected or not self.session:
            return ToolResult(
                success=False,
                error="Not connected to MCP server"
            )
        
        start_time = time.time()
        
        try:
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            
            # Call the tool
            result = await self.session.call_tool(tool_name, arguments)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool execution failed: {e}")
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools."""
        return self.available_tools
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.get("name", "") for tool in self.available_tools if tool.get("name")]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        for tool in self.available_tools:
            if tool.get("name") == tool_name:
                return tool
        return None
    
    def categorize_tools(self) -> Dict[str, List[str]]:
        """Categorize tools by type."""
        categories = {
            "openshift": [],
            "llm": [],
            "other": []
        }
        
        for tool in self.available_tools:
            name = tool.get("name", "")
            if "llm" in name.lower() or "intelligent" in name.lower():
                categories["llm"].append(name)
            elif any(keyword in name.lower() for keyword in ["namespace", "pod", "service", "route", "cluster", "deployment"]):
                categories["openshift"].append(name)
            else:
                categories["other"].append(name)
        
        return categories
    
    async def test_connection(self) -> bool:
        """Test the connection by calling a simple tool."""
        try:
            # Try to get LLM providers as a test
            result = await self.execute_tool("get_llm_providers", {})
            return result.success
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

class OpenShiftMCPService:
    """High-level service for OpenShift management via MCP."""
    
    def __init__(self, client: EnhancedOpenShiftMCPClient):
        self.client = client
    
    async def get_cluster_info(self) -> ToolResult:
        """Get basic cluster information."""
        return await self.client.execute_tool("get_llm_providers", {})
    
    async def ask_llm(self, question: str, context: str = "", provider: str = "") -> ToolResult:
        """Ask the LLM a question about OpenShift management."""
        args = {"question": question}
        if context:
            args["context"] = context
        if provider:
            args["provider"] = provider
        
        return await self.client.execute_tool("ask_llm", args)
    
    async def analyze_cluster(self, namespace: str = "", provider: str = "") -> ToolResult:
        """Get intelligent cluster analysis."""
        args = {}
        if namespace:
            args["namespace"] = namespace
        if provider:
            args["provider"] = provider
        
        return await self.client.execute_tool("intelligent_cluster_analysis", args)
    
    async def get_troubleshooting_help(self, issue: str, error_messages: str = "", provider: str = "") -> ToolResult:
        """Get AI-powered troubleshooting help."""
        args = {"issue_description": issue}
        if error_messages:
            args["error_messages"] = error_messages
        if provider:
            args["provider"] = provider
        
        return await self.client.execute_tool("get_troubleshooting_help", args)
    
    async def list_namespaces(self) -> ToolResult:
        """List all namespaces in the cluster."""
        return await self.client.execute_tool("list_namespaces", {})
    
    async def list_pods(self, namespace: str) -> ToolResult:
        """List pods in a namespace."""
        return await self.client.execute_tool("list_pods", {"namespace": namespace})
    
    async def get_pod_logs(self, namespace: str, pod_name: str, tail_lines: int = 100) -> ToolResult:
        """Get logs from a specific pod."""
        return await self.client.execute_tool("get_pod_logs", {
            "namespace": namespace,
            "pod_name": pod_name,
            "tail_lines": tail_lines
        })

async def main():
    """Main function for testing the enhanced client."""
    # Server command - adjust path as needed
    server_command = f"{sys.executable} openshift_mcp_server_with_llm.py"
    
    # Create client
    client = EnhancedOpenShiftMCPClient(server_command)
    
    try:
        # Connect to server
        if not await client.connect():
            print("❌ Failed to connect to MCP server")
            return
        
        # Test connection
        if not await client.test_connection():
            print("❌ Connection test failed")
            return
        
        print("✅ Successfully connected to MCP server!")
        
        # Create service
        service = OpenShiftMCPService(client)
        
        # Show available tools
        tools = client.get_available_tools()
        print(f"\n🛠️  Available tools: {len(tools)}")
        
        categories = client.categorize_tools()
        for category, tool_list in categories.items():
            if tool_list:
                print(f"\n{category.upper()} Tools:")
                for tool in tool_list:
                    print(f"  • {tool}")
        
        # Test LLM integration
        print("\n🧪 Testing LLM integration...")
        
        # Test basic question
        result = await service.ask_llm(
            "What are the best practices for managing OpenShift namespaces?",
            provider="gemini"
        )
        
        if result.success:
            print(f"✅ LLM Response: {result.data.get('response', '')[:200]}...")
            print(f"   Provider: {result.data.get('provider', 'Unknown')}")
            print(f"   Model: {result.data.get('model', 'Unknown')}")
            print(f"   Response time: {result.execution_time:.2f}s")
        else:
            print(f"❌ LLM test failed: {result.error}")
        
        # Test troubleshooting
        print("\n🔧 Testing troubleshooting help...")
        result = await service.get_troubleshooting_help(
            "My pods are stuck in Pending state",
            "0/1 nodes are available: 1 node(s) had taints",
            provider="gemini"
        )
        
        if result.success:
            print(f"✅ Troubleshooting help: {result.data.get('troubleshooting_help', '')[:200]}...")
        else:
            print(f"❌ Troubleshooting test failed: {result.error}")
        
        print("\n🎉 Enhanced MCP client test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Test error: {e}")
    
    finally:
        # Disconnect
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
