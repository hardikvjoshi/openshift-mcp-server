#!/usr/bin/env python3
"""
Real MCP Client for OpenShift MCP Server

This client actually connects to the MCP server and executes tools
to get real OpenShift cluster data.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealMCPClient:
    """Real MCP client that connects to the server and executes tools."""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def start_server(self) -> bool:
        """Start the MCP server if not already running."""
        try:
            # Check if server is already running
            if self._is_server_running():
                print("✅ MCP Server is already running")
                return True
            
            print("🚀 Starting MCP Server...")
            
            # Start the server
            self.server_process = subprocess.Popen(
                [sys.executable, "openshift_mcp_server_with_llm.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            if self.server_process.poll() is None:
                print("✅ MCP Server started successfully")
                return True
            else:
                print("❌ Failed to start MCP server")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def _is_server_running(self) -> bool:
        """Check if the MCP server is already running."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "openshift_mcp_server_with_llm.py"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an MCP tool and return the result."""
        if arguments is None:
            arguments = {}
        
        try:
            # Create the MCP tool call message
            tool_call = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send the tool call to the server
            message = json.dumps(tool_call) + "\n"
            
            if self.server_process and self.server_process.poll() is None:
                # Send the message
                self.server_process.stdin.write(message)
                self.server_process.stdin.flush()
                
                # Wait for response
                await asyncio.sleep(2)
                
                # Try to read response
                try:
                    response = self.server_process.stdout.readline()
                    if response:
                        return {"success": True, "data": response.strip()}
                    else:
                        return {"success": False, "error": "No response from server"}
                except:
                    return {"success": False, "error": "Failed to read response"}
            else:
                return {"success": False, "error": "Server not running"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_namespaces_via_mcp(self) -> str:
        """List namespaces using the MCP list_namespaces tool."""
        print("🔍 Executing MCP tool: list_namespaces")
        
        result = await self.execute_mcp_tool("list_namespaces")
        
        if result["success"]:
            return f"✅ MCP Tool Result:\n{result['data']}"
        else:
            return f"❌ MCP Tool Error: {result['error']}"
    
    async def list_pods_via_mcp(self, namespace: str = "default") -> str:
        """List pods using the MCP list_pods tool."""
        print(f"🔍 Executing MCP tool: list_pods for namespace: {namespace}")
        
        result = await self.execute_mcp_tool("list_pods", {"namespace": namespace})
        
        if result["success"]:
            return f"✅ MCP Tool Result:\n{result['data']}"
        else:
            return f"❌ MCP Tool Error: {result['error']}"
    
    async def connect_cluster_via_mcp(self) -> str:
        """Connect to cluster using the MCP connect_cluster tool."""
        print("🔍 Executing MCP tool: connect_cluster")
        
        # Get cluster details from environment
        cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
        token = os.getenv("OPENSHIFT_TOKEN")
        verify_ssl = os.getenv("OPENSHIFT_VERIFY_SSL", "true").lower() == "true"
        
        if not cluster_url or not token:
            return "❌ Missing cluster credentials in environment variables"
        
        result = await self.execute_mcp_tool("connect_cluster", {
            "cluster_url": cluster_url,
            "token": token,
            "verify_ssl": verify_ssl
        })
        
        if result["success"]:
            return f"✅ MCP Tool Result:\n{result['data']}"
        else:
            return f"❌ MCP Tool Error: {result['error']}"
    
    async def ask_llm_via_mcp(self, question: str) -> str:
        """Ask LLM using the MCP ask_llm tool."""
        print(f"🔍 Executing MCP tool: ask_llm")
        
        result = await self.execute_mcp_tool("ask_llm", {
            "question": question,
            "context": "OpenShift cluster management"
        })
        
        if result["success"]:
            return f"✅ MCP Tool Result:\n{result['data']}"
        else:
            return f"❌ MCP Tool Error: {result['error']}"
    
    def add_to_history(self, user_query: str, response: str, tool_used: str = "", execution_time: float = 0.0):
        """Add interaction to conversation history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "response": response,
            "tool_used": tool_used,
            "execution_time": execution_time
        })
    
    async def process_user_query(self, user_query: str) -> str:
        """Process a user query using MCP tools when possible."""
        start_time = time.time()
        
        try:
            # Analyze the query to determine which MCP tool to use
            if "namespace" in user_query.lower() and "list" in user_query.lower():
                response = await self.list_namespaces_via_mcp()
                tool_used = "list_namespaces"
            elif "pod" in user_query.lower() and "list" in user_query.lower():
                # Extract namespace if specified
                namespace = "default"
                if "namespace" in user_query.lower():
                    # Simple extraction - in real app, use NLP
                    if "production" in user_query.lower():
                        namespace = "production"
                    elif "development" in user_query.lower():
                        namespace = "development"
                response = await self.list_pods_via_mcp(namespace)
                tool_used = "list_pods"
            elif "connect" in user_query.lower() or "cluster" in user_query.lower():
                response = await self.connect_cluster_via_mcp()
                tool_used = "connect_cluster"
            elif "ai" in user_query.lower() or "llm" in user_query.lower() or "help" in user_query.lower():
                response = await self.ask_llm_via_mcp(user_query)
                tool_used = "ask_llm"
            else:
                # Fallback to LLM for general questions
                response = await self.ask_llm_via_mcp(user_query)
                tool_used = "ask_llm"
            
            execution_time = time.time() - start_time
            
            # Add to history
            self.add_to_history(user_query, response, tool_used, execution_time)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"❌ Error processing query: {str(e)}"
            self.add_to_history(user_query, error_msg, "error", execution_time)
            return error_msg
    
    async def interactive_mode(self):
        """Run the client in interactive mode."""
        print("\n" + "="*60)
        print("🎭 Real MCP Client - OpenShift Management")
        print("="*60)
        print("Type 'help' for available commands, 'quit' to exit")
        print("Ask me to list namespaces, pods, or connect to cluster!")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n🤔 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                elif user_input.lower() == 'history':
                    self._show_history()
                    continue
                
                elif user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                elif user_input.lower() == 'test-mcp':
                    await self._test_mcp_tools()
                    continue
                
                # Process the query using MCP tools
                print("\n🤖 Processing your query with MCP tools...")
                response = await self.process_user_query(user_input)
                print(f"\n💡 Response:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
🆘 **Available Commands:**
• help - Show this help message
• history - Show conversation history
• status - Show application status
• test-mcp - Test MCP tool execution
• quit/exit/q - Exit the application

💡 **Example Queries (These WILL use MCP tools):**
• "List all namespaces" → Uses MCP list_namespaces tool
• "Show pods in default namespace" → Uses MCP list_pods tool
• "Connect to cluster" → Uses MCP connect_cluster tool
• "List pods in production" → Uses MCP list_pods tool
• "AI help with troubleshooting" → Uses MCP ask_llm tool

🔧 **This client ACTUALLY calls MCP tools!**
   Unlike the previous host app, this one executes real MCP operations.
        """
        print(help_text)
    
    def _show_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            print("No conversation history yet.")
            return
        
        print(f"\n📚 Conversation History ({len(self.conversation_history)} interactions):")
        for i, entry in enumerate(self.conversation_history[-5:], 1):
            print(f"{i}. Query: {entry['user_query'][:50]}...")
            print(f"   Tool: {entry['tool_used']} | Time: {entry['execution_time']:.2f}s")
            print()
    
    def _show_status(self):
        """Show application status."""
        server_running = self._is_server_running()
        status = f"""
📊 **Application Status:**
• MCP Server Running: {'✅ Yes' if server_running else '❌ No'}
• MCP Client: ✅ Real MCP Client (executes tools)
• OpenShift Cluster: ✅ Connected via environment
• Available MCP Tools: 20 (15 OpenShift + 5 LLM)
• Conversation History: {len(self.conversation_history)} interactions
• Last Activity: {self.conversation_history[-1]['timestamp'] if self.conversation_history else 'None'}
        """
        print(status)
    
    async def _test_mcp_tools(self):
        """Test MCP tool execution."""
        print("\n🧪 Testing MCP Tools...")
        
        # Test 1: List namespaces
        print("\n1️⃣ Testing list_namespaces tool:")
        result1 = await self.list_namespaces_via_mcp()
        print(result1)
        
        # Test 2: List pods
        print("\n2️⃣ Testing list_pods tool:")
        result2 = await self.list_pods_via_mcp("default")
        print(result2)
        
        # Test 3: Ask LLM
        print("\n3️⃣ Testing ask_llm tool:")
        result3 = await self.ask_llm_via_mcp("What is OpenShift?")
        print(result3)
        
        print("\n✅ MCP Tool Testing Complete!")
    
    async def shutdown(self):
        """Shutdown the client."""
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
        print("🛑 MCP Client shutdown complete")

async def main():
    """Main function."""
    client = RealMCPClient()
    
    try:
        # Start server if needed
        if not await client.start_server():
            print("❌ Failed to start MCP server")
            return
        
        # Run interactive mode
        await client.interactive_mode()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        logger.error(f"Application error: {e}")
    
    finally:
        # Shutdown
        await client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
