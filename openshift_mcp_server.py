#!/usr/bin/env python3
"""
OpenShift MCP Server

A Model Context Protocol server that provides integration with OpenShift clusters,
allowing management of namespaces, applications, and administrative tasks.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

import mcp.server
import mcp.server.stdio
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from openshift import client as openshift_client
from openshift.dynamic import DynamicClient
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server instance
server = mcp.server.Server("openshift-mcp-server")

from openshift_cluster import OpenShiftCluster

# Global cluster instance
cluster: Optional[OpenShiftCluster] = None


@server.list_tools()
async def handle_list_tools() -> list[mcp.server.Tool]:
    """List available tools for OpenShift cluster management."""
    return [
        mcp.server.Tool(
            name="connect_cluster",
            description="Connect to an OpenShift cluster using URL and token",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_url": {"type": "string", "description": "OpenShift cluster URL"},
                    "token": {"type": "string", "description": "Authentication token"}
                },
                "required": ["cluster_url", "token"]
            }
        ),
        mcp.server.Tool(
            name="list_namespaces",
            description="List all namespaces/projects in the OpenShift cluster",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        mcp.server.Tool(
            name="list_applications",
            description="List applications running in a specific namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="list_pods",
            description="List all pods in a specific namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="list_services",
            description="List all services in a specific namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="list_routes",
            description="List all routes in a specific namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="get_pod_logs",
            description="Get logs from a specific pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"},
                    "pod_name": {"type": "string", "description": "Pod name"},
                    "tail_lines": {"type": "integer", "description": "Number of lines to retrieve", "default": 100}
                },
                "required": ["namespace", "pod_name"]
            }
        ),
        mcp.server.Tool(
            name="describe_resource",
            description="Describe a specific Kubernetes resource",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"},
                    "resource_type": {"type": "string", "description": "Resource type (Pod, Service, Deployment, etc.)"},
                    "resource_name": {"type": "string", "description": "Resource name"}
                },
                "required": ["namespace", "resource_type", "resource_name"]
            }
        ),
        mcp.server.Tool(
            name="get_namespace_info",
            description="Get detailed information about a namespace including quotas and limits",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="list_configmaps",
            description="List all configmaps in a specific namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="list_secrets",
            description="List all secrets in a specific namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        ),
        mcp.server.Tool(
            name="scale_deployment",
            description="Scale a deployment to the specified number of replicas",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"},
                    "deployment_name": {"type": "string", "description": "Deployment name"},
                    "replicas": {"type": "integer", "description": "Number of replicas"}
                },
                "required": ["namespace", "deployment_name", "replicas"]
            }
        ),
        mcp.server.Tool(
            name="restart_deployment",
            description="Restart a deployment by triggering a rollout",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"},
                    "deployment_name": {"type": "string", "description": "Deployment name"}
                },
                "required": ["namespace", "deployment_name"]
            }
        ),
        mcp.server.Tool(
            name="get_cluster_health",
            description="Get overall cluster health information including nodes and pod status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        mcp.server.Tool(
            name="get_resource_usage",
            description="Get resource usage information for a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Namespace name"}
                },
                "required": ["namespace"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[mcp.server.TextContent]:
    """Handle tool calls for OpenShift cluster operations."""
    global cluster
    
    try:
        if name == "connect_cluster":
            cluster_url = arguments["cluster_url"]
            token = arguments["token"]
            
            cluster = OpenShiftCluster(cluster_url, token)
            return [mcp.server.TextContent(
                type="text",
                text=f"Successfully connected to OpenShift cluster: {cluster_url}"
            )]
        
        elif name == "list_namespaces":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespaces = cluster.list_namespaces()
            if namespaces:
                result = "**Namespaces in the cluster:**\n\n"
                for ns in namespaces:
                    result += f"- **{ns['name']}** (Display: {ns['display_name']})\n"
                    result += f"  - Status: {ns['status']}\n"
                    result += f"  - Description: {ns['description']}\n"
                    result += f"  - Created: {ns['created']}\n\n"
            else:
                result = "No namespaces found or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "list_applications":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            applications = cluster.list_applications(namespace)
            
            if applications:
                result = f"**Applications in namespace '{namespace}':**\n\n"
                for app in applications:
                    result += f"- **{app['name']}** ({app['type']})\n"
                    result += f"  - Image: {app['image']}\n"
                    result += f"  - Created: {app['created']}\n"
                    if 'replicas' in app:
                        result += f"  - Replicas: {app['replicas']}\n"
                    if 'available_replicas' in app:
                        result += f"  - Available: {app['available_replicas']}\n"
                    result += "\n"
            else:
                result = f"No applications found in namespace '{namespace}' or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "list_pods":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            pods = cluster.list_pods(namespace)
            
            if pods:
                result = f"**Pods in namespace '{namespace}':**\n\n"
                for pod in pods:
                    result += f"- **{pod['name']}**\n"
                    result += f"  - Status: {pod['status']}\n"
                    result += f"  - Ready: {pod['ready']}\n"
                    result += f"  - Node: {pod['node']}\n"
                    result += f"  - Image: {pod['image']}\n"
                    result += f"  - Restarts: {pod['restart_count']}\n\n"
            else:
                result = f"No pods found in namespace '{namespace}' or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "list_services":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            services = cluster.list_services(namespace)
            
            if services:
                result = f"**Services in namespace '{namespace}':**\n\n"
                for service in services:
                    result += f"- **{service['name']}** ({service['type']})\n"
                    result += f"  - Cluster IP: {service['cluster_ip']}\n"
                    if service['external_ips']:
                        result += f"  - External IPs: {', '.join(service['external_ips'])}\n"
                    if service['ports']:
                        ports_str = ", ".join([f"{p['port']}:{p['target_port']}/{p['protocol']}" for p in service['ports']])
                        result += f"  - Ports: {ports_str}\n"
                    result += "\n"
            else:
                result = f"No services found in namespace '{namespace}' or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "list_routes":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            routes = cluster.list_routes(namespace)
            
            if routes:
                result = f"**Routes in namespace '{namespace}':**\n\n"
                for route in routes:
                    result += f"- **{route['name']}**\n"
                    result += f"  - Host: {route['host']}\n"
                    result += f"  - Service: {route['service_name']}\n"
                    result += f"  - Port: {route['port']}\n"
                    result += f"  - TLS: {route['tls']}\n\n"
            else:
                result = f"No routes found in namespace '{namespace}' or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "get_pod_logs":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            pod_name = arguments["pod_name"]
            tail_lines = arguments.get("tail_lines", 100)
            
            logs = cluster.get_pod_logs(namespace, pod_name, tail_lines)
            result = f"**Logs for pod '{pod_name}' in namespace '{namespace}':**\n\n```\n{logs}\n```"
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "describe_resource":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            resource_type = arguments["resource_type"]
            resource_name = arguments["resource_name"]
            
            resource_info = cluster.describe_resource(namespace, resource_type, resource_name)
            result = f"**Resource description for {resource_type} '{resource_name}' in namespace '{namespace}':**\n\n```json\n{json.dumps(resource_info, indent=2)}\n```"
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "get_namespace_info":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            namespace_info = cluster.get_namespace_info(namespace)
            
            if "error" not in namespace_info:
                result = f"**Detailed information for namespace '{namespace}':**\n\n"
                result += f"- **Name**: {namespace_info['name']}\n"
                result += f"- **Display Name**: {namespace_info['display_name']}\n"
                result += f"- **Description**: {namespace_info['description']}\n"
                result += f"- **Status**: {namespace_info['status']}\n"
                result += f"- **Created**: {namespace_info['created']}\n"
                result += f"- **Resource Quotas**: {len(namespace_info['resource_quotas'])}\n"
                result += f"- **Limit Ranges**: {len(namespace_info['limit_ranges'])}\n"
            else:
                result = f"Error getting namespace info: {namespace_info['error']}"
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "list_configmaps":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            configmaps = cluster.list_configmaps(namespace)
            
            if configmaps:
                result = f"**ConfigMaps in namespace '{namespace}':**\n\n"
                for configmap in configmaps:
                    result += f"- **{configmap['name']}**\n"
                    result += f"  - Data Keys: {', '.join(configmap['data_keys']) if configmap['data_keys'] else 'None'}\n"
                    result += f"  - Created: {configmap['created']}\n\n"
            else:
                result = f"No configmaps found in namespace '{namespace}' or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "list_secrets":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            secrets = cluster.list_secrets(namespace)
            
            if secrets:
                result = f"**Secrets in namespace '{namespace}':**\n\n"
                for secret in secrets:
                    result += f"- **{secret['name']}** ({secret['type']})\n"
                    result += f"  - Data Keys: {', '.join(secret['data_keys']) if secret['data_keys'] else 'None'}\n"
                    result += f"  - Created: {secret['created']}\n\n"
            else:
                result = f"No secrets found in namespace '{namespace}' or error occurred."
            
            return [mcp.server.TextContent(type="text", text=result)]
        
        elif name == "scale_deployment":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            deployment_name = arguments["deployment_name"]
            replicas = arguments["replicas"]
            
            result = cluster.scale_deployment(namespace, deployment_name, replicas)
            if result['success']:
                response = f"✅ **{result['message']}**\n\n"
                response += f"- **Deployment**: {result['name']}\n"
                response += f"- **Replicas**: {result['replicas']}\n"
            else:
                response = f"❌ **Error scaling deployment**: {result['error']}"
            
            return [mcp.server.TextContent(type="text", text=response)]
        
        elif name == "restart_deployment":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            deployment_name = arguments["deployment_name"]
            
            result = cluster.restart_deployment(namespace, deployment_name)
            if result['success']:
                response = f"✅ **{result['message']}**\n\n"
                response += f"- **Deployment**: {result['name']}\n"
            else:
                response = f"❌ **Error restarting deployment**: {result['error']}"
            
            return [mcp.server.TextContent(type="text", text=response)]
        
        elif name == "get_cluster_health":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            health_info = cluster.get_cluster_health()
            if 'error' not in health_info:
                response = "🏥 **Cluster Health Overview**\n\n"
                response += f"📊 **Statistics:**\n"
                response += f"- Total Namespaces: {health_info['namespaces_count']}\n"
                response += f"- Total Pods: {health_info['total_pods']}\n"
                response += f"- Running Pods: {health_info['running_pods']}\n"
                response += f"- Failed Pods: {health_info['failed_pods']}\n"
                response += f"- Pending Pods: {health_info['pending_pods']}\n\n"
                
                response += f"🖥️ **Nodes ({len(health_info['nodes'])}):**\n"
                for node in health_info['nodes']:
                    status_icon = "✅" if node['ready'] else "❌"
                    response += f"- {status_icon} **{node['name']}** ({node['status']})\n"
                    response += f"  - CPU: {node['capacity']['cpu']}, Memory: {node['capacity']['memory']}\n"
            else:
                response = f"❌ **Error getting cluster health**: {health_info['error']}"
            
            return [mcp.server.TextContent(type="text", text=response)]
        
        elif name == "get_resource_usage":
            if not cluster:
                return [mcp.server.TextContent(
                    type="text",
                    text="Error: Not connected to a cluster. Please connect first using connect_cluster."
                )]
            
            namespace = arguments["namespace"]
            usage_info = cluster.get_resource_usage(namespace)
            
            if 'error' not in usage_info:
                response = f"📊 **Resource Usage for namespace '{namespace}'**\n\n"
                response += f"💾 **Total Resource Requests:**\n"
                response += f"- CPU: {usage_info['total_cpu_request']:.2f} cores\n"
                response += f"- Memory: {self._format_memory(usage_info['total_memory_request'])}\n\n"
                
                response += f"🚫 **Total Resource Limits:**\n"
                response += f"- CPU: {usage_info['total_cpu_limit']:.2f} cores\n"
                response += f"- Memory: {self._format_memory(usage_info['total_memory_limit'])}\n\n"
                
                response += f"📦 **Pods ({len(usage_info['pods'])}):**\n"
                for pod in usage_info['pods'][:5]:  # Show first 5 pods
                    response += f"- **{pod['name']}** ({pod['status']})\n"
                    response += f"  - CPU: {pod['cpu_request']:.2f} req / {pod['cpu_limit']:.2f} limit\n"
                    response += f"  - Memory: {self._format_memory(pod['memory_request'])} req / {self._format_memory(pod['memory_limit'])} limit\n"
                
                if len(usage_info['pods']) > 5:
                    response += f"  ... and {len(usage_info['pods']) - 5} more pods\n"
            else:
                response = f"❌ **Error getting resource usage**: {usage_info['error']}"
            
            return [mcp.server.TextContent(type="text", text=response)]
        
        else:
            return [mcp.server.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return [mcp.server.TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}"
        )]

    def _format_memory(self, bytes_value: int) -> str:
        """Format memory bytes into human-readable format."""
        if bytes_value == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"


async def main():
    """Main function to run the MCP server."""
    # Load environment variables if .env file exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Auto-connect if environment variables are set
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    
    if cluster_url and token:
        try:
            global cluster
            cluster = OpenShiftCluster(cluster_url, token)
            logger.info("Auto-connected to OpenShift cluster using environment variables")
        except Exception as e:
            logger.warning(f"Failed to auto-connect to cluster: {e}")
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main()) 