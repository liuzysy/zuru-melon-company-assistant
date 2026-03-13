# ZURU Melon Company Assistant Agent - Complete Submission Package

## Table of Contents
1. [Project Overview](#project-overview)
2. [Core Features & Assignment Requirements Alignment](#core-features--assignment-requirements-alignment)
3. [Architecture Overview](#architecture-overview)
4. [Technical Choices & Rationale](#technical-choices--rationale)
5. [Setup & Installation Guide](#setup--installation-guide)
6. [Running the Assistant](#running-the-assistant)
7. [Complete Test Scenarios (Assignment Requirements)](#complete-test-scenarios-assignment-requirements)
8. [Git Repository Setup & Upload Instructions](#git-repository-setup--upload-instructions)
9. [Project Structure](#project-structure)

---

## Project Overview
This repository contains the implementation of an intelligent, agentic AI system designed to act as a ZURU Melon Company Assistant. It functions as a "Company ChatGPT" capable of answering both internal company-related queries and general knowledge questions through an autonomous decision-making process.

---

## Core Features & Assignment Requirements Alignment
The assistant implements all required capabilities as specified in the assignment:

### 1. Query Handling
- ✅ **Retrieve company information from a local knowledge base**: Loads and searches Markdown/text files from the `data/` directory
- ✅ **Use internet search for external or up-to-date details**: Integrates with Serper API for public web search
- ✅ **Fall back to its intrinsic knowledge when appropriate**: Uses the LLM's built-in knowledge for general queries
- ✅ **Decide automatically which source to use**: Agentic router makes autonomous tool selection decisions
- ✅ **Ask clarifying questions when uncertain**: Proactively requests more context for ambiguous queries

### 2. Compliance & Safety
- ✅ **Block or neutralize harmful, inappropriate, or policy-violating queries**: Implements dual-layer safety checks (keyword-based + LLM-based)

### 3. User Interface
- ✅ **Command-Line Interface (CLI)**: Clean, intuitive interactive CLI with progress indicators
- ✅ **Clear instructions**: Complete documentation for installation, configuration, and running

### 4. Implementation
- ✅ **Programming Language**: Python (industry standard for AI/ML)
- ✅ **Frameworks**: LangChain for orchestration, OpenAI SDK for API access
- ✅ **API Access**: Uses the provided OpenRouter API key

---

## Architecture Overview

The system follows a standard Agentic AI architecture with clear separation of concerns:

```text
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface (CLI)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Safety & Compliance Guardrail                    │
│        (Filters harmful/inappropriate queries first)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Router (LLM Brain)                      │
│         (Decides which tool to use based on user query)          │
└────────────────────┬───────────────────┬────────────────────────┘
                     │                   │
         ┌───────────┴───────────┬───────┴───────────┬───────────┐
         ▼                       ▼                   ▼           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────┐ ┌──────────┐
│ Knowledge Base   │  │ Internet Search  │  │ Ask for  │ │ Fallback │
│ Retriever        │  │ (Serper)         │  │ Clarify  │ │ (LLM)    │
└──────────────────┘  └──────────────────┘  └──────────┘ └──────────┘
         │                       │                   │           │
         └───────────────────────┴───────────────────┴───────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Response Generation (LLM)                      │
│        (Synthesizes final answer based on tool results)          │
└─────────────────────────────────────────────────────────────────┘
```


### Key Components
- **`src/config.py`**: Centralized configuration management, loads all settings from environment variables (no hardcoded secrets)
- **`src/safety/guardrail.py`**: Implements safety and compliance checks
- **`src/agent/router.py`**: The "brain" of the agent, makes tool decisions and generates responses
- **`src/agent/executor.py`**: Executes the tools selected by the router
- **`src/knowledge_base/`**: Handles loading, splitting, and retrieving documents from the local knowledge base
- **`src/cli.py`**: The interactive command-line interface

---

## Technical Choices & Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Programming Language** | Python | Industry standard for AI/ML applications, excellent ecosystem for LLM development |
| **LLM Provider** | OpenRouter | Provides access to multiple state-of-the-art models via a unified API |
| **Primary Model** | Meta Llama 3 8B Instruct | Free, high-quality, supports function calling (tool use), no region restrictions |
| **Internet Search** | Serper API | Cost-effective, reliable Google Search API with free tier available |
| **Document Loading** | LangChain | Robust, well-maintained library for document processing and LLM orchestration |
| **Configuration** | Pydantic + `.env` | Type-safe configuration, secrets management following security best practices |

---

## Setup & Installation Guide

### Prerequisites
- Python 3.10 or higher
- `pip` package manager
- A valid OpenRouter API key (provided with the assignment)
- (Optional) A Serper API key for internet search functionality (free tier available at https://serper.dev/)

### Step 1: Clone or Initialize the Repository
```bash
# If you're cloning from GitHub
git clone <your-repository-url>
cd zuru-melon-company-assistant

# Or if you're initializing locally
cd zuru-melon-company-assistant
```

### Step 2: Create and Activate Virtual Environment
```bash
运行
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate virtual environment (Windows)
.venv\Scripts\activate
```