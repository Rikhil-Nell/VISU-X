
---
## Overview

**VISU Agent** is an advanced conversational AI agent designed for asynchronous interactions with users. It leverages the power of the `pydantic_ai` framework to simplify structured workflows, integrating state-of-the-art large language models (LLMs) and vector search for enriched conversational memory. 

This repository marks the initial development of the VISU Agent, transitioning from a previous implementation using `LangChain`. The switch to `pydantic_ai` was motivated by the need for a more structured and declarative approach to handling agent workflows, tools, and dependencies.

---

## Features in the First Commit

### Core Functionality
1. **Agent Implementation**:
   - Utilizes `pydantic_ai` for defining the VISU Agent.
   - Integrated with Groq’s **Llama 3.3 70B Versatile** model for LLM inference.

2. **Memory System**:
   - Sliding window memory for recent conversations.
   - Persistent vector-based memory using Supabase for long-term retrieval.

3. **Tooling**:
   - A vector search tool for retrieving past conversations based on query embeddings generated using OpenAI’s `text-embedding-ada-003` model.

4. **Database Integration**:
   - Supabase is used as the backend for storing user data, conversation history, and embeddings.

5. **Logging and Monitoring**:
   - Live integration with **Logfire** for real-time logging.
   - Basic logging of execution times and error handling.

---

### Transition from `LangChain` to `pydantic_ai`

The decision to transition from `LangChain` to `pydantic_ai` was driven by:
- **Modularity**: `pydantic_ai` offers a clearer separation between the agent logic and tools, which makes it easier to maintain and expand.
- **Validation**: Strong data validation features in `pydantic_ai` reduce runtime errors and streamline tool definitions.
- **Simplified Async Workflows**: `pydantic_ai` natively supports asynchronous programming, which is essential for scaling the agent.

---

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the root directory and set the following:
   ```env
   GROQ_API_KEY=your_groq_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   LOGFIRE_API_KEY=your_logfire_api_key
   ```

3. **Run the Agent**:
   Execute the agent by running:
   ```bash
   python visu_agent.py
   ```

---

## Current Limitations
- **Embedding Cost**: Relying on external API calls for embedding generation may lead to increased costs at scale.
- **Monitoring Dashboards**: Logfire integration is limited to the live dashboard for now. Custom dashboards are yet to be implemented.

---

## Changelog

### Initial Commit (v0.1.0)
- Implemented VISU Agent with `pydantic_ai`.
- Added vector search for conversation retrieval.
- Integrated OpenAI embedding generation and Supabase for persistent memory.
- Basic Logfire integration for real-time monitoring.

---

## Future Enhancements
1. Implement custom Logfire dashboards for improved monitoring.
2. Add support for multiple personas.
3. Optimize vector search for faster query resolution.
4. Enhance embedding cost efficiency by exploring local embedding generation.
