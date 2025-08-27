# 🖥️ MCP Server Folder

This folder contains the **Model Context Protocol (MCP) Server** for OpenShift cluster management.

## 📁 Contents

- **`openshift_mcp_server_with_llm.py`** - Main MCP server with LLM integration
- **`openshift_cluster.py`** - OpenShift cluster management class
- **`llm_integration.py`** - LLM integration module (Gemini, OpenAI, Claude)
- **`requirements.txt`** - Python dependencies
- **`.env`** - Environment variables (cluster credentials, API keys)
- **`env.example`** - Template for environment variables

## 🚀 Purpose

The MCP server provides 20 tools for OpenShift management:
- **15 OpenShift Tools**: Namespace, pod, service, route management
- **5 LLM Tools**: AI-powered cluster analysis and troubleshooting

## 🔧 How to Run

```bash
cd mcp_server
source ../.venv/bin/activate
python openshift_mcp_server_with_llm.py
```

## 🔗 Dependencies

- OpenShift cluster credentials in `.env`
- LLM API keys (Gemini, OpenAI, Claude)
- Python virtual environment with dependencies installed

## 📊 Status

✅ **Server**: Running and ready for MCP client connections
✅ **OpenShift**: Connected to cluster
✅ **LLM**: Gemini integration working
✅ **Tools**: All 20 tools available and functional
