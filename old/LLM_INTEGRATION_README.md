# OpenShift MCP Server with LLM Integration

This enhanced version of the OpenShift MCP Server integrates multiple Large Language Models (LLMs) to provide intelligent OpenShift cluster management capabilities.

## 🚀 Features

### **OpenShift Management Tools (15 tools)**
- Cluster connection and management
- Namespace, pod, service, and route management
- Resource monitoring and scaling
- Configuration and secret management

### **LLM Integration Tools (5 tools)**
- **`ask_llm`** - Ask questions about OpenShift management
- **`intelligent_cluster_analysis`** - AI-powered cluster health analysis
- **`get_troubleshooting_help`** - AI-powered troubleshooting assistance
- **`get_llm_providers`** - View available LLM providers
- **`test_llm_connection`** - Test LLM provider connections

## 🤖 Supported LLM Providers

### 1. **Google Gemini (Default)**
- **Model**: `gemini-1.5-flash`
- **Features**: Fast, cost-effective, excellent for technical content
- **Configuration**: Set `GEMINI_API_KEY` in your `.env` file

### 2. **OpenAI ChatGPT**
- **Models**: `gpt-4`, `gpt-3.5-turbo`
- **Features**: Advanced reasoning, extensive knowledge
- **Configuration**: Set `OPENAI_API_KEY` in your `.env` file

### 3. **Anthropic Claude**
- **Models**: `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **Features**: Safety-focused, excellent for complex analysis
- **Configuration**: Set `ANTHROPIC_API_KEY` in your `.env` file

### 4. **Custom LLM Providers**
- **Features**: Support for any LLM with REST API
- **Configuration**: Set `CUSTOM_LLM_API_KEY` and `CUSTOM_LLM_BASE_URL`

## 🛠️ Installation & Setup

### 1. **Install Dependencies**
```bash
# Install LLM integration packages
pip install google-generativeai openai anthropic requests websockets
```

### 2. **Environment Configuration**
Copy `env.example` to `.env` and configure your API keys:

```bash
# Required: Gemini (default)
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: OpenAI
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# Optional: Claude
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229

# Optional: Custom LLM
CUSTOM_LLM_API_KEY=your-custom-key
CUSTOM_LLM_BASE_URL=https://your-llm-api.com
```

### 3. **Get API Keys**

#### **Google Gemini**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

#### **OpenAI**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key to your `.env` file

#### **Anthropic Claude**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create a new API key
3. Copy the key to your `.env` file

## 🚀 Usage

### **Start the Enhanced Server**
```bash
python openshift_mcp_server_with_llm.py
```

### **Test LLM Integration**
```bash
python demo_llm_integration.py
```

### **Run Individual Tests**
```bash
python llm_integration.py
```

## 🎯 LLM Tool Examples

### **1. Ask LLM Questions**
```python
# Ask about OpenShift best practices
result = await call_tool("ask_llm", {
    "question": "What are the best practices for managing OpenShift namespaces?",
    "provider": "gemini"  # Optional: specify provider
})
```

### **2. Intelligent Cluster Analysis**
```python
# Get AI-powered cluster analysis
result = await call_tool("intelligent_cluster_analysis", {
    "namespace": "my-namespace",  # Optional
    "provider": "claude"  # Optional
})
```

### **3. AI-Powered Troubleshooting**
```python
# Get troubleshooting help
result = await call_tool("get_troubleshooting_help", {
    "issue_description": "My pods are stuck in Pending state",
    "error_messages": "0/1 nodes are available: 1 node(s) had taints",
    "provider": "openai"  # Optional
})
```

### **4. Check LLM Status**
```python
# Get available providers
result = await call_tool("get_llm_providers", {})

# Test connections
result = await call_tool("test_llm_connection", {
    "provider": "gemini"  # Optional: test specific provider
})
```

## 🔧 Configuration Options

### **Model Customization**
```bash
# Gemini
GEMINI_MODEL=gemini-1.5-flash
GEMINI_MAX_TOKENS=2048
GEMINI_TEMPERATURE=0.7

# OpenAI
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2048
OPENAI_TEMPERATURE=0.7

# Claude
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=2048
CLAUDE_TEMPERATURE=0.7
```

### **Custom LLM API Format**
Your custom LLM should support this API format:

```json
POST /generate
{
  "prompt": "Your question here",
  "model": "model-name",
  "max_tokens": 2048,
  "temperature": 0.7
}

Response:
{
  "response": "LLM response content",
  "content": "Alternative response field"
}
```

## 🧪 Testing & Validation

### **Test LLM Connections**
```bash
# Test all providers
python -c "
import asyncio
from llm_integration import llm_manager
async def test():
    results = await llm_manager.test_all_connections()
    print('Connection Results:', results)
asyncio.run(test())
"
```

### **Test Response Generation**
```bash
# Test with default provider
python -c "
import asyncio
from llm_integration import llm_manager
async def test():
    response = await llm_manager.generate_response('Hello, how are you?')
    print('Response:', response.content)
    print('Provider:', response.provider)
    print('Model:', response.model)
asyncio.run(test())
"
```

## 🔒 Security Considerations

### **API Key Security**
- Never commit API keys to version control
- Use environment variables or secure secret management
- Rotate API keys regularly
- Monitor API usage and costs

### **Network Security**
- Use HTTPS for all API communications
- Implement rate limiting if needed
- Monitor for unusual API usage patterns

### **Data Privacy**
- Be aware of what data is sent to LLM providers
- Review provider privacy policies
- Consider data residency requirements

## 🚨 Troubleshooting

### **Common Issues**

#### **1. LLM Connection Failed**
```bash
# Check API key
echo $GEMINI_API_KEY

# Test connection
python llm_integration.py
```

#### **2. Rate Limiting**
```bash
# Reduce request frequency
# Check provider quotas
# Implement retry logic
```

#### **3. Model Not Available**
```bash
# Check model names
# Verify API access
# Update to supported models
```

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance & Cost

### **Response Times**
- **Gemini**: ~1-3 seconds
- **OpenAI**: ~2-5 seconds
- **Claude**: ~3-6 seconds
- **Custom**: Depends on implementation

### **Cost Optimization**
- Use appropriate models for tasks
- Implement caching for repeated questions
- Monitor token usage
- Set reasonable max_token limits

## 🔮 Future Enhancements

### **Planned Features**
- **Multi-modal support** (images, diagrams)
- **Conversation memory** across sessions
- **Custom prompt templates**
- **Advanced caching strategies**
- **Provider failover** and load balancing

### **Integration Possibilities**
- **GitHub Copilot** integration
- **VS Code extensions**
- **CI/CD pipeline integration**
- **Monitoring and alerting**

## 📚 Additional Resources

### **Documentation**
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)

### **Examples & Tutorials**
- [LLM Integration Examples](examples/)
- [Best Practices Guide](docs/best-practices.md)
- [Security Guidelines](docs/security.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Areas for Contribution**
- Additional LLM provider support
- Enhanced error handling
- Performance optimizations
- New intelligent features
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎉 Ready to experience intelligent OpenShift management with AI-powered insights!**

For support and questions, please open an issue in our repository.
