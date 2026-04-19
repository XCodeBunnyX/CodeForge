# CodeForge 🤖  
> Autonomously solve GeeksforGeeks competitive programming batches using AI

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  
[![Groq API](https://img.shields.io/badge/Powered%20By-Groq%20API-red)](https://groq.com)

---

## Features ✨  

- 🧠 **AI-Powered Code Generation**  
  Uses Groq’s Llama 3.3 70B model to generate optimized solutions.

- 🎯 **Fully Autonomous Workflow**  
  Extracts problems, generates code, and submits solutions automatically.

- 🔄 **Self-Correcting System**  
  Detects CE, RE, WA, TLE, MLE and applies targeted fixes with retries.

- ⚡ **High-Speed Automation**  
  Simulates human-like typing for fast and stealthy execution.

- 🛡️ **Robust Code Processing**  
  Template-aware injection, brace balancing, and cleanup of extra code.

- 📊 **Smart Error Handling**  
  Improves outputs using structured feedback from submissions.

- ⏱️ **Timeout & Stability Control**  
  Handles network/UI delays with safe fallback mechanisms.

---

# CodeForge 🤖

## Quick Start 🚀

### 1. Install Dependencies
```bash
pip install selenium undetected-chromedriver
```

### 2. Setup API Key
- Sign up at https://groq.com  
- Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## How It Works ⚙️

1. Extracts problem data from GeeksforGeeks  
2. Sends structured prompts to AI  
3. Injects code into GFG template  
4. Submits and evaluates results  
5. Retries with fixes if errors occur  

---

## Use Cases 🎯

- Automating GFG problem batches  
- Competitive programming practice  
- Algorithm testing and benchmarking  
- Learning optimized solutions  