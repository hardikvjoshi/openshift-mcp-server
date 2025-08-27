#!/usr/bin/env python3
"""
Demo Script for OpenShift Host Test Application

This script demonstrates how the host application processes user queries
and provides intelligent responses using the MCP client.
"""

import asyncio
import sys
from enhanced_mcp_client import EnhancedOpenShiftMCPClient, OpenShiftMCPService

async def demo_host_app():
    """Demonstrate the host application capabilities."""
    
    print("🎭 OpenShift Host Application Demo")
    print("="*50)
    
    # Server command
    server_command = f"{sys.executable} openshift_mcp_server_with_llm.py"
    
    # Create client
    client = EnhancedOpenShiftMCPClient(server_command)
    
    try:
        # Connect to server
        print("🔗 Connecting to MCP server...")
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
        
        # Demo queries
        demo_queries = [
            "What are the best practices for managing OpenShift namespaces?",
            "How do I troubleshoot pods stuck in Pending state?",
            "Analyze my cluster health",
            "List all namespaces",
            "Show pods in the default namespace"
        ]
        
        print(f"\n🧪 Running {len(demo_queries)} demo queries...")
        print("-" * 50)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("🤖 Processing...")
            
            # Process the query
            if "analyze" in query.lower():
                result = await service.analyze_cluster(provider="gemini")
            elif "troubleshoot" in query.lower() or "pending" in query.lower():
                result = await service.get_troubleshooting_help(
                    "My pods are stuck in Pending state",
                    "0/1 nodes are available: 1 node(s) had taints",
                    provider="gemini"
                )
            elif "best practice" in query.lower() or "how" in query.lower():
                result = await service.ask_llm(query, provider="gemini")
            elif "namespace" in query.lower() and "list" in query.lower():
                result = await service.list_namespaces()
            elif "pod" in query.lower() and "show" in query.lower():
                result = await service.list_pods("default")
            else:
                result = await service.ask_llm(query, provider="gemini")
            
            # Display result
            if result.success:
                if "analysis" in result.data:
                    print(f"✅ Analysis: {result.data['analysis'][:150]}...")
                elif "troubleshooting_help" in result.data:
                    print(f"✅ Troubleshooting: {result.data['troubleshooting_help'][:150]}...")
                elif "response" in result.data:
                    print(f"✅ Response: {result.data['response'][:150]}...")
                elif "namespaces" in result.data:
                    namespaces = result.data['namespaces']
                    print(f"✅ Namespaces: {len(namespaces)} found")
                elif "pods" in result.data:
                    pods = result.data['pods']
                    print(f"✅ Pods: {len(pods)} found")
                else:
                    print(f"✅ Result: {str(result.data)[:150]}...")
                
                print(f"   Time: {result.execution_time:.2f}s")
            else:
                print(f"❌ Error: {result.error}")
            
            print("-" * 30)
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    finally:
        # Disconnect
        await client.disconnect()

async def demo_simple_queries():
    """Demo with simple, focused queries."""
    
    print("\n🔬 Simple Query Demo")
    print("="*30)
    
    server_command = f"{sys.executable} openshift_mcp_server_with_llm.py"
    client = EnhancedOpenShiftMCPClient(server_command)
    
    try:
        if not await client.connect():
            print("❌ Connection failed")
            return
        
        service = OpenShiftMCPService(client)
        
        # Simple LLM query
        print("\n1. Simple LLM Query:")
        result = await service.ask_llm("What is OpenShift?", provider="gemini")
        if result.success:
            print(f"✅ {result.data['response'][:100]}...")
        else:
            print(f"❌ {result.error}")
        
        # Get LLM providers
        print("\n2. Get LLM Providers:")
        result = await service.get_cluster_info()
        if result.success:
            providers = result.data.get('available_providers', [])
            default = result.data.get('default_provider', 'Unknown')
            print(f"✅ Available: {providers}, Default: {default}")
        else:
            print(f"❌ {result.error}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.disconnect()

async def main():
    """Main demo function."""
    print("🚀 Starting OpenShift Host Application Demos...")
    
    # Run main demo
    await demo_host_app()
    
    # Run simple demo
    await demo_simple_queries()
    
    print("\n🎭 All demos completed!")
    print("\n💡 To run the interactive host application:")
    print("   python host_test_app.py")

if __name__ == "__main__":
    asyncio.run(main())
