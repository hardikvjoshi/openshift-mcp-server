#!/usr/bin/env python3
"""
Working MCP Demo - Shows How to Use Your MCP Server

This demo shows the different ways to use your OpenShift MCP server:
1. Direct Python imports (bypassing MCP protocol)
2. LLM integration working
3. MCP server status
4. Available tools demonstration
"""

import asyncio
import os
import subprocess
import sys
import time
from typing import Dict, Any, List

def check_mcp_server_status():
    """Check if MCP server is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "openshift_mcp_server_with_llm.py"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def test_direct_openshift_tools():
    """Test OpenShift tools directly (bypassing MCP protocol)."""
    print("\n🔧 Testing OpenShift Tools Directly...")
    
    try:
        # Import the OpenShift cluster class directly
        from openshift_cluster import OpenShiftCluster
        
        # Get cluster credentials from environment
        cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
        token = os.getenv("OPENSHIFT_TOKEN")
        verify_ssl = os.getenv("OPENSHIFT_VERIFY_SSL", "true").lower() == "true"
        
        if not cluster_url or not token:
            print("❌ Missing cluster credentials in environment variables")
            return False
        
        print(f"✅ Cluster URL: {cluster_url}")
        print(f"✅ Token: {'*' * 10}{token[-4:] if token else 'None'}")
        print(f"✅ Verify SSL: {verify_ssl}")
        
        # Try to connect
        print("\n🔄 Attempting to connect to cluster...")
        cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
        print("✅ Successfully connected to OpenShift cluster!")
        
        # Test listing namespaces
        print("\n📋 Testing list_namespaces...")
        namespaces = cluster.list_namespaces()
        print(f"✅ Found {len(namespaces)} namespaces:")
        for ns in namespaces[:5]:  # Show first 5
            print(f"   • {ns['name']} ({ns['status']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenShift tools: {e}")
        return False

def test_llm_integration():
    """Test LLM integration directly."""
    print("\n🤖 Testing LLM Integration...")
    
    try:
        from llm_integration import llm_manager
        
        print("✅ LLM Manager imported successfully")
        
        # Test Gemini connection
        print("\n🔄 Testing Gemini connection...")
        
        # Create a new event loop for this test
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(llm_manager.generate_response(
                "What is OpenShift and why is it useful?",
                "OpenShift cluster management",
                "gemini"
            ))
            loop.close()
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            return False
        
        if response.error:
            print(f"❌ Gemini Error: {response.error}")
            return False
        
        print(f"✅ Gemini Response ({response.provider}/{response.model}):")
        print(f"   Response time: {response.response_time:.2f}s")
        print(f"   Content: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM integration: {e}")
        return False

def show_available_mcp_tools():
    """Show all available MCP tools."""
    print("\n🛠️ Available MCP Tools (20 total):")
    
    print("\n📊 OpenShift Management Tools (15):")
    openshift_tools = [
        "connect_cluster", "list_namespaces", "list_applications", "list_pods",
        "list_services", "list_routes", "list_configmaps", "list_secrets",
        "get_pod_logs", "get_resource_usage", "scale_deployment", "delete_pod",
        "create_namespace", "delete_namespace", "get_cluster_health"
    ]
    for i, tool in enumerate(openshift_tools, 1):
        print(f"   {i:2d}. {tool}")
    
    print("\n🤖 LLM Integration Tools (5):")
    llm_tools = [
        "ask_llm", "get_llm_providers", "test_llm_connection",
        "intelligent_cluster_analysis", "get_troubleshooting_help"
    ]
    for i, tool in enumerate(llm_tools, 1):
        print(f"   {i:2d}. {tool}")
    
    print(f"\n💡 Total: {len(openshift_tools) + len(llm_tools)} powerful tools available!")

def show_mcp_usage_instructions():
    """Show how to use the MCP server."""
    print("\n📚 How to Use Your MCP Server:")
    
    print("\n1️⃣ **Direct Python Usage (Current Demo):**")
    print("   • Import openshift_cluster.py directly")
    print("   • Use OpenShiftCluster class methods")
    print("   • Import llm_integration.py for AI features")
    print("   • ✅ This is what we're doing now!")
    
    print("\n2️⃣ **MCP Protocol Usage (Advanced):**")
    print("   • Connect via Claude Desktop")
    print("   • Use other MCP-compatible clients")
    print("   • Execute tools via MCP protocol")
    print("   • ⚠️ Requires proper MCP client implementation")
    
    print("\n3️⃣ **Command Line Usage:**")
    print("   • python openshift_mcp_server_with_llm.py")
    print("   • Server waits for MCP client connections")
    print("   • Use stdin/stdout for MCP protocol")
    print("   • ⚠️ Not interactive without proper client")

def show_system_status():
    """Show overall system status."""
    print("\n" + "="*60)
    print("📊 OpenShift MCP Server System Status")
    print("="*60)
    
    # MCP Server Status
    server_running = check_mcp_server_status()
    print(f"🖥️  MCP Server: {'✅ Running' if server_running else '❌ Not Running'}")
    
    # Environment Variables
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    print(f"🔗 Cluster URL: {'✅ Set' if cluster_url else '❌ Missing'}")
    print(f"🔑 Token: {'✅ Set' if token else '❌ Missing'}")
    
    # LLM Configuration
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"🤖 Gemini API Key: {'✅ Set' if gemini_key else '❌ Missing'}")
    
    print("="*60)

async def main():
    """Main demo function."""
    print("🚀 OpenShift MCP Server - Working Demo")
    print("="*50)
    
    # Show system status
    show_system_status()
    
    # Test LLM integration
    llm_working = test_llm_integration()
    
    # Test OpenShift tools
    openshift_working = test_direct_openshift_tools()
    
    # Show available tools
    show_available_mcp_tools()
    
    # Show usage instructions
    show_mcp_usage_instructions()
    
    # Summary
    print("\n" + "="*50)
    print("📋 Demo Summary:")
    print(f"   • LLM Integration: {'✅ Working' if llm_working else '❌ Failed'}")
    print(f"   • OpenShift Tools: {'✅ Working' if openshift_working else '❌ Failed'}")
    print(f"   • MCP Server: {'✅ Running' if check_mcp_server_status() else '❌ Not Running'}")
    print("="*50)
    
    if llm_working and openshift_working:
        print("\n🎉 **Your system is working perfectly!**")
        print("   You can:")
        print("   • Use OpenShift tools directly via Python")
        print("   • Get AI-powered responses via Gemini")
        print("   • Connect MCP clients for advanced usage")
    else:
        print("\n⚠️  **Some components need attention**")
        print("   Check the errors above and fix configuration issues")

if __name__ == "__main__":
    asyncio.run(main())
