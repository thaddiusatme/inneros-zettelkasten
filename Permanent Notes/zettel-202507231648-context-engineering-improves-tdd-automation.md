---
type: permanent
created: 2025-07-23 16:48
status: draft
tags: ["#zettelkasten", "#automation", "#tdd", "#context-engineering", "#prompt-engineering"]
visibility: private
---

# Context Engineering is Key for TDD-based Zettelkasten Automation

**Insight:** While developing automations for a Zettelkasten using Test-Driven Development (TDD), it becomes clear that effective automation hinges less on perfect prompt engineering and more on robust **context engineering**. Context engineering is the practice of supplying the right metadata and surrounding information to an AI to ensure it can classify, refactor, and connect notes accurately and reliably.

## The Challenge of Automation without Context

When scripting the cleanup and processing of raw, fleeting notes, the primary goal is to surface relevant ideas quickly and reduce manual effort. However, without sufficient context, AI-driven automation can introduce more noise than value. A well-crafted prompt can guide an AI, but it cannot compensate for missing information.

For example, a script designed to auto-tag a note will fail or perform poorly if the note lacks:
-   The source of the idea (e.g., a conversation, an article).
-   Connections to existing concepts in the knowledge base.
-   Clear, atomic thoughts.

## TDD as a Framework for Better Context

Using a TDD approach highlights these context gaps systematically. By writing tests that expect specific outcomes (e.g., a note being correctly tagged or linked), we are forced to define what constitutes a "complete" note.

This leads to defining clear requirements for incoming notes, such as:
-   **Unit tests that flag missing context blocks.**
-   **Metrics to measure the time saved by automation.**
-   **A collection of effective context patterns for different note types.**

Ultimately, the discipline of TDD in a Zettelkasten context shifts the focus from simply writing prompts to building a resilient system that gathers and provides the necessary context for successful automation.

---
*Source: [[fleeting-2025-07-20-tdd-context-code-review-step]]*
