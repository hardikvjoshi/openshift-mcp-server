# 🔌 MCP Client Folder

This folder contains various **Model Context Protocol (MCP) Clients** for connecting to the OpenShift MCP server.

## 📁 Contents

- **`working_mcp_client.py`** - Working MCP client with proper protocol implementation
- **`direct_mcp_client.py`** - Direct client that simulates MCP tools
- **`real_mcp_client.py`** - Real MCP client with subprocess communication
- **`enhanced_mcp_client.py`** - Enhanced client with service layer
- **`simple_mcp_client.py`** - Simple client for basic testing

## 🚀 Purpose

MCP clients connect to the MCP server to:
- Execute OpenShift management tools
- Use LLM integration features
- Provide programmatic access to cluster operations

## 🔧 How to Use

### Working MCP Client (Recommended)
```bash
cd mcp_client
source ../.venv/bin/activate
python working_mcp_client.py
```

### Direct MCP Client (Simplified)
```bash
cd mcp_client
source ../.venv/bin/activate
python direct_mcp_client.py
```

## 📊 Status

✅ **working_mcp_client.py**: MCP protocol implementation
✅ **direct_mcp_client.py**: Direct tool execution (working)
⚠️ **Other clients**: Experimental/prototype versions

## 🔗 Architecture

```
MCP Client → MCP Protocol → MCP Server → OpenShift Cluster
     ↓
User Interface
```

## 💡 Note

The **working_mcp_client.py** is the most complete implementation, but **direct_mcp_client.py** provides the most reliable tool execution by bypassing the MCP protocol complexity.
