# 📦 Old Files Archive

This folder contains all the **old, experimental, and deprecated files** from the root directory that are no longer needed for the main MCP system.

## 📁 What's Here

### 🔧 **Python Files (Old Versions)**
- **Server Files**: Old MCP server implementations
- **Client Files**: Experimental MCP client versions
- **Host Files**: Deprecated host applications
- **Test Files**: Various testing and demo scripts
- **Utility Files**: Helper scripts and utilities

### 📚 **Documentation Files**
- **README Files**: Old documentation versions
- **Integration Guides**: LLM integration documentation
- **Usage Guides**: MCP usage documentation
- **Project Documentation**: Development documentation

### 🗂️ **Other Files**
- **Configuration Files**: Old config files
- **Log Files**: Server logs
- **Cache Files**: Python cache directories
- **Scripts**: Old utility scripts

## 🚀 **Current Working System**

The **clean, working system** is now organized in the root directory:

- **`mcp_server/`** - Active MCP server components
- **`mcp_client/`** - Working MCP client implementations  
- **`mcp_host/`** - Functional host applications
- **`README.md`** - Main system documentation
- **`requirements.txt`** - Current dependencies
- **`.env`** - Active environment configuration

## 💡 **Why These Files Are Here**

1. **Historical Reference**: Keep for development history
2. **Rollback Option**: Can restore if needed
3. **Learning Material**: Examples of different approaches
4. **Clean Root**: Main directory is now organized and clean

## 🔄 **If You Need to Restore**

```bash
# Restore a specific file
cp old/filename.py ./

# Restore all files (not recommended)
cp old/* ./
```

## ⚠️ **Note**

These files are **not needed** for the current working system. The organized folders (`mcp_server/`, `mcp_client/`, `mcp_host/`) contain all the functional components you need. 