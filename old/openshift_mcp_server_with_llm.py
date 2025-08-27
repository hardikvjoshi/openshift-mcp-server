#!/usr/bin/env python3
"""
Enhanced OpenShift MCP Server with LLM Integration

This server combines OpenShift cluster management with LLM capabilities,
allowing AI assistants to intelligently manage OpenShift resources.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from openshift_cluster import OpenShiftCluster
from llm_integration import llm_manager, LLMResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cluster instance
cluster: Optional[OpenShiftCluster] = None

def _format_memory(bytes_value: int) -> str:
    """Format memory bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

class EnhancedOpenShiftMCPServer:
    def __init__(self):
        self.server = Server("openshift-mcp-server-with-llm", version="2.0.0")
        self.setup_tools()
    
    def setup_tools(self):
        """Register all OpenShift and LLM tools with the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Dict[str, Any]]:
            """List all available tools."""
            return [
                # OpenShift Management Tools
                {
                    "name": "connect_cluster",
                    "description": "Connect to an OpenShift cluster",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "cluster_url": {"type": "string", "description": "OpenShift cluster URL"},
                            "token": {"type": "string", "description": "Authentication token"},
                            "verify_ssl": {"type": "boolean", "description": "Verify SSL certificates"}
                        },
                        "required": ["cluster_url", "token"]
                    }
                },
                {
                    "name": "list_namespaces",
                    "description": "List all namespaces in the cluster",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "list_applications",
                    "description": "List applications in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "list_pods",
                    "description": "List pods in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "list_services",
                    "description": "List services in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "list_routes",
                    "description": "List routes in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "list_configmaps",
                    "description": "List configmaps in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "list_secrets",
                    "description": "List secrets in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "get_pod_logs",
                    "description": "Get logs from a specific pod",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"},
                            "pod_name": {"type": "string", "description": "Pod name"},
                            "tail_lines": {"type": "integer", "description": "Number of lines to retrieve"}
                        },
                        "required": ["namespace", "pod_name"]
                    }
                },
                {
                    "name": "get_resource_usage",
                    "description": "Get resource usage for pods in a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["namespace"]
                    }
                },
                {
                    "name": "scale_deployment",
                    "description": "Scale a deployment to a specific number of replicas",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"},
                            "deployment_name": {"type": "string", "description": "Deployment name"},
                            "replicas": {"type": "integer", "description": "Number of replicas"}
                        },
                        "required": ["namespace", "deployment_name", "replicas"]
                    }
                },
                {
                    "name": "delete_pod",
                    "description": "Delete a specific pod",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace name"},
                            "pod_name": {"type": "string", "description": "Pod name"}
                        },
                        "required": ["namespace", "pod_name"]
                    }
                },
                {
                    "name": "create_namespace",
                    "description": "Create a new namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Namespace name"},
                            "labels": {"type": "object", "description": "Labels to apply"}
                        },
                        "required": ["name"]
                    }
                },
                {
                    "name": "delete_namespace",
                    "description": "Delete a namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Namespace name"}
                        },
                        "required": ["name"]
                    }
                },
                
                # LLM Integration Tools
                {
                    "name": "ask_llm",
                    "description": "Ask the LLM a question about OpenShift management",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "Your question about OpenShift management"},
                            "context": {"type": "string", "description": "Additional context or cluster information"},
                            "provider": {"type": "string", "description": "LLM provider to use (gemini, openai, claude, custom)"}
                        },
                        "required": ["question"]
                    }
                },
                {
                    "name": "get_llm_providers",
                    "description": "Get available LLM providers and their status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "test_llm_connection",
                    "description": "Test connection to LLM providers",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string", "description": "Specific provider to test (optional)"}
                        }
                    }
                },
                {
                    "name": "intelligent_cluster_analysis",
                    "description": "Use LLM to analyze cluster health and provide recommendations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {"type": "string", "description": "Namespace to analyze (optional)"},
                            "provider": {"type": "string", "description": "LLM provider to use"}
                        }
                    }
                },
                {
                    "name": "get_troubleshooting_help",
                    "description": "Get AI-powered troubleshooting help for OpenShift issues",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_description": {"type": "string", "description": "Description of the issue you're facing"},
                            "error_messages": {"type": "string", "description": "Any error messages or logs"},
                            "provider": {"type": "string", "description": "LLM provider to use"}
                        },
                        "required": ["issue_description"]
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            """Execute tools based on the name and arguments."""
            global cluster
            
            try:
                # OpenShift Management Tools
                if name == "connect_cluster":
                    return await self._handle_connect_cluster(arguments)
                elif name == "list_namespaces":
                    return await self._handle_list_namespaces()
                elif name == "list_applications":
                    return await self._handle_list_applications(arguments)
                elif name == "list_pods":
                    return await self._handle_list_pods(arguments)
                elif name == "list_services":
                    return await self._handle_list_services(arguments)
                elif name == "list_routes":
                    return await self._handle_list_routes(arguments)
                elif name == "list_configmaps":
                    return await self._handle_list_configmaps(arguments)
                elif name == "list_secrets":
                    return await self._handle_list_secrets(arguments)
                elif name == "get_pod_logs":
                    return await self._handle_get_pod_logs(arguments)
                elif name == "get_resource_usage":
                    return await self._handle_get_resource_usage(arguments)
                elif name == "scale_deployment":
                    return await self._handle_scale_deployment(arguments)
                elif name == "delete_pod":
                    return await self._handle_delete_pod(arguments)
                elif name == "create_namespace":
                    return await self._handle_create_namespace(arguments)
                elif name == "delete_namespace":
                    return await self._handle_delete_namespace(arguments)
                
                # LLM Integration Tools
                elif name == "ask_llm":
                    return await self._handle_ask_llm(arguments)
                elif name == "get_llm_providers":
                    return await self._handle_get_llm_providers()
                elif name == "test_llm_connection":
                    return await self._handle_test_llm_connection(arguments)
                elif name == "intelligent_cluster_analysis":
                    return await self._handle_intelligent_cluster_analysis(arguments)
                elif name == "get_troubleshooting_help":
                    return await self._handle_get_troubleshooting_help(arguments)
                
                else:
                    return {"error": f"Unknown tool: {name}"}
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return {"error": str(e)}
    
    # OpenShift Tool Handlers
    async def _handle_connect_cluster(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cluster connection."""
        global cluster
        
        cluster_url = arguments.get("cluster_url")
        token = arguments.get("token")
        verify_ssl = arguments.get("verify_ssl", True)
        
        if not cluster_url or not token:
            return {"error": "cluster_url and token are required"}
        
        cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
        return {"message": f"Successfully connected to cluster: {cluster_url}"}
    
    async def _handle_list_namespaces(self) -> Dict[str, Any]:
        """Handle namespace listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespaces = cluster.list_namespaces()
        return {"namespaces": namespaces}
    
    async def _handle_list_applications(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle application listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        applications = cluster.list_applications(namespace)
        return {"applications": applications}
    
    async def _handle_list_pods(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pod listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        pods = cluster.list_pods(namespace)
        return {"pods": pods}
    
    async def _handle_list_services(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle service listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        services = cluster.list_services(namespace)
        return {"services": services}
    
    async def _handle_list_routes(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle route listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        routes = cluster.list_routes(namespace)
        return {"routes": routes}
    
    async def _handle_list_configmaps(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configmap listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        configmaps = cluster.list_configmaps(namespace)
        return {"configmaps": configmaps}
    
    async def _handle_list_secrets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle secret listing."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        secrets = cluster.list_secrets(namespace)
        return {"secrets": secrets}
    
    async def _handle_get_pod_logs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pod log retrieval."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        pod_name = arguments.get("pod_name")
        tail_lines = arguments.get("tail_lines", 100)
        
        if not namespace or not pod_name:
            return {"error": "namespace and pod_name are required"}
        
        logs = cluster.get_pod_logs(namespace, pod_name, tail_lines)
        return {"logs": logs}
    
    async def _handle_get_resource_usage(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource usage retrieval."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        if not namespace:
            return {"error": "namespace is required"}
        
        usage = cluster.get_resource_usage(namespace)
        return {"resource_usage": usage}
    
    async def _handle_scale_deployment(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deployment scaling."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        deployment_name = arguments.get("deployment_name")
        replicas = arguments.get("replicas")
        
        if not namespace or not deployment_name or replicas is None:
            return {"error": "namespace, deployment_name, and replicas are required"}
        
        result = cluster.scale_deployment(namespace, deployment_name, replicas)
        return {"result": result}
    
    async def _handle_delete_pod(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pod deletion."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        pod_name = arguments.get("pod_name")
        
        if not namespace or not pod_name:
            return {"error": "namespace and pod_name are required"}
        
        result = cluster.delete_pod(namespace, pod_name)
        return {"result": result}
    
    async def _handle_create_namespace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle namespace creation."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        name = arguments.get("name")
        labels = arguments.get("labels", {})
        
        if not name:
            return {"error": "name is required"}
        
        result = cluster.create_namespace(name, labels)
        return {"result": result}
    
    async def _handle_delete_namespace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle namespace deletion."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        name = arguments.get("name")
        if not name:
            return {"error": "name is required"}
        
        result = cluster.delete_namespace(name)
        return {"result": result}
    
    # LLM Tool Handlers
    async def _handle_ask_llm(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM questions."""
        question = arguments.get("question")
        context = arguments.get("context", "")
        provider = arguments.get("provider")
        
        if not question:
            return {"error": "question is required"}
        
        # Add OpenShift context if available
        if cluster:
            cluster_context = f"Connected to OpenShift cluster: {cluster.cluster_url}"
            context = f"{cluster_context}\n\n{context}" if context else cluster_context
        
        response = await llm_manager.generate_response(question, context, provider)
        
        if response.error:
            return {"error": f"LLM error: {response.error}"}
        
        return {
            "response": response.content,
            "provider": response.provider,
            "model": response.model,
            "response_time": response.response_time,
            "tokens_used": response.tokens_used
        }
    
    async def _handle_get_llm_providers(self) -> Dict[str, Any]:
        """Handle LLM provider information."""
        providers = llm_manager.get_available_providers()
        default = llm_manager.get_default_provider()
        
        return {
            "available_providers": providers,
            "default_provider": default,
            "total_providers": len(providers)
        }
    
    async def _handle_test_llm_connection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM connection testing."""
        provider = arguments.get("provider")
        
        if provider:
            # Test specific provider
            if provider in llm_manager.providers:
                status = await llm_manager.providers[provider].test_connection()
                return {provider: status}
            else:
                return {"error": f"Provider '{provider}' not found"}
        else:
            # Test all providers
            results = await llm_manager.test_all_connections()
            return {"connection_results": results}
    
    async def _handle_intelligent_cluster_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intelligent cluster analysis using LLM."""
        if not cluster:
            return {"error": "Not connected to cluster. Use connect_cluster first."}
        
        namespace = arguments.get("namespace")
        provider = arguments.get("provider")
        
        # Gather cluster information
        try:
            namespaces = cluster.list_namespaces()
            cluster_info = f"Total namespaces: {len(namespaces)}"
            
            if namespace:
                pods = cluster.list_pods(namespace)
                services = cluster.list_services(namespace)
                routes = cluster.list_routes(namespace)
                
                context = f"""
Cluster Information:
- Total namespaces: {len(namespaces)}
- Current namespace: {namespace}
- Pods in namespace: {len(pods)}
- Services in namespace: {len(services)}
- Routes in namespace: {len(routes)}
"""
            else:
                context = f"""
Cluster Information:
- Total namespaces: {len(namespaces)}
- Namespace names: {[ns['name'] for ns in namespaces[:5]]}
"""
            
            prompt = f"""
Please analyze this OpenShift cluster and provide:
1. Overall health assessment
2. Key observations
3. Recommendations for optimization
4. Potential issues to watch for

{context}
"""
            
            response = await llm_manager.generate_response(prompt, context, provider)
            
            if response.error:
                return {"error": f"LLM analysis failed: {response.error}"}
            
            return {
                "analysis": response.content,
                "provider": response.provider,
                "model": response.model,
                "cluster_info": context.strip(),
                "response_time": response.response_time
            }
            
        except Exception as e:
            return {"error": f"Failed to gather cluster information: {str(e)}"}
    
    async def _handle_get_troubleshooting_help(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI-powered troubleshooting help."""
        issue_description = arguments.get("issue_description")
        error_messages = arguments.get("error_messages", "")
        provider = arguments.get("provider")
        
        if not issue_description:
            return {"error": "issue_description is required"}
        
        # Add cluster context if available
        context = ""
        if cluster:
            try:
                namespaces = cluster.list_namespaces()
                context = f"Connected to OpenShift cluster with {len(namespaces)} namespaces."
            except:
                context = "Connected to OpenShift cluster."
        
        prompt = f"""
I'm experiencing an OpenShift issue and need help troubleshooting:

Issue: {issue_description}

{f"Error messages/logs: {error_messages}" if error_messages else ""}

{context}

Please provide:
1. Possible causes of this issue
2. Step-by-step troubleshooting steps
3. Commands to run for diagnosis
4. Prevention tips for the future
5. When to contact support
"""
        
        response = await llm_manager.generate_response(prompt, context, provider)
        
        if response.error:
            return {"error": f"Troubleshooting help failed: {response.error}"}
        
        return {
            "troubleshooting_help": response.content,
            "provider": response.provider,
            "model": response.model,
            "response_time": response.response_time
        }

async def main():
    """Main function to run the enhanced MCP server."""
    # Auto-connect if environment variables are set
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    verify_ssl = os.getenv("OPENSHIFT_VERIFY_SSL", "true").lower() == "true"
    
    if cluster_url and token:
        global cluster
        try:
            cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
            logger.info(f"Auto-connected to cluster: {cluster_url}")
        except Exception as e:
            logger.warning(f"Auto-connection failed: {e}")
    
    # Test LLM integration
    logger.info("Testing LLM integration...")
    try:
        connection_results = await llm_manager.test_all_connections()
        for provider, status in connection_results.items():
            logger.info(f"LLM Provider {provider}: {'✅' if status else '❌'}")
    except Exception as e:
        logger.warning(f"LLM integration test failed: {e}")
    
    # Create and run the enhanced MCP server
    server = EnhancedOpenShiftMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openshift-mcp-server-with-llm",
                server_version="2.0.0",
                capabilities={
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
