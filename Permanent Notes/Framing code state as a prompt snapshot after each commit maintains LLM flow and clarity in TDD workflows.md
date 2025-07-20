
---

**Type**: 📌 Permanent Note  
**Created**: 2025-06-30  
**Tags**: #permanent #windsurf #llm #tdd #promptdesign #workflow

---

## Core Idea

**Framing your code state as a prompt after each commit enables stable, iterative development with an LLM in flow-based coding.**  
In a Windsurf + TDD workflow, documenting the project state using a structured prompt allows the LLM to continue work without re-explaining context. This supports sustained flow, better test-driven guidance, and better source control over AI co-development.

## Why It Matters

When vibe coding with LLMs, **context is king** — but also fragile. Without a shared state, the LLM forgets prior structure or misinterprets goals. By ritualizing the creation of a prompt snapshot after each commit or major change, you:

- Preserve environment knowledge
    
- Prime the LLM with your working state
    
- Reduce confusion and hallucination
    
- Empower modular improvements and debugging
    

This process also creates _prompt legibility_, so anyone (or any LLM) can jump in with clarity.

## Usage Ritual

Use the `LLM Prompt Snapshot Template` after:

- Each major change or commit
    
- When you shift focus modules or logic
    
- Before asking the LLM for code suggestions, documentation help, or refactors
    

Store the snapshot in a scratch file or as a comment block in a working `.md` file.

## Snapshot Prompt Template

````md
## Prompt input # {Module Title}

## Project Status
- **Current Focus**: {e.g., test coverage, logic refactor, integration}
- **Module**: {filename.py}
- **Branch**: {git-branch}
- **Test Status**: {pass/fail + coverage info}

## Recent Improvements
- {summarize code/test/doc changes}

## Current Context
- Working in: {main file path}
- Test coverage: {percentage}
- Documentation: {level of completeness or key updates}

## Next Steps
1. {planned change}
2. {question for LLM}
3. {optional: refactor or test improvements}

## Key Files
- {relevant source or test files}

## Quick Start
```bash
# Run tests, check coverage, or reproduce bug
````

## Dependencies

- Python {version}
    
- {libraries, API keys, env notes}
    

## Recent Changes

---
## Links  
- Related: [[Vibe Coding Needs Guardrails]], [[TDD Ritual for AI Tools]], [[Perplexity Integration Workflow]]  
- Source: Windsurf Workflow, June 2025  

---

