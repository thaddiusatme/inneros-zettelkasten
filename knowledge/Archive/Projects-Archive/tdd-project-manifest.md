---
type: permanent
created: 2025-07-27 14:24
status: draft
tags: [project, manifest, tdd, mvp]
visibility: private
---

# TDD Project Manifest - InnerOS AI Integration (Phase 5)

## TDD Philosophy & Approach

### Core TDD Principles
1. **Red-Green-Refactor Cycle**: Every feature starts with a failing test
2. **Test First**: No production code without a failing test
3. **Incremental Development**: Small, testable increments toward MVP
4. **Behavior-Driven Tests**: Tests describe user-visible behavior
5. **Fast Feedback**: Tests run in <3 seconds locally

### Test Pyramid Strategy
- **Unit Tests** (70%): Individual functions, pure logic
- **Integration Tests** (20%): Component interactions, file I/O
- **End-to-End Tests** (10%): Full workflow validation

## MVP Definition - Phase 5 AI Integration

### MVP Success Criteria
```gherkin
Feature: Basic AI Integration
  As a knowledge worker
  I want AI to automatically tag my notes
  So that I can discover connections between ideas

  Scenario: Auto-tag new permanent note
    Given I create a new permanent note about "machine learning fundamentals"
    When I save the note
    Then the system should suggest tags: ["ai", "learning", "technology"]
    And I should be able to accept or modify suggestions

  Scenario: Note summarization
    Given I have a note longer than 500 words
    When I request a summary
    Then I receive a 2-3 sentence summary
    And the summary is stored as note metadata
```

### MVP Scope Boundaries
**IN Scope:**
- Local AI model integration (Ollama)
- Automatic tag generation for permanent notes
- Basic summarization for long notes
- Simple connection suggestions
- Obsidian plugin integration

**OUT of Scope:**
- Multi-user collaboration
- Advanced NLP features
- External API dependencies
- Real-time collaboration
- Mobile app integration

## Test-Driven Development Workflow

### 1. Test Structure
```
tests/
├── unit/
│   ├── test_ai_tagger.py
│   ├── test_summarizer.py
│   └── test_note_processor.py
├── integration/
│   ├── test_ollama_client.py
│   ├── test_obsidian_plugin.py
│   └── test_file_processing.py
└── e2e/
    ├── test_complete_workflow.py
    └── test_ai_features.py
```

### 2. Development Cycle
1. **Write failing test** (Red)
2. **Run test suite** (Confirm failure)
3. **Write minimal code** (Green)
4. **Refactor** (Improve design)
5. **Run tests** (Ensure still green)
6. **Commit** (Atomic commits)

### 3. Test Categories

#### Unit Tests - Core Logic
- Tag extraction algorithms
- Text preprocessing functions
- Configuration validation
- Metadata processing

#### Integration Tests - Component Interaction
- Ollama API communication
- File system operations
- Obsidian plugin API
- Configuration file handling

#### End-to-End Tests - User Workflows
- Complete note processing pipeline
- AI feature user interactions
- Error handling scenarios
- Performance benchmarks

## Testing Infrastructure

### Test Framework Setup
```python
# pytest configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: marks tests as unit (deselect with '-m \"not unit\"')",
    "integration: marks tests as integration",
    "e2e: marks tests as end-to-end",
    "slow: marks tests as slow",
]
```

### Mock Strategy
- **Ollama API**: Mock responses for consistent testing
- **File System**: Use temporary directories
- **Obsidian API**: Stub plugin interfaces
- **Network Calls**: VCR.py for recording/replaying

### Test Data Management
```
tests/fixtures/
├── sample_notes/
│   ├── permanent/
│   ├── fleeting/
│   └── literature/
├── mock_responses/
│   ├── ollama_tags.json
│   └── ollama_summary.json
└── test_configs/
    ├── minimal_config.yaml
    └── full_config.yaml
```

## Development Phases (TDD)

### Phase 5.1: Foundation (Week 1)
**Goal**: Testable AI infrastructure

**Test-Driven Tasks**:
- [ ] Write test for Ollama client initialization
- [ ] Write test for configuration validation
- [ ] Write test for model availability check
- [ ] Write test for basic API health check

**Deliverables**:
- `tests/unit/test_ollama_client.py`
- `tests/integration/test_ai_config.py`
- Working Ollama client with 100% test coverage

### Phase 5.2: Core Features (Week 2)
**Goal**: AI-powered tagging and summarization

**Test-Driven Tasks**:
- [ ] Write test for tag generation from note content
- [ ] Write test for summary generation
- [ ] Write test for tag relevance scoring
- [ ] Write test for note length detection

**Deliverables**:
- `tests/unit/test_ai_tagger.py`
- `tests/unit/test_summarizer.py`
- `tests/integration/test_note_processing.py`
- Feature-complete AI services

### Phase 5.3: Integration (Week 3)
**Goal**: Obsidian plugin integration

**Test-Driven Tasks**:
- [ ] Write test for plugin command registration
- [ ] Write test for settings panel validation
- [ ] Write test for keyboard shortcut handling
- [ ] Write test for note update triggers

**Deliverables**:
- `tests/integration/test_obsidian_plugin.py`
- `tests/e2e/test_complete_workflow.py`
- Fully integrated Obsidian plugin

## Quality Gates

### Pre-commit Hooks
- All tests must pass
- Code coverage ≥ 80%
- Type checking with mypy
- Linting with ruff
- Security scanning with bandit

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml
      - run: mypy src/
      - run: ruff check src/
```

### Performance Benchmarks
- Tag generation: <2 seconds per note
- Summary generation: <5 seconds per 1000 words
- Memory usage: <500MB for typical workload
- Cold start time: <10 seconds

## Risk Mitigation

### Technical Risks
- **AI Model Performance**: Fallback to simpler algorithms
- **Local Resource Limits**: Configurable model size limits
- **Obsidian API Changes**: Version compatibility tests
- **Data Privacy**: All processing stays local

### Testing Risks
- **Flaky Tests**: Retry mechanisms and timeouts
- **Slow Tests**: Parallel execution strategy
- **Complex Setup**: Docker-based test environment
- **Mock Drift**: Regular mock validation tests

## Success Metrics

### Development Metrics
- Test coverage: Target 85%
- Build time: <2 minutes
- Test execution: <30 seconds
- Code review time: <1 day

### User Experience Metrics
- Time to first tag suggestion: <5 seconds
- Tag acceptance rate: >70%
- Summary usefulness rating: >4/5
- Error rate: <1%

### Business Metrics
- Notes processed per day: Target 100+
- User engagement: Daily active usage
- Knowledge discovery: 2x more connections found
- Workflow efficiency: 50% reduction in manual tagging

## Next Steps

1. **Setup Test Environment** (Day 1)
   - Install pytest and dependencies
   - Create initial test structure
   - Configure pre-commit hooks

2. **Write First Failing Test** (Day 1)
   - Test Ollama client initialization
   - Test basic configuration loading

3. **Implement MVP Features** (Weeks 1-3)
   - Follow TDD cycle for each feature
   - Maintain test coverage above 80%
   - Regular refactoring based on test feedback

4. **Integration Testing** (Week 4)
   - End-to-end workflow validation
   - Performance testing
   - User acceptance testing

---

*This manifest is a living document. Update tests and implementation as requirements evolve.*
