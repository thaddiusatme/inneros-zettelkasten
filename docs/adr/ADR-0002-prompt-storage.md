# ADR-0002 Prompt storage and versioning
 
 Status: Proposed
 Date: 2025-10-26

## Context
 
 Prompts live inside code, hard to audit or tweak.

## Decision
 
 - Store human readable prompts under `docs/prompts/`.
 - Version with semver in file headers.
 - Code loads prompts via helper that resolves path or falls back to inline defaults.

## Consequences
 
 - Easy to review and update prompts.
 - Slight indirection in code.
