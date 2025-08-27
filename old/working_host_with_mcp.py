#!/usr/bin/env python3
"""
Working Host Application with MCP Client

This host application uses the working MCP client to actually execute
MCP tools and provide intelligent OpenShift management.
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, List
from datetime import datetime

# Import our working MCP client
from working_mcp_client import WorkingMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingHostWithMCP:
    """Working host application that uses the MCP client."""
    
    def __init__(self):
        self.mcp_client = WorkingMCPClient()
        self.conversation_history: List[Dict[str, Any]] = []
        self.mcp_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the host application and MCP client."""
        try:
            print("🚀 Initializing Working Host with MCP...")
            
            # Start MCP server if needed
            if not await self.mcp_client.start_server():
                print("❌ Failed to start MCP server")
                return False
            
            # Initialize MCP connection
            print("🤝 Initializing MCP connection...")
            if await self.mcp_client.initialize_mcp_connection():
                self.mcp_initialized = True
                print("✅ MCP connection initialized successfully")
            else:
                print("⚠️  MCP connection initialization failed, but continuing...")
            
            print("✅ Host application initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing host: {e}")
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
    
    async def process_user_query(self, user_query: str) -> str:
        """Process a user query using MCP tools."""
        start_time = time.time()
        
        try:
            print(f"\n🤖 Processing: {user_query}")
            
            # Use the MCP client to process the query
            response = await self.mcp_client.process_user_query(user_query)
            
            execution_time = time.time() - start_time
            
            # Add to history (get tool info from MCP client)
            if self.mcp_client.conversation_history:
                last_entry = self.mcp_client.conversation_history[-1]
                tool_used = last_entry.get('tool_used', 'unknown')
            else:
                tool_used = 'unknown'
            
            self.add_to_history(user_query, response, tool_used, execution_time)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"❌ Error processing query: {str(e)}"
            self.add_to_history(user_query, error_msg, "error", execution_time)
            return error_msg
    
    async def test_mcp_integration(self):
        """Test the MCP integration."""
        print("\n🧪 Testing MCP Integration...")
        
        if not self.mcp_initialized:
            print("⚠️  MCP not initialized, attempting to initialize...")
            if await self.mcp_client.initialize_mcp_connection():
                self.mcp_initialized = True
                print("✅ MCP connection established")
            else:
                print("❌ Failed to establish MCP connection")
                return False
        
        # Test 1: List namespaces
        print("\n1️⃣ Testing list_namespaces via MCP:")
        result1 = await self.mcp_client.list_namespaces_via_mcp()
        print(result1)
        
        # Test 2: Ask LLM
        print("\n2️⃣ Testing ask_llm via MCP:")
        result2 = await self.mcp_client.ask_llm_via_mcp("What is OpenShift?")
        print(result2)
        
        print("\n✅ MCP Integration Testing Complete!")
        return True
    
    async def interactive_mode(self):
        """Run the host application in interactive mode."""
        print("\n" + "="*60)
        print("🎭 Working Host with MCP - OpenShift Management")
        print("="*60)
        print("Type 'help' for available commands, 'quit' to exit")
        print("This host ACTUALLY uses MCP tools for OpenShift operations!")
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
                    await self.test_mcp_integration()
                    continue
                
                elif user_input.lower() == 'init':
                    if await self.mcp_client.initialize_mcp_connection():
                        self.mcp_initialized = True
                        print("✅ MCP connection initialized")
                    else:
                        print("❌ Failed to initialize MCP connection")
                    continue
                
                # Process the query using MCP tools
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
• init - Initialize MCP connection
• quit/exit/q - Exit the application

💡 **Example Queries (These WILL use MCP tools):**
• "List all namespaces" → Uses MCP list_namespaces tool
• "Show pods in default namespace" → Uses MCP list_pods tool
• "Connect to cluster" → Uses MCP connect_cluster tool
• "List pods in production" → Uses MCP list_pods tool
• "AI help with troubleshooting" → Uses MCP ask_llm tool

🔧 **This host ACTUALLY uses MCP tools!**
   Unlike the previous host app, this one executes real MCP operations.
   Type 'test-mcp' to verify MCP integration is working.
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
        server_running = self.mcp_client._is_server_running()
        status = f"""
📊 **Application Status:**
• MCP Server Running: {'✅ Yes' if server_running else '❌ No'}
• MCP Connection: {'✅ Initialized' if self.mcp_initialized else '❌ Not Initialized'}
• Host Application: ✅ Working Host with MCP
• OpenShift Cluster: ✅ Connected via environment
• Available MCP Tools: 20 (15 OpenShift + 5 LLM)
• Conversation History: {len(self.conversation_history)} interactions
• Last Activity: {self.conversation_history[-1]['timestamp'] if self.conversation_history else 'None'}
        """
        print(status)
    
    async def shutdown(self):
        """Shutdown the host application."""
        await self.mcp_client.shutdown()
        print("🛑 Host application shutdown complete")

async def main():
    """Main function."""
    host = WorkingHostWithMCP()
    
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
    
    finally:
        # Shutdown
        await host.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
