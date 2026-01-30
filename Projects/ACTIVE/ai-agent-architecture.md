# InnerOS AI Agent Architecture (Proposed)

> **Goal**: Add "Reasoning & Tool Use" capabilities to InnerOS without heavy frameworks.
> **Philosophy**: Lightweight, file-centric, transparent.

## 1. The Core Concept: "Micro-Agents"

Instead of one giant "General Intelligence" that tries to do everything, we implement small, purpose-built agents that share a common runtime.

**Why?**

- Easier to debug.
- Lower latency.
- Predictable costs.

## 2. The Architecture (Python-Native)

We will use a standard **ReAct (Reason + Act)** loop pattern, implemented with raw OpenAI/Anthropic tool-calling APIs. No heavy `LangChain` or `CrewAI` dependencies required.

### Directory Structure

```text
development/src/ai/
├── agent/
│   ├── core.py           # The loop (LLM -> Tool -> Result -> LLM)
│   ├── tools.py          # Registry of allowed functions (read_note, search_vectors)
│   └── prompts.py        # System prompts
└── agents/               # Specialized implementations
    ├── librarian.py      # "Organize this mess"
    └── researcher.py     # "Read these 5 notes and synthesize"
```

## 3. The "Tool Belt" (What it can do)

The agent needs hands. We expose existing InnerOS functions as tools:

1. **`search_vault(query)`**: (Coming soon with RAG) Find relevant notes.
2. **`read_note(filename)`**: Read content of a specific note.
3. **`create_note(filename, content)`**: Write a new Zettel.
4. **`append_to_daily_log(text)`**: Log actions.

## 4. How You Trigger It (The Interface)

Since InnerOS is file-centric, we can trigger agents via **Magic Files** in the Inbox.

**Example User Action:**
Create file: `knowledge/Inbox/Request: Research AI Agents.md`

```markdown
# Request
Please research the history of autonomous agents.
Check my existing notes on 'Agents' and 'LLMs' first.
Compile a summary in a new permanent note.
```

**System Response:**

1. Daemon sees `Request: *.md`.
2. Spins up `ResearcherAgent`.
3. Agent reads request -> Searches Vault -> Reads Notes -> Writes `Permanent Notes/History of AI Agents.md`.
4. Agent moves Request file to `Archive/Requests/`.

## 5. Implementation Roadmap

### Step 1: The `AgentRuntime` (Base Class)

- Wraps `client.chat.completions.create` (OpenAI/Anthropic).
- Handles the `tools` definition schema automatically.
- Manages the `messages` history (memory).

### Step 2: Tool Registry

- Simple `@tool` decorator to register Python functions.
- Auto-generates the JSON schema for the LLM.

### Step 3: The `Librarian` (First Pilot)

- **Goal**: Look at `Inbox/` and suggest filenames/folders for loose notes.
- **Risk**: Low (it only suggests, doesn't delete).

## 6. Comparison to n8n

| Feature | InnerOS Agent (Python) | n8n Agent |
| :--- | :--- | :--- |
| **Context** | Full access to local vault & RAG | Limited to what you upload/pass |
| **Tools** | Native Python functions | API calls / Code nodes |
| **Cost** | API Tokens only | Hosting + API Tokens |
| **Debug** | Standard Python logs | Visual node debugging |

## 7. Next Steps

1. Create `development/src/ai/agent/` module.
2. Implement `BaseAgent` class.
3. Build the `Librarian` pilot to organize your Inbox.
