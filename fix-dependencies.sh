#!/bin/bash

# Quick fix script to add missing dependencies to requirements.txt

echo "🔧 Adding missing dependencies to requirements.txt..."

# Add aiohttp to backend requirements
echo "aiohttp==3.9.1" >> Automated-AI-Messaging-Tool-Backend/requirements.txt

# Add any other missing dependencies that might be needed
echo "httpx==0.25.2" >> Automated-AI-Messaging-Tool-Backend/requirements.txt
echo "asyncio==3.4.3" >> Automated-AI-Messaging-Tool-Backend/requirements.txt

echo "✅ Dependencies added to requirements.txt"
echo "📋 Updated requirements.txt:"
cat Automated-AI-Messaging-Tool-Backend/requirements.txt
