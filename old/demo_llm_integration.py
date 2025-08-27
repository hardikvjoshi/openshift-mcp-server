#!/usr/bin/env python3
"""
LLM Integration Demo for OpenShift MCP Server

This script demonstrates the enhanced capabilities of the MCP server
with LLM integration for intelligent OpenShift management.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Dict, Any, Optional

from llm_integration import llm_manager, LLMResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMIntegrationDemo:
    """Demonstrates LLM integration capabilities."""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
    
    async def start_server(self) -> bool:
        """Start the enhanced MCP server."""
        try:
            cmd = [sys.executable, "openshift_mcp_server_with_llm.py"]
            print(f"🚀 Starting Enhanced MCP Server: {' '.join(cmd)}")
            
            # Start the server process
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            if self.server_process.poll() is None:
                print("✅ Enhanced MCP Server started successfully")
                return True
            else:
                print("❌ Enhanced MCP Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server."""
        if self.server_process and self.server_process.poll() is None:
            print("🛑 Stopping Enhanced MCP Server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("✅ Enhanced MCP Server stopped")
    
    async def test_llm_integration(self):
        """Test the LLM integration capabilities."""
        print("\n" + "="*60)
        print("🧪 Testing LLM Integration")
        print("="*60)
        
        # Test available providers
        providers = llm_manager.get_available_providers()
        default = llm_manager.get_default_provider()
        
        print(f"Available LLM providers: {providers}")
        print(f"Default provider: {default}")
        
        if not providers:
            print("❌ No LLM providers configured!")
            return False
        
        # Test connections
        print("\n🔗 Testing LLM connections...")
        connection_results = await llm_manager.test_all_connections()
        for provider, status in connection_results.items():
            print(f"  {provider}: {'✅' if status else '❌'}")
        
        # Test response generation
        if default and default in providers:
            print(f"\n🤖 Testing response generation with {default}...")
            
            test_prompts = [
                "What are the best practices for managing OpenShift namespaces?",
                "How can I troubleshoot a pod that's stuck in Pending state?",
                "What are the security considerations when deploying applications to OpenShift?"
            ]
            
            for i, prompt in enumerate(test_prompts, 1):
                print(f"\n  Test {i}: {prompt[:50]}...")
                response = await llm_manager.generate_response(prompt)
                
                if response.error:
                    print(f"    ❌ Error: {response.error}")
                else:
                    print(f"    ✅ Response: {response.content[:100]}...")
                    print(f"       Provider: {response.provider}")
                    print(f"       Model: {response.model}")
                    print(f"       Response time: {response.response_time:.2f}s")
        
        return True
    
    async def demonstrate_intelligent_features(self):
        """Demonstrate intelligent OpenShift management features."""
        print("\n" + "="*60)
        print("🧠 Intelligent OpenShift Management Features")
        print("="*60)
        
        # Check if we have cluster access
        cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
        if not cluster_url:
            print("⚠️  No OpenShift cluster configured. Skipping intelligent features demo.")
            return
        
        print("🎯 Available intelligent features:")
        
        features = [
            ("ask_llm", "Ask LLM questions about OpenShift management"),
            ("intelligent_cluster_analysis", "AI-powered cluster health analysis"),
            ("get_troubleshooting_help", "AI-powered troubleshooting assistance"),
            ("get_llm_providers", "View available LLM providers"),
            ("test_llm_connection", "Test LLM provider connections")
        ]
        
        for i, (name, description) in enumerate(features, 1):
            print(f"  {i}. {name:<30} - {description}")
        
        print("\n💡 These tools allow AI assistants to:")
        print("   • Provide intelligent recommendations for cluster management")
        print("   • Analyze cluster health and suggest optimizations")
        print("   • Offer troubleshooting guidance based on your specific issues")
        print("   • Answer complex OpenShift management questions")
        print("   • Learn from your cluster context for better responses")
    
    def show_usage_instructions(self):
        """Show usage instructions for the enhanced server."""
        print("\n" + "="*60)
        print("📖 Usage Instructions")
        print("="*60)
        
        print("\n🎯 To use the Enhanced MCP Server with LLM Integration:")
        print()
        print("1. 🚀 Start the server:")
        print("   python openshift_mcp_server_with_llm.py")
        print()
        print("2. 🔗 Connect with MCP clients:")
        print("   • Claude Desktop (Settings → Model Context Protocol)")
        print("   • Custom MCP clients")
        print("   • AI assistants with MCP support")
        print()
        print("3. 🛠️  Available tools:")
        print("   • 15 OpenShift management tools")
        print("   • 5 LLM integration tools")
        print("   • Total: 20 powerful tools")
        print()
        print("4. 🤖 LLM-powered features:")
        print("   • Intelligent cluster analysis")
        print("   • AI-powered troubleshooting")
        print("   • Context-aware OpenShift guidance")
        print("   • Multi-provider LLM support")
        print()
        print("5. ⚙️  Configuration:")
        print("   • Gemini is the default LLM provider")
        print("   • Configure additional providers in .env file")
        print("   • Customize models, tokens, and temperature")
        
        print("\n🎉 The server is now ready for intelligent OpenShift management!")
    
    async def run_demo(self):
        """Run the complete LLM integration demo."""
        try:
            print("🎭 OpenShift MCP Server with LLM Integration Demo")
            print("="*60)
            
            # Test LLM integration
            llm_success = await self.test_llm_integration()
            
            if not llm_success:
                print("\n⚠️  LLM integration test failed. Please check your configuration.")
                return
            
            # Start the enhanced server
            if not await self.start_server():
                return
            
            # Demonstrate intelligent features
            await self.demonstrate_intelligent_features()
            
            # Show usage instructions
            self.show_usage_instructions()
            
            # Keep the server running
            print("\n🔄 Enhanced MCP Server is running...")
            print("Press Ctrl+C to stop the demo")
            
            while True:
                await asyncio.sleep(1)
                if self.server_process and self.server_process.poll() is not None:
                    print("❌ Server process stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Received interrupt signal")
        finally:
            self.stop_server()

async def main():
    """Main function."""
    # Check environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("❌ Error: GEMINI_API_KEY environment variable must be set")
        print("Please set it in your .env file or export it")
        print("\nExample:")
        print("export GEMINI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    print(f"🔑 Gemini API Key: {gemini_key[:10]}...")
    print()
    
    # Run the demo
    demo = LLMIntegrationDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
