# OpenShift MCP Server Usage Guide

This guide explains how to use the OpenShift MCP (Model Context Protocol) server and client.

## What is MCP?

The Model Context Protocol (MCP) is a standard that allows AI assistants and other clients to connect to external tools and data sources. Our OpenShift MCP server provides 15 tools for managing OpenShift clusters.

## Quick Start

### 1. Prerequisites

- Python 3.8+ with virtual environment
- OpenShift cluster access (URL and token)
- Environment variables set in `.env` file

### 2. Start the MCP Server

```bash
# Start the server (it will auto-connect to your cluster)
python openshift_mcp_server.py
```

The server will:
- Connect to your OpenShift cluster automatically
- Start listening for MCP client connections
- Be ready to handle tool requests

### 3. Available Tools

The server provides these OpenShift management tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `connect_cluster` | Connect to OpenShift cluster | `cluster_url`, `token`, `verify_ssl` |
| `list_namespaces` | List all namespaces | None |
| `list_applications` | List applications in namespace | `namespace` |
| `list_pods` | List pods in namespace | `namespace` |
| `list_services` | List services in namespace | `namespace` |
| `list_routes` | List routes in namespace | `namespace` |
| `list_configmaps` | List configmaps in namespace | `namespace` |
| `list_secrets` | List secrets in namespace | `namespace` |
| `get_pod_logs` | Get pod logs | `namespace`, `pod_name`, `tail_lines` |
| `get_resource_usage` | Get resource usage | `namespace` |
| `scale_deployment` | Scale deployment | `namespace`, `deployment_name`, `replicas` |
| `delete_pod` | Delete a pod | `namespace`, `pod_name` |
| `create_namespace` | Create namespace | `name`, `labels` |
| `delete_namespace` | Delete namespace | `name` |

## Using with MCP Clients

### Option 1: Claude Desktop (Recommended)

1. Install Claude Desktop
2. Go to Settings → Model Context Protocol
3. Add a new server:
   - **Name**: OpenShift MCP
   - **Command**: `python openshift_mcp_server.py`
   - **Working Directory**: Your project directory
4. Restart Claude Desktop
5. The OpenShift tools will now be available in your conversations

### Option 2: Custom MCP Client

We provide a simple client (`mcp_client.py`) for testing:

```bash
python mcp_client.py
```

This will start an interactive session where you can:
- List namespaces: `list_namespaces`
- List pods: `list_pods <namespace>`
- List services: `list_services <namespace>`
- Get resource usage: `get_resource_usage <namespace>`
- Quit: `quit`

### Option 3: Programmatic Client

```python
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def use_openshift_mcp():
    server_params = StdioServerParameters(
        command="python openshift_mcp_server.py",
        args=[],
        env={}
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        session = ClientSession(read_stream, write_stream, "my-client", "1.0.0")
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[t['name'] for t in tools]}")
        
        # Call a tool
        result = await session.call_tool("list_namespaces", {})
        print(f"Namespaces: {result}")
```

## Demo Script

Run the demonstration script to see the server in action:

```bash
python demo_mcp.py
```

This will:
- Start the MCP server
- Show all available tools
- Keep the server running for client connections
- Provide usage instructions

## Testing

Test the server functionality:

```bash
python test_mcp_server.py
```

This verifies that:
- The server can start successfully
- It connects to your OpenShift cluster
- All tools are properly registered

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Python version (3.8+ required)
   - Verify virtual environment is activated
   - Check environment variables are set

2. **Connection failed**
   - Verify OpenShift cluster URL and token
   - Check SSL verification settings
   - Ensure network connectivity

3. **Tools not working**
   - Verify cluster connection
   - Check RBAC permissions
   - Review server logs

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### SSL Issues

For self-signed certificates, set in your `.env`:

```env
OPENSHIFT_VERIFY_SSL=false
```

## Architecture

```
┌─────────────────┐    MCP Protocol    ┌─────────────────────┐
│   MCP Client    │ ◄────────────────► │  OpenShift MCP      │
│  (Claude, etc.) │                    │      Server         │
└─────────────────┘                    └─────────────────────┘
                                                │
                                                ▼
                                       ┌─────────────────────┐
                                       │  OpenShift Cluster  │
                                       │   (via Kubernetes   │
                                       │      API)           │
                                       └─────────────────────┘
```

## Security Considerations

- **Token Security**: Store tokens securely, never commit to version control
- **RBAC**: Use least-privilege access for OpenShift tokens
- **Network**: Ensure secure network connections to your cluster
- **SSL**: Enable SSL verification in production environments

## Next Steps

1. **Integration**: Connect the MCP server to your preferred AI assistant
2. **Customization**: Add new tools specific to your OpenShift workflows
3. **Automation**: Use the MCP server in CI/CD pipelines
4. **Monitoring**: Add metrics and health checks

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error details
3. Verify OpenShift cluster connectivity
4. Test with the provided demo and test scripts

---

**Note**: This MCP server is designed for OpenShift cluster management and provides a bridge between AI assistants and your Kubernetes/OpenShift infrastructure.
