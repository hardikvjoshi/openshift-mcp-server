#!/usr/bin/env python3
"""
Host Test Application for OpenShift MCP Server

This application demonstrates how to use the MCP client to provide
intelligent OpenShift management responses to user queries.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from enhanced_mcp_client import EnhancedOpenShiftMCPClient, OpenShiftMCPService, ToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenShiftHostApp:
    """Host application that provides intelligent OpenShift management responses."""
    
    def __init__(self):
        self.client: Optional[EnhancedOpenShiftMCPClient] = None
        self.service: Optional[OpenShiftMCPService] = None
        self.is_connected = False
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """Initialize the host application and connect to MCP server."""
        try:
            print("🚀 Initializing OpenShift Host Application...")
            
            # Server command
            server_command = f"{sys.executable} openshift_mcp_server_with_llm.py"
            
            # Create and connect client
            self.client = EnhancedOpenShiftMCPClient(server_command)
            
            if not await self.client.connect():
                print("❌ Failed to connect to MCP server")
                return False
            
            # Test connection
            if not await self.client.test_connection():
                print("❌ Connection test failed")
                return False
            
            # Create service
            self.service = OpenShiftMCPService(self.client)
            self.is_connected = True
            
            print("✅ Successfully connected to OpenShift MCP Server!")
            print(f"🛠️  Available tools: {len(self.client.get_available_tools())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            logger.error(f"Initialization error: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the host application."""
        if self.client:
            await self.client.disconnect()
        self.is_connected = False
        print("🛑 Host application shutdown complete")
    
    def add_to_history(self, user_query: str, response: str, tool_used: str = "", execution_time: float = 0.0):
        """Add interaction to conversation history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "response": response,
            "tool_used": tool_used,
            "execution_time": execution_time
        })
    
    def get_history_summary(self) -> str:
        """Get a summary of conversation history."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        summary = f"Conversation History ({len(self.conversation_history)} interactions):\n"
        for i, entry in enumerate(self.conversation_history[-5:], 1):  # Last 5 interactions
            summary += f"{i}. {entry['user_query'][:50]}...\n"
            summary += f"   Tool: {entry['tool_used']} | Time: {entry['execution_time']:.2f}s\n"
        
        return summary
    
    async def process_user_query(self, user_query: str) -> str:
        """Process a user query and return an intelligent response."""
        if not self.is_connected or not self.service:
            return "❌ Not connected to MCP server. Please initialize the application first."
        
        start_time = time.time()
        
        try:
            # Analyze the query to determine the best tool to use
            tool_to_use, args = self._analyze_query(user_query)
            
            if not tool_to_use:
                return "I'm not sure how to help with that query. Please try asking about OpenShift management, cluster analysis, or troubleshooting."
            
            # Execute the appropriate tool
            result = await self._execute_tool(tool_to_use, args)
            
            execution_time = time.time() - start_time
            
            # Format the response
            response = self._format_response(result, user_query, tool_to_use)
            
            # Add to history
            self.add_to_history(user_query, response, tool_to_use, execution_time)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"❌ Error processing query: {str(e)}"
            self.add_to_history(user_query, error_msg, "error", execution_time)
            return error_msg
    
    def _analyze_query(self, query: str) -> tuple[Optional[str], Dict[str, Any]]:
        """Analyze user query to determine the best tool to use."""
        query_lower = query.lower()
        
        # LLM-powered tools
        if any(keyword in query_lower for keyword in ["analyze", "analysis", "health", "recommendation"]):
            return "intelligent_cluster_analysis", {}
        
        if any(keyword in query_lower for keyword in ["troubleshoot", "problem", "issue", "error", "help", "fix"]):
            return "get_troubleshooting_help", {"issue_description": query}
        
        if any(keyword in query_lower for keyword in ["what", "how", "why", "explain", "best practice", "guide"]):
            return "ask_llm", {"question": query}
        
        # OpenShift management tools
        if any(keyword in query_lower for keyword in ["namespace", "namespaces"]):
            return "list_namespaces", {}
        
        if any(keyword in query_lower for keyword in ["pod", "pods"]):
            # Try to extract namespace from query
            namespace = self._extract_namespace(query)
            return "list_pods", {"namespace": namespace} if namespace else {}
        
        if any(keyword in query_lower for keyword in ["log", "logs"]):
            # Try to extract pod info from query
            namespace, pod_name = self._extract_pod_info(query)
            if namespace and pod_name:
                return "get_pod_logs", {"namespace": namespace, "pod_name": pod_name, "tail_lines": 100}
        
        # Default to asking LLM
        return "ask_llm", {"question": query}
    
    def _extract_namespace(self, query: str) -> Optional[str]:
        """Extract namespace from query if mentioned."""
        # Simple extraction - could be enhanced with NLP
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["namespace", "in", "from"] and i + 1 < len(words):
                return words[i + 1]
        return None
    
    def _extract_pod_info(self, query: str) -> tuple[Optional[str], Optional[str]]:
        """Extract namespace and pod name from query if mentioned."""
        # Simple extraction - could be enhanced with NLP
        words = query.split()
        namespace = None
        pod_name = None
        
        for i, word in enumerate(words):
            if word.lower() == "namespace" and i + 1 < len(words):
                namespace = words[i + 1]
            elif word.lower() == "pod" and i + 1 < len(words):
                pod_name = words[i + 1]
        
        return namespace, pod_name
    
    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> ToolResult:
        """Execute the specified tool with arguments."""
        if tool_name == "intelligent_cluster_analysis":
            return await self.service.analyze_cluster(
                namespace=args.get("namespace", ""),
                provider=args.get("provider", "gemini")
            )
        elif tool_name == "get_troubleshooting_help":
            return await self.service.get_troubleshooting_help(
                issue=args.get("issue_description", ""),
                error_messages=args.get("error_messages", ""),
                provider=args.get("provider", "gemini")
            )
        elif tool_name == "ask_llm":
            return await self.service.ask_llm(
                question=args.get("question", ""),
                context=args.get("context", ""),
                provider=args.get("provider", "gemini")
            )
        elif tool_name == "list_namespaces":
            return await self.service.list_namespaces()
        elif tool_name == "list_pods":
            return await self.service.list_pods(args.get("namespace", ""))
        elif tool_name == "get_pod_logs":
            return await self.service.get_pod_logs(
                namespace=args.get("namespace", ""),
                pod_name=args.get("pod_name", ""),
                tail_lines=args.get("tail_lines", 100)
            )
        else:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")
    
    def _format_response(self, result: ToolResult, user_query: str, tool_used: str) -> str:
        """Format the tool result into a user-friendly response."""
        if not result.success:
            return f"❌ Error: {result.error}"
        
        # Format based on tool type
        if tool_used == "intelligent_cluster_analysis":
            analysis = result.data.get("analysis", "")
            provider = result.data.get("provider", "Unknown")
            model = result.data.get("model", "Unknown")
            
            return f"""🧠 **Intelligent Cluster Analysis** (via {provider}/{model})

{analysis}

*Analysis completed in {result.execution_time:.2f} seconds*"""
        
        elif tool_used == "get_troubleshooting_help":
            help_text = result.data.get("troubleshooting_help", "")
            provider = result.data.get("provider", "Unknown")
            model = result.data.get("model", "Unknown")
            
            return f"""🔧 **AI-Powered Troubleshooting Help** (via {provider}/{model})

{help_text}

*Troubleshooting completed in {result.execution_time:.2f} seconds*"""
        
        elif tool_used == "ask_llm":
            response = result.data.get("response", "")
            provider = result.data.get("provider", "Unknown")
            model = result.data.get("model", "Unknown")
            
            return f"""🤖 **AI Response** (via {provider}/{model})

{response}

*Response generated in {result.execution_time:.2f} seconds*"""
        
        elif tool_used == "list_namespaces":
            namespaces = result.data.get("namespaces", [])
            if namespaces:
                namespace_list = "\n".join([f"  • {ns.get('name', 'Unknown')}" for ns in namespaces])
                return f"""📁 **Namespaces in Cluster**

{namespace_list}

*Total: {len(namespaces)} namespaces*"""
            else:
                return "📁 No namespaces found in the cluster."
        
        elif tool_used == "list_pods":
            pods = result.data.get("pods", [])
            if pods:
                pod_list = "\n".join([f"  • {pod.get('name', 'Unknown')} - {pod.get('status', 'Unknown')}" for pod in pods])
                return f"""🔄 **Pods in Namespace**

{pod_list}

*Total: {len(pods)} pods*"""
            else:
                return "🔄 No pods found in the specified namespace."
        
        elif tool_used == "get_pod_logs":
            logs = result.data.get("logs", "")
            if logs:
                return f"""📋 **Pod Logs**

```
{logs}
```

*Logs retrieved in {result.execution_time:.2f} seconds*"""
            else:
                return "📋 No logs available for the specified pod."
        
        else:
            # Generic response
            return f"✅ **Tool Execution Result** ({tool_used})\n\n{json.dumps(result.data, indent=2)}\n\n*Completed in {result.execution_time:.2f} seconds*"
    
    async def interactive_mode(self):
        """Run the application in interactive mode."""
        print("\n" + "="*60)
        print("🎭 OpenShift Host Test Application - Interactive Mode")
        print("="*60)
        print("Type 'help' for available commands, 'quit' to exit")
        print("Ask me anything about OpenShift management!")
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
                    print(self.get_history_summary())
                    continue
                
                elif user_input.lower() == 'tools':
                    self._show_available_tools()
                    continue
                
                elif user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                # Process the query
                print("\n🤖 Processing your query...")
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
• tools - Show available MCP tools
• status - Show application status
• quit/exit/q - Exit the application

