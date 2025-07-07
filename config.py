"""
Configuration file for LLMS.txt Generator
Contains constants, model lists, and category mappings
"""

from typing import Dict, List

# OpenRouter API Configuration (Updated January 2025)
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_MODELS = {
    "Free Models": [
        # DeepSeek Models (Latest and Popular)
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat:free",
        "deepseek/deepseek-v3-base:free",
        "deepseek/deepseek-r1-distill-llama-70b:free",
        "deepseek/deepseek-r1-distill-qwen-14b:free",

        # Google Models
        "google/gemini-2.0-flash-exp:free",
        "google/gemma-2-9b-it:free",
        "google/gemma-3-12b-it:free",
        "google/gemma-3-27b-it:free",

        # Meta Models
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.2-1b-instruct:free",

        # Microsoft Models
        "microsoft/phi-3.5-mini-128k-instruct:free",

        # Other Popular Free Models
        "openrouter/cypher-alpha:free",
        "cognitivecomputations/dolphin3.0-mistral-24b:free",
        "qwen/qwen-2.5-7b-instruct:free"
    ],
    "Premium Models": [
        # OpenAI Models
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-4-turbo",
        "openai/gpt-3.5-turbo",

        # Anthropic Models
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-haiku",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-haiku",

        # Google Models
        "google/gemini-pro-1.5",
        "google/gemini-pro",
        "google/gemini-flash-1.5",

        # DeepSeek Premium Models
        "deepseek/deepseek-r1",
        "deepseek/deepseek-v3",
        "deepseek/deepseek-chat",

        # Meta Models
        "meta-llama/llama-3.3-70b-instruct",
        "meta-llama/llama-3.1-405b-instruct",

        # Mistral Models
        "mistralai/mistral-large",
        "mistralai/mistral-medium",

        # Other Premium Models
        "cohere/command-r-plus",
        "perplexity/llama-3.1-sonar-large-128k-online"
    ]
}

# URL Categorization Keywords
CATEGORY_KEYWORDS = {
    "Introduction": [
        "about", "intro", "introduction", "overview", "welcome", "home", 
        "getting-started", "start", "begin", "what-is", "why"
    ],
    "Get started": [
        "quickstart", "quick-start", "setup", "install", "installation", 
        "tutorial", "first-steps", "onboarding", "guide", "how-to"
    ],
    "API Reference": [
        "api", "reference", "docs", "documentation", "endpoints", 
        "methods", "functions", "sdk", "rest", "graphql"
    ],
    "Guides": [
        "guide", "tutorial", "how-to", "example", "examples", 
        "walkthrough", "step-by-step", "learn", "training"
    ],
    "Resources": [
        "resources", "tools", "utilities", "downloads", "assets", 
        "templates", "samples", "community", "support"
    ]
}

# Common LLM Crawler User Agents
LLM_CRAWLERS = [
    "GPTBot",
    "ClaudeBot", 
    "Google-Extended",
    "anthropic-ai",
    "PerplexityBot",
    "ChatGPT-User",
    "CCBot",
    "Claude-Web",
    "Bard",
    "AI2Bot"
]

# Content Processing Settings
MAX_CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
BATCH_SIZE = 20

# AI Description Settings
AI_DESCRIPTION_PROMPT = """
Please provide a concise, informative description (1-2 sentences, max 150 characters) 
for this webpage content. Focus on what information or functionality it provides:

{content}

Description:"""

# Custom CSS for Streamlit
CUSTOM_CSS = """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    
    .download-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
    }
    
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        color: #856404;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
"""

# File Extensions to Check for Markdown Links
MD_EXTENSIONS = [".md", "/index.md", "/README.md"]

# Default Headers for Web Requests
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
