#!/usr/bin/env python3
"""
LLM Integration Module for OpenShift MCP Server

Supports multiple LLM providers:
- Google Gemini (default)
- OpenAI ChatGPT
- Anthropic Claude
- Custom LLMs via API endpoints
"""

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai
import openai
import anthropic
import requests
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    CUSTOM = "custom"

@dataclass
class LLMResponse:
    """Standardized LLM response format."""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    error: Optional[str] = None

@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    timeout: int = 30

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider_name = config.provider.value
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        """Generate response from the LLM."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to the LLM provider."""
        pass

class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model)
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        """Generate response using Gemini."""
        start_time = time.time()
        
        try:
            # Combine context and prompt
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.text,
                provider=self.provider_name,
                model=self.config.model,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.config.model,
                error=str(e)
            )
    
    async def test_connection(self) -> bool:
        """Test Gemini connection."""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                "Hello, this is a test message.",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            return True
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

class OpenAIProvider(BaseLLMProvider):
    """OpenAI ChatGPT provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        """Generate response using OpenAI."""
        start_time = time.time()
        
        try:
            # Combine context and prompt
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant with access to OpenShift cluster management tools."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.config.model,
                tokens_used=response.usage.total_tokens if response.usage else None,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.config.model,
                error=str(e)
            )
    
    async def test_connection(self) -> bool:
        """Test OpenAI connection."""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False

class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        """Generate response using Claude."""
        start_time = time.time()
        
        try:
            # Combine context and prompt
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens or 1000,
                temperature=self.config.temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=response.content[0].text,
                provider=self.provider_name,
                model=self.config.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.config.model,
                error=str(e)
            )
    
    async def test_connection(self) -> bool:
        """Test Claude connection."""
        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception as e:
            logger.error(f"Claude connection test failed: {e}")
            return False

class CustomLLMProvider(BaseLLMProvider):
    """Custom LLM provider via API endpoints."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.base_url:
            raise ValueError("Custom LLM requires base_url configuration")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        """Generate response using custom LLM API."""
        start_time = time.time()
        
        try:
            # Combine context and prompt
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Prepare request payload
            payload = {
                "prompt": full_prompt,
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            # Make API request
            response = await asyncio.to_thread(
                requests.post,
                f"{self.config.base_url}/generate",
                json=payload,
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            response_time = time.time() - start_time
            
            return LLMResponse(
                content=result.get("response", result.get("content", "")),
                provider=self.provider_name,
                model=self.config.model,
                response_time=response_time
            )
            
        except Exception as e:
            logger.error(f"Custom LLM API error: {e}")
            return LLMResponse(
                content="",
                provider=self.provider_name,
                model=self.config.model,
                error=str(e)
            )
    
    async def test_connection(self) -> bool:
        """Test custom LLM connection."""
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{self.config.base_url}/health",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Custom LLM connection test failed: {e}")
            return False

class LLMManager:
    """Manages multiple LLM providers."""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.setup_providers()
    
    def setup_providers(self):
        """Setup available LLM providers from environment variables."""
        
        # Gemini (default)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            gemini_config = LLMConfig(
                provider=LLMProvider.GEMINI,
                api_key=gemini_key,
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "2048")),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
            )
            self.providers["gemini"] = GeminiProvider(gemini_config)
            self.default_provider = "gemini"
            logger.info("Gemini provider configured as default")
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai_config = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                base_url=os.getenv("OPENAI_BASE_URL"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2048")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            )
            self.providers["openai"] = OpenAIProvider(openai_config)
            logger.info("OpenAI provider configured")
        
        # Claude
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            claude_config = LLMConfig(
                provider=LLMProvider.CLAUDE,
                api_key=claude_key,
                model=os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229"),
                max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "2048")),
                temperature=float(os.getenv("CLAUDE_TEMPERATURE", "0.7"))
            )
            self.providers["claude"] = ClaudeProvider(claude_config)
            logger.info("Claude provider configured")
        
        # Custom LLM
        custom_key = os.getenv("CUSTOM_LLM_API_KEY")
        custom_url = os.getenv("CUSTOM_LLM_BASE_URL")
        if custom_key and custom_url:
            custom_config = LLMConfig(
                provider=LLMProvider.CUSTOM,
                api_key=custom_key,
                model=os.getenv("CUSTOM_LLM_MODEL", "custom"),
                base_url=custom_url,
                max_tokens=int(os.getenv("CUSTOM_LLM_MAX_TOKENS", "2048")),
                temperature=float(os.getenv("CUSTOM_LLM_TEMPERATURE", "0.7"))
            )
            self.providers["custom"] = CustomLLMProvider(custom_config)
            logger.info("Custom LLM provider configured")
        
        if not self.providers:
            logger.warning("No LLM providers configured!")
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test connections to all configured providers."""
        results = {}
        for name, provider in self.providers.items():
            results[name] = await provider.test_connection()
        return results
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        provider: Optional[str] = None
    ) -> LLMResponse:
        """Generate response using specified or default provider."""
        
        # Determine provider to use
        if provider and provider in self.providers:
            selected_provider = provider
        elif self.default_provider:
            selected_provider = self.default_provider
        else:
            return LLMResponse(
                content="",
                provider="none",
                model="none",
                error="No LLM provider available"
            )
        
        # Generate response
        return await self.providers[selected_provider].generate_response(prompt, context)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())
    
    def get_default_provider(self) -> Optional[str]:
        """Get the default provider name."""
        return self.default_provider

# Global LLM manager instance
llm_manager = LLMManager()

async def test_llm_integration():
    """Test the LLM integration."""
    print("🧪 Testing LLM Integration...")
    print(f"Available providers: {llm_manager.get_available_providers()}")
    print(f"Default provider: {llm_manager.get_default_provider()}")
    
    # Test connections
    print("\n🔗 Testing connections...")
    connection_results = await llm_manager.test_all_connections()
    for provider, status in connection_results.items():
        print(f"  {provider}: {'✅' if status else '❌'}")
    
    # Test response generation
    if llm_manager.get_default_provider():
        print(f"\n🤖 Testing response generation with {llm_manager.get_default_provider()}...")
        test_prompt = "Hello! Can you help me manage my OpenShift cluster?"
        response = await llm_manager.generate_response(test_prompt)
        
        if response.error:
            print(f"❌ Error: {response.error}")
        else:
            print(f"✅ Response: {response.content[:100]}...")
            print(f"   Provider: {response.provider}")
            print(f"   Model: {response.model}")
            print(f"   Response time: {response.response_time:.2f}s")
    
    print("\n🎉 LLM Integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_llm_integration())
