# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- Access to an OpenShift cluster
- OpenShift authentication token

## Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd ocpMCP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your cluster connection**
   ```bash
   cp env.example .env
   # Edit .env with your cluster details
   ```

## Configuration

Edit the `.env` file with your OpenShift cluster details:

```env
OPENSHIFT_CLUSTER_URL=https://your-cluster.example.com
OPENSHIFT_TOKEN=your-openshift-token-here
```

### Getting Your OpenShift Token

1. **From OpenShift Web Console:**
   - Log in to your OpenShift web console
   - Click on your username in the top right
   - Select "Copy login command"
   - Copy the token from the displayed command

2. **Using OpenShift CLI:**
   ```bash
   oc whoami -t
   ```

## Testing the Connection

Run the test script to verify everything works:

```bash
python test_openshift_mcp.py
```

This will:
- Test cluster connectivity
- List available namespaces
- Show applications in the first namespace
- Display pods, services, and other resources

## Using the MCP Server

### Method 1: Direct Execution
```bash
python openshift_mcp_server.py
```

### Method 2: With MCP Client Configuration
1. Copy `mcp-config.json` to your MCP client configuration directory
2. Update the environment variables in the config file
3. Start your MCP client

## Available Commands

Once connected, you can use these MCP tools:

- `connect_cluster` - Connect to OpenShift cluster
- `list_namespaces` - List all namespaces/projects
- `list_applications <namespace>` - List applications in a namespace
- `list_pods <namespace>` - List pods in a namespace
- `list_services <namespace>` - List services in a namespace
- `list_routes <namespace>` - List routes in a namespace
- `get_pod_logs <namespace> <pod_name>` - Get pod logs
- `describe_resource <namespace> <type> <name>` - Describe a resource
- `get_namespace_info <namespace>` - Get detailed namespace info
- `list_configmaps <namespace>` - List configmaps
- `list_secrets <namespace>` - List secrets

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   - The server is configured to skip SSL verification by default
   - For production, enable SSL verification in `openshift_cluster.py`

2. **Authentication Errors**
   - Verify your token is valid and not expired
   - Ensure you have appropriate permissions on the cluster

3. **Connection Timeouts**
   - Check your cluster URL is correct
   - Verify network connectivity to the cluster

4. **Permission Errors**
   - Ensure your token has sufficient RBAC permissions
   - You need at least read access to namespaces and resources

### Debug Mode

Enable debug logging by modifying the logging level in `openshift_mcp_server.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

- Explore the available MCP tools
- Integrate with your preferred MCP client
- Customize the server for your specific needs
- Add additional OpenShift resource types as needed

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the main README.md for detailed documentation
- Open an issue in the project repository 