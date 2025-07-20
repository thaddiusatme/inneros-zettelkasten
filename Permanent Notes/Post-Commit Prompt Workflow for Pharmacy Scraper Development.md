

**Type**: 🧠 Fleeting Note  
**Created**: 2025-07-03 13:19  
**Tags**: #fleeting #inbox  #prompt #project #active #dev_workflow #documentation #automation #pharmacy_scraper #2025_roadmap #test_coverage

---

## Thought  
we want to use this prompt anytime we finish a git commit and a feature change

## Context  
git commit. then  update and Adjust this prompt. Keep the general structure and format, just for what we have done ##Prompt input # Pharmacy Scraper:   ## Project Status - **Current Focus**: Perplexity client improvements and documentation - **Module**: Classification system (perplexity_client.py) - **Branch**: feature/independent-pharmacy-filter - **Test Status**: All tests passing (56% coverage for perplexity_client.py) ## Recent Improvements - Fixed failing tests in Perplexity client test suite - Improved test coverage for edge cases and error handling - Enhanced documentation for classify_pharmacy method - Added comprehensive examples and usage patterns - Documented thread safety and performance characteristics ## Current Context - Working in: [src/pharmacy_scraper/classification/perplexity_client.py](cci:7://file:///Users/myung/Downloads/Pharmacy_Scrape/src/pharmacy_scraper/classification/perplexity_client.py:0:0-0:0) - Test coverage: 56% (perplexity_client.py) - Documentation: Recently updated with examples and detailed behavior ## Next Steps 1. Review and improve test coverage for remaining untested code paths 2. Consider adding integration tests for the full classification workflow 3. Update project documentation to reflect recent changes ## Key Files - [src/pharmacy_scraper/classification/perplexity_client.py](cci:7://file:///Users/myung/Downloads/Pharmacy_Scrape/src/pharmacy_scraper/classification/perplexity_client.py:0:0-0:0) - [tests/classification/test_perplexity_client_coverage.py](cci:7://file:///Users/myung/Downloads/Pharmacy_Scrape/tests/classification/test_perplexity_client_coverage.py:0:0-0:0) - [tests/classification/test_perplexity_client_edge_cases.py](cci:7://file:///Users/myung/Downloads/Pharmacy_Scrape/tests/classification/test_perplexity_client_edge_cases.py:0:0-0:0) - [tests/classification/test_perplexity_client_comprehensive.py](cci:7://file:///Users/myung/Downloads/Pharmacy_Scrape/tests/classification/test_perplexity_client_comprehensive.py:0:0-0:0) ## Quick Start ```bash # Run all Perplexity client tests pytest tests/classification/test_perplexity_*.py -v # Check coverage pytest --cov=src/pharmacy_scraper/classification --cov-report=term-missing tests/classification/ # Run specific test file pytest tests/classification/test_perplexity_client_coverage.py -v ## Dependencies - Python 3.9.6+ - Perplexity API (for LLM classification) - OpenAI Python client (Perplexity API wrapper) - Pydantic (data validation) - Pytest (testing) - pytest-cov (coverage reporting) ## Recent Changes - Added comprehensive test coverage for error cases - Improved documentation with examples and behavior details - Enhanced thread safety documentation - Added performance characteristics and usage patterns ##End of Prompt input

## Evergreen test

| Criterion | Yes/No | Note | | Strategic fit with my 2025 goals | Yes | Process improves dev workflow and project documentation | | Unique or insightful idea | Yes | Systematic prompt updates after every commit is uncommon | | Concrete next actions present | Yes | Clear next steps on tests, docs, and coverage | | Reusable reference value | Yes | Format/template can be used for future development cycles |

**Decision** Promote to permanent note

## Permanent note draft

**Title** 

**Why it matters** A structured prompt to capture all context, status, and next steps after each feature commit improves project traceability and onboarding. This discipline supports quality, speeds up handoff, and aligns with scaling and maintainability goals critical for our 2025 roadmap.

**Desired outcome**

- Higher team velocity due to clear, actionable notes after changes
- Reduction in context loss and rework during development cycles
- Improved onboarding and project documentation consistency
- Measurable increase in test coverage and code quality metrics

**Key requirements**

- Use prompt template after every commit impacting a feature or workflow
- Capture current status, recent improvements, context, next steps, and quick start info
- Link key files and commands cleanly
- Keep prompt up-to-date as the single source of module/project status

**Open questions / research**

- Could this be further automated with commit hooks?
- How to integrate this flow into standard team practices?
- What tools best manage/mirror these structured prompts (Notion? Github Discussions?)
- Are developers finding value, or does it add friction?

**Next actions**

- Integrate prompt template into PR/commit checklist
- Develop lightweight script or hook for auto-generation
- Gather feedback after one sprint of use
- Analyze changes in onboarding or context questions from new devs
- Assess test coverage deltas from systematic workflow

