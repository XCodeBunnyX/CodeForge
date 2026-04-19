# CodeForge 🤖

> Autonomously solve GeeksforGeeks competitive programming batches using AI

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq API](https://img.shields.io/badge/Powered%20By-Groq%20API-red)](https://groq.com)

## Features ✨

- 🧠 **AI-Powered**: Uses Groq's Llama 3.3 70B model for intelligent code generation
- 🎯 **Autonomous**: End-to-end problem solving without human intervention
- 🔄 **Self-Correcting**: Automatically analyzes failures and regenerates fixes
- ⚡ **Fast**: Human-like typing at 8000 WPM for stealthy automation
- 🛡️ **Robust**: Template-aware injection, helper class detection, brace balancing
- 📊 **Intelligent**: Error classification (CE/RE/WA/TLE/MLE) with targeted fixes
- ⏱️ **Timeout-Safe**: Network & UI timeouts with graceful fallbacks

## Quick Start 🚀

### 1. Install Dependencies
```bash
pip install selenium undetected-chromedriver openai python-dotenv webdriver-manager
```

### 2. Get Groq API Key
- Sign up free at [groq.com](https://groq.com)
- Create `.env` file: