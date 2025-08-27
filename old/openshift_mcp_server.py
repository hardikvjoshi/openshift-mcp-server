#!/usr/bin/env python3
"""
OpenShift MCP Server

A Model Context Protocol (MCP) server that provides tools for managing OpenShift clusters.
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

class OpenShiftMCPServer:
    def __init__(self):
        self.server = Server("openshift-mcp-server", version="1.0.0")
        self.setup_tools()
    
    def setup_tools(self):
        """Register all OpenShift tools with the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Dict[str, Any]]:
            """List all available OpenShift tools."""
            return [
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
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            """Execute an OpenShift tool based on the name and arguments."""
            global cluster
            
            try:
                if name == "connect_cluster":
                    cluster_url = arguments.get("cluster_url")
                    token = arguments.get("token")
                    verify_ssl = arguments.get("verify_ssl", True)
                    
                    if not cluster_url or not token:
                        return {"error": "cluster_url and token are required"}
                    
                    cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
                    # Note: OpenShiftCluster connects synchronously in __init__
                    return {"message": f"Successfully connected to cluster: {cluster_url}"}
                
                elif name == "list_namespaces":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespaces = cluster.list_namespaces()
                    return {"namespaces": namespaces}
                
                elif name == "list_applications":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    applications = cluster.list_applications(namespace)
                    return {"applications": applications}
                
                elif name == "list_pods":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    pods = cluster.list_pods(namespace)
                    return {"pods": pods}
                
                elif name == "list_services":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    services = cluster.list_services(namespace)
                    return {"services": services}
                
                elif name == "list_routes":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    routes = cluster.list_routes(namespace)
                    return {"routes": routes}
                
                elif name == "list_configmaps":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    configmaps = cluster.list_configmaps(namespace)
                    return {"configmaps": configmaps}
                
                elif name == "list_secrets":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    secrets = cluster.list_secrets(namespace)
                    return {"secrets": secrets}
                
                elif name == "get_pod_logs":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    pod_name = arguments.get("pod_name")
                    tail_lines = arguments.get("tail_lines", 100)
                    
                    if not namespace or not pod_name:
                        return {"error": "namespace and pod_name are required"}
                    
                    logs = cluster.get_pod_logs(namespace, pod_name, tail_lines)
                    return {"logs": logs}
                
                elif name == "get_resource_usage":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    if not namespace:
                        return {"error": "namespace is required"}
                    
                    usage = cluster.get_resource_usage(namespace)
                    return {"resource_usage": usage}
                
                elif name == "scale_deployment":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    deployment_name = arguments.get("deployment_name")
                    replicas = arguments.get("replicas")
                    
                    if not namespace or not deployment_name or replicas is None:
                        return {"error": "namespace, deployment_name, and replicas are required"}
                    
                    result = cluster.scale_deployment(namespace, deployment_name, replicas)
                    return {"result": result}
                
                elif name == "delete_pod":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    namespace = arguments.get("namespace")
                    pod_name = arguments.get("pod_name")
                    
                    if not namespace or not pod_name:
                        return {"error": "namespace and pod_name are required"}
                    
                    result = cluster.delete_pod(namespace, pod_name)
                    return {"result": result}
                
                elif name == "create_namespace":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    name = arguments.get("name")
                    labels = arguments.get("labels", {})
                    
                    if not name:
                        return {"error": "name is required"}
                    
                    result = cluster.create_namespace(name, labels)
                    return {"result": result}
                
                elif name == "delete_namespace":
                    if not cluster:
                        return {"error": "Not connected to cluster. Use connect_cluster first."}
                    
                    name = arguments.get("name")
                    if not name:
                        return {"error": "name is required"}
                    
                    result = cluster.delete_namespace(name)
                    return {"result": result}
                
                else:
                    return {"error": f"Unknown tool: {name}"}
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return {"error": str(e)}

async def main():
    """Main function to run the MCP server."""
    # Auto-connect if environment variables are set
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    verify_ssl = os.getenv("OPENSHIFT_VERIFY_SSL", "true").lower() == "true"
    
    if cluster_url and token:
        global cluster
        try:
            cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
            # Note: OpenShiftCluster connects synchronously in __init__
            logger.info(f"Auto-connected to cluster: {cluster_url}")
        except Exception as e:
            logger.warning(f"Auto-connection failed: {e}")
    
    # Create and run the MCP server
    server = OpenShiftMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openshift-mcp-server",
                server_version="1.0.0",
                capabilities={
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                }
            )
        )

if __name__ == "__main__":
    asyncio.run(main()) 