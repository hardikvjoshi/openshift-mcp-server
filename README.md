# OpenShift MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with OpenShift clusters, allowing you to manage namespaces, applications, and perform administrative tasks.

## Features

- **Cluster Connection**: Connect to OpenShift clusters using URL and token authentication
- **Namespace Management**: List all namespaces/projects in the cluster
- **Application Discovery**: List applications running in selected namespaces
- **Administrative Tools**: Provide administrative capabilities for OpenShift cluster management
- **Real-time Data**: Get live information from your OpenShift cluster

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file with your OpenShift cluster credentials:

```env
OPENSHIFT_CLUSTER_URL=https://your-cluster.example.com
OPENSHIFT_TOKEN=your-openshift-token
```

## Usage

### Starting the MCP Server

```bash
python openshift_mcp_server.py
```

### Available Commands

#### Basic Operations
- `connect_cluster`: Connect to OpenShift cluster using URL and token
- `list_namespaces`: List all namespaces in the cluster
- `list_applications <namespace>`: List applications in a specific namespace
- `get_namespace_info <namespace>`: Get detailed information about a namespace
- `list_pods <namespace>`: List all pods in a namespace
- `list_services <namespace>`: List all services in a namespace
- `list_routes <namespace>`: List all routes in a namespace
- `list_configmaps <namespace>`: List all configmaps in a namespace
- `list_secrets <namespace>`: List all secrets in a namespace

#### Administrative Operations
- `get_pod_logs <namespace> <pod_name>`: Get logs from a specific pod
- `describe_resource <namespace> <resource_type> <resource_name>`: Describe a specific resource
- `scale_deployment <namespace> <deployment_name> <replicas>`: Scale a deployment
- `restart_deployment <namespace> <deployment_name>`: Restart a deployment
- `get_cluster_health`: Get overall cluster health information
- `get_resource_usage <namespace>`: Get resource usage information for a namespace

## Security

- Uses token-based authentication for secure cluster access
- Supports RBAC (Role-Based Access Control) permissions
- Validates cluster connectivity before operations

## Requirements

- Python 3.8+
- OpenShift cluster access
- Valid cluster token with appropriate permissions 