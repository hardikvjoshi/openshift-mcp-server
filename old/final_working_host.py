#!/usr/bin/env python3
"""
Final Working Host Application for OpenShift MCP Server

This host application provides a working interface that can:
1. Execute OpenShift tools directly
2. Use LLM integration
3. Provide intelligent responses
4. Track conversation history
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalWorkingHost:
    """Final working host application for OpenShift management."""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.cluster = None
        self.llm_manager = None
    
    async def initialize(self) -> bool:
        """Initialize the host application."""
        try:
            print("🚀 Initializing Final Working Host...")
            
            # Initialize OpenShift cluster connection
            if await self._initialize_openshift():
                print("✅ OpenShift cluster connected")
            else:
                print("❌ Failed to connect to OpenShift cluster")
            
            # Initialize LLM integration
            if await self._initialize_llm():
                print("✅ LLM integration ready")
            else:
                print("❌ Failed to initialize LLM integration")
            
            print("✅ Host application initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing host: {e}")
            return False
    
    async def _initialize_openshift(self) -> bool:
        """Initialize OpenShift cluster connection."""
        try:
            from openshift_cluster import OpenShiftCluster
            
            # Get cluster credentials from environment
            cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
            token = os.getenv("OPENSHIFT_TOKEN")
            verify_ssl = os.getenv("OPENSHIFT_VERIFY_SSL", "true").lower() == "true"
            
            if not cluster_url or not token:
                print("⚠️  Missing cluster credentials")
                return False
            
            # Connect to cluster
            self.cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
            return True
            
        except Exception as e:
            print(f"❌ OpenShift initialization error: {e}")
            return False
    
    async def _initialize_llm(self) -> bool:
        """Initialize LLM integration."""
        try:
            from llm_integration import llm_manager
            self.llm_manager = llm_manager
            return True
        except Exception as e:
            print(f"❌ LLM initialization error: {e}")
            return False
    
    def add_to_history(self, user_query: str, response: str, tool_used: str = "", execution_time: float = 0.0):
        """Add interaction to conversation history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "response": response,
            "tool_used": tool_used,
            "execution_time": execution_time
        })
    
    async def execute_list_namespaces(self) -> str:
        """Execute list_namespaces tool."""
        try:
            if not self.cluster:
                return "❌ OpenShift cluster not connected"
            
            print("🔍 Executing: list_namespaces")
            namespaces = self.cluster.list_namespaces()
            
            # Format the response
            result = {
                "tool": "list_namespaces",
                "namespaces_found": len(namespaces),
                "namespaces": []
            }
            
            for ns in namespaces:
                result["namespaces"].append({
                    "name": ns.get("name", "Unknown"),
                    "status": ns.get("status", "Unknown"),
                    "display_name": ns.get("display_name", ns.get("name", "Unknown")),
                    "description": ns.get("description", "")
                })
            
            return f"✅ **list_namespaces Result:**\n{json.dumps(result, indent=2)}"
            
        except Exception as e:
            return f"❌ Error executing list_namespaces: {str(e)}"
    
    async def execute_list_pods(self, namespace: str = "default") -> str:
        """Execute list_pods tool."""
        try:
            if not self.cluster:
                return "❌ OpenShift cluster not connected"
            
            print(f"🔍 Executing: list_pods for namespace '{namespace}'")
            pods = self.cluster.list_pods(namespace)
            
            # Format the response
            result = {
                "tool": "list_pods",
                "namespace": namespace,
                "pods_found": len(pods),
                "pods": []
            }
            
            for pod in pods:
                result["pods"].append({
                    "name": pod.get("name", "Unknown"),
                    "status": pod.get("status", "Unknown"),
                    "ready": pod.get("ready", "Unknown"),
                    "restarts": pod.get("restarts", 0),
                    "age": pod.get("age", "Unknown")
                })
            
            return f"✅ **list_pods Result:**\n{json.dumps(result, indent=2)}"
            
        except Exception as e:
            return f"❌ Error executing list_pods: {str(e)}"
    
    async def execute_ask_llm(self, question: str) -> str:
        """Execute ask_llm tool."""
        try:
            if not self.llm_manager:
                return "❌ LLM integration not available"
            
            print(f"🔍 Executing: ask_llm")
            
            # Use asyncio.create_task for proper async handling
            try:
                response = await self.llm_manager.generate_response(
                    question,
                    "OpenShift cluster management",
                    "gemini"
                )
            except Exception as e:
                return f"❌ LLM Error: {e}"
            
            if response.error:
                return f"❌ LLM Error: {response.error}"
            
            result = {
                "tool": "ask_llm",
                "provider": response.provider,
                "model": response.model,
                "response_time": f"{response.response_time:.2f}s",
                "content": response.content
            }
            
            return f"✅ **ask_llm Result:**\n{json.dumps(result, indent=2)}"
            
        except Exception as e:
            return f"❌ Error executing ask_llm: {str(e)}"
    
    async def process_user_query(self, user_query: str) -> str:
        """Process a user query using available tools."""
        start_time = time.time()
        
        try:
            # Analyze the query to determine which tool to use
            if "namespace" in user_query.lower() and "list" in user_query.lower():
                response = await self.execute_list_namespaces()
                tool_used = "list_namespaces"
            elif "pod" in user_query.lower() and "list" in user_query.lower():
                namespace = "default"
                if "namespace" in user_query.lower():
                    if "production" in user_query.lower():
                        namespace = "production"
                    elif "development" in user_query.lower():
                        namespace = "development"
                response = await self.execute_list_pods(namespace)
                tool_used = "list_pods"
            elif "ai" in user_query.lower() or "llm" in user_query.lower() or "help" in user_query.lower():
                response = await self.execute_ask_llm(user_query)
                tool_used = "ask_llm"
            else:
                # Fallback to LLM for general questions
                response = await self.execute_ask_llm(user_query)
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
    
    async def test_tools(self):
        """Test all available tools."""
        print("\n🧪 Testing Available Tools...")
        
        # Test 1: List namespaces
        print("\n1️⃣ Testing list_namespaces tool:")
        result1 = await self.execute_list_namespaces()
        print(result1)
        
        # Test 2: List pods
        print("\n2️⃣ Testing list_pods tool:")
        result2 = await self.execute_list_pods("default")
        print(result2)
        
        # Test 3: Ask LLM
        print("\n3️⃣ Testing ask_llm tool:")
        result3 = await self.execute_ask_llm("What is OpenShift?")
        print(result3)
        
        print("\n✅ Tool Testing Complete!")
    
    async def interactive_mode(self):
        """Run the host application in interactive mode."""
        print("\n" + "="*60)
        print("🎭 Final Working Host - OpenShift Management")
        print("="*60)
        print("Type 'help' for available commands, 'quit' to exit")
        print("This host ACTUALLY executes OpenShift tools!")
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
                
                elif user_input.lower() == 'test-tools':
                    await self.test_tools()
                    continue
                
                # Process the query
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
• test-tools - Test all available tools
• quit/exit/q - Exit the application

💡 **Example Queries (These WILL execute tools):**
• "List all namespaces" → Uses list_namespaces tool
• "Show pods in default namespace" → Uses list_pods tool
• "List pods in production" → Uses list_pods tool
• "AI help with troubleshooting" → Uses ask_llm tool

🔧 **This host ACTUALLY executes OpenShift tools!**
   It provides real cluster data and AI-powered responses.
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
        status = f"""
📊 **Application Status:**
• OpenShift Cluster: {'✅ Connected' if self.cluster else '❌ Not Connected'}
• LLM Integration: {'✅ Ready' if self.llm_manager else '❌ Not Available'}
• Host Application: ✅ Final Working Host
• Available Tools: 3 (list_namespaces, list_pods, ask_llm)
• Conversation History: {len(self.conversation_history)} interactions
• Last Activity: {self.conversation_history[-1]['timestamp'] if self.conversation_history else 'None'}
        """
        print(status)

async def main():
    """Main function."""
    host = FinalWorkingHost()
    
    try:
        # Initialize the host
        if not await host.initialize():
            print("❌ Failed to initialize host application")
            return
        
        # Run interactive mode
        await host.interactive_mode()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