💡 **Example Queries:**
• "What are the best practices for managing OpenShift namespaces?"
• "How do I troubleshoot pods stuck in Pending state?"
• "Analyze my cluster health"
• "List all namespaces"
• "Show pods in the default namespace"
• "Get logs from my-app-pod in production namespace"
        """
        print(help_text)
    
    def _show_available_tools(self):
        """Show available MCP tools."""
        if not self.client:
            print("❌ Not connected to MCP server")
            return
        
        tools = self.client.get_available_tools()
        categories = self.client.categorize_tools()
        
        print(f"\n🛠️  **Available MCP Tools ({len(tools)} total):**")
        
        for category, tool_list in categories.items():
            if tool_list:
                print(f"\n{category.upper()} Tools:")
                for tool in tool_list:
                    tool_info = self.client.get_tool_info(tool)
                    description = tool_info.get("description", "No description") if tool_info else "No description"
                    print(f"  • {tool:<30} - {description}")
    
    def _show_status(self):
        """Show application status."""
        status = f"""
📊 **Application Status:**
• Connected to MCP Server: {'✅ Yes' if self.is_connected else '❌ No'}
• Available Tools: {len(self.client.get_available_tools()) if self.client else 0}
• Conversation History: {len(self.conversation_history)} interactions
• Last Activity: {self.conversation_history[-1]['timestamp'] if self.conversation_history else 'None'}
        """
        print(status)

async def main():
    """Main function."""
    app = OpenShiftHostApp()
    
    try:
        # Initialize the application
        if not await app.initialize():
            print("❌ Failed to initialize application")
            return
        
        # Run interactive mode
        await app.interactive_mode()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        logger.error(f"Application error: {e}")
    
    finally:
        # Shutdown
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
