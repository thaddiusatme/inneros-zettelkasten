# ADR-0001 Default model provider policy

Status: Proposed
Date: 2025-10-26

## Context

We run local first. Cloud models add cost and keys.

## Decision

- Default provider is local Ollama.
- Enable cloud with `USE_CLOUD=1`.
- Respect `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` only when cloud is enabled.

## Consequences

- Predictable cost and latency offline.
- Slightly lower quality on some tasks unless cloud is enabled.
