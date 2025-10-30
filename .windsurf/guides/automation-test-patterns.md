# Automation Test Patterns Guide

**Created**: 2025-10-30  
**Source**: P2-4 Medium Complexity Test Fixes (178/178 = 100%)  
**Purpose**: Reusable patterns for fixing automation tests  
**Average Fix Time**: 14.3 minutes per test

---

## Pattern Index

1. [YAML Wikilink Preservation](#1-yaml-wikilink-preservation)
2. [Date Mocking](#2-date-mocking)
3. [Logging Assertions](#3-logging-assertions)
4. [Error Handling](#4-error-handling)
5. [Integration with Cache](#5-integration-with-cache)
6. [Fixture Configuration](#6-fixture-configuration)

---

## 1. YAML Wikilink Preservation

### Problem Signature
**Error Pattern**:
```python
AssertionError: assert 'transcript_file: [[youtube-video-2025-10-18]]' == 
'transcript_file: \'[[youtube-video-2025-10-18]]\''
```

**Recognition**:
- Test expects raw wikilink `[[...]]` in YAML
- Actual output has quotes around wikilink `'[[...]]'`
- Occurs after `yaml.dump()` operations
- Breaks wikilink parsing in downstream systems

### Root Cause
Python's YAML dumper adds quotes to strings containing special characters like `[` and `]` to ensure valid YAML syntax.

### Solution Template
```python
import yaml

class WikiLinkRepresenter:
    """Custom YAML representer that preserves wikilink syntax without quotes."""
    
    @staticmethod
    def represent_wikilink_str(dumper, data):
        """Represent strings as plain scalars when they contain wikilinks."""
        if '[[' in data and ']]' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
        return dumper.represent_str(data)

# Register the custom representer
yaml.add_representer(str, WikiLinkRepresenter.represent_wikilink_str)

# Now yaml.dump() will preserve wikilinks:
frontmatter = {
    'title': 'My Note',
    'transcript_file': '[[youtube-video-2025-10-18]]'
}
result = yaml.dump(frontmatter, default_flow_style=False)
# Output: transcript_file: [[youtube-video-2025-10-18]]  ✅ No quotes!
```

### When to Use
- YAML dumping operations that include wikilinks
- Frontmatter updates with `[[note-name]]` references
- Any serialization preserving Obsidian/wiki-style links

### Real Example (P2-4.1)
```python
# Before: Quotes added by YAML dumper
'transcript_file: \'[[youtube-dQw4w9WgXcQ-2025-10-18]]\''

# After: Custom representer preserves raw syntax
'transcript_file: [[youtube-dQw4w9WgXcQ-2025-10-18]]'
```

### Duration: 25 minutes
**Breakdown**: 12 min RED analysis + 8 min GREEN implementation + 5 min REFACTOR

---

## 2. Date Mocking

### Problem Signature
**Error Pattern**:
```python
AssertionError: assert '2025-11-01' == '2025-10-18'
# Test expected fixed date but got today's date
```

**Recognition**:
- Test assertions fail with current date instead of expected date
- Code uses `datetime.now()` or `datetime.datetime.now()`
- Tests need deterministic date values
- Timestamps in assertions don't match

### Root Cause
Production code calls `datetime.now()` which returns current system time, making tests non-deterministic.

### Solution Template
```python
from unittest.mock import MagicMock, patch
from datetime import datetime

@patch("src.automation.feature_handlers.datetime")
def test_with_fixed_date(mock_datetime):
    """Test with mocked date for deterministic results."""
    
    # Create mock datetime that returns fixed date
    mock_dt = MagicMock()
    mock_dt.now.return_value = datetime(2025, 10, 18, 0, 0, 0)
    
    # Replace datetime.datetime with our mock
    mock_datetime.datetime = mock_dt
    
    # CRITICAL: Allow datetime() constructor to work normally
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    
    # Now code will get fixed date from datetime.now()
    result = my_function()
    assert result['created'] == '2025-10-18'  ✅
```

### Diagnostic Questions
1. Does the test assertion include a date value?
2. Does production code call `datetime.now()` or similar?
3. Does the error show today's date vs a fixed date?
4. Is the date dynamically generated?

### Alternative: freeze_time
```python
from freezegun import freeze_time

@freeze_time("2025-10-18")
def test_with_frozen_time():
    """Simpler approach using freeze_time decorator."""
    result = my_function()
    assert result['created'] == '2025-10-18'  ✅
```

### When to Use
- **Mock datetime directly**: When you need fine control or can't add dependencies
- **Use freeze_time**: When available and you want simplicity

### Real Example (P2-4.2)
```python
# Test expected: 2025-10-18
# Got: 2025-10-30 (current date)

# Fix: Mock datetime at correct module path
@patch("src.automation.feature_handlers.datetime")
def test_handler_generates_transcript_wikilink(mock_datetime, ...):
    mock_dt = MagicMock()
    mock_dt.now.return_value = datetime(2025, 10, 18, 0, 0)
    mock_datetime.datetime = mock_dt
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    # ... rest of test
```

### Duration: 8 minutes (fastest!)
**Breakdown**: 3 min RED + 3 min GREEN + 2 min REFACTOR

---

## 3. Logging Assertions

### Problem Signature
**Error Pattern**:
```python
AssertionError: Expected log message "Cache HIT: video123" not found
# OR
AttributeError: 'function' object has no attribute 'records'
```

**Recognition**:
- Test needs to verify log output
- Trying to capture logger.info/warning/error calls
- Manual log capture attempts failing
- Need to assert on log messages/levels

### Root Cause
Tests trying to verify logging behavior without proper log capture mechanism.

### Solution Template
```python
import logging

def test_logging_with_caplog(caplog):
    """Use pytest's caplog fixture to capture log output."""
    
    # Set log level (caplog captures WARNING+ by default)
    caplog.set_level(logging.INFO)
    
    # Run code that logs
    result = my_function()
    
    # Assert on log messages
    assert "Cache HIT: video123" in caplog.text
    
    # OR check specific records
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "INFO"
    assert "Cache HIT" in caplog.records[0].message
    
    # OR use any() for pattern matching
    assert any("Cache HIT" in record.message for record in caplog.records)
```

### caplog Fixture Features
```python
# Access log output
caplog.text            # Full log output as string
caplog.records         # List of LogRecord objects
caplog.record_tuples   # [(logger_name, level, message), ...]

# LogRecord attributes
record.levelname       # 'INFO', 'WARNING', 'ERROR', etc.
record.message         # The formatted message
record.name            # Logger name
record.funcName        # Function that logged
```

### When to Use
- Verifying log messages in tests
- Asserting on log levels (INFO, WARNING, ERROR)
- Testing error handling that logs
- Validating diagnostic output

### Real Example (P2-4.3)
```python
def test_integration_with_youtube_feature_handler(caplog, handler_config, ...):
    """Test cache behavior logs correctly."""
    caplog.set_level(logging.INFO)
    
    handler = YouTubeFeatureHandler(config=handler_config)
    handler._fetch_transcript("video123")
    
    # Verify cache HIT was logged
    assert "Cache HIT: video123 - no API call needed!" in caplog.text
```

### Duration: 20 minutes
**Breakdown**: 8 min RED + 8 min GREEN + 4 min REFACTOR

---

## 4. Error Handling

### Problem Signature
**Error Pattern**:
```python
AssertionError: Expected 'success' to be True
# OR
AttributeError: 'Mock' object has no attribute 'method_name'
# Test tries to verify graceful failure but mocks break too early
```

**Recognition**:
- Test expects error handling/graceful degradation
- Mocking shared utilities causes early failure
- Test never reaches the error handling code
- Wrong-level patching breaks execution path

### Root Cause
**Wrong-Level Mocking**: Patching shared utilities (like `parse_frontmatter`) breaks ALL callers, not just the target behavior. Need to patch specific handler methods instead.

### Solution Template
```python
from unittest.mock import patch

def test_graceful_error_handling(handler_config, temp_vault):
    """Test error handling with targeted method patching."""
    
    # ❌ WRONG: Patches shared utility, breaks everything
    # with patch("src.utils.frontmatter.parse_frontmatter", return_value=None):
    
    # ✅ CORRECT: Patch specific handler method
    handler = YouTubeFeatureHandler(config=handler_config)
    
    with patch.object(handler, "_add_transcript_links_to_note", return_value=False):
        # This isolates the error - only link adding fails
        result = handler.handle(event)
        
        # Verify graceful degradation
        assert result['success'] is True
        assert result.get('transcript_link_added') is False
        # Handler continued despite link failure
```

### Key Principle
**Patch at the Right Level**:
- ✅ **DO**: `patch.object(handler, "method_name")` - Targets specific instance
- ❌ **DON'T**: `patch("shared.utility.function")` - Breaks everything using it

### Diagnostic Questions
1. Does the test patch a shared utility function?
2. Does the error happen BEFORE the code being tested?
3. Is the mock too broad (affects multiple code paths)?
4. Can you target a specific method on the handler instead?

### Real Example (P2-4.4)
```python
# BEFORE: Wrong-level patching
@patch("src.utils.frontmatter.parse_frontmatter", return_value=None)
def test_handler_handles_linking_failure_gracefully(mock_parse, ...):
    handler = YouTubeFeatureHandler(config=handler_config)
    # ❌ Breaks immediately - handler.__init__ calls parse_frontmatter!

# AFTER: Targeted patching
def test_handler_handles_linking_failure_gracefully(handler_config, ...):
    handler = YouTubeFeatureHandler(config=handler_config)
    
    with patch.object(handler, "_add_transcript_links_to_note", return_value=False):
        result = handler.handle(event)
        # ✅ Only link adding fails, rest continues
        assert result['success'] is True
```

### Duration: 8 minutes (fastest!)
**Breakdown**: 5 min RED + 3 min GREEN

---

## 5. Integration with Cache

### Problem Signature
**Error Pattern**:
```python
AssertionError: Expected 'fetch_with_retry' to have been called once. 
Called 0 times.
```

**Recognition**:
- Integration test expects API call
- Cache layer returns hit, preventing API call
- Mock never called because of cache
- Test log shows "Cache HIT" message

### Root Cause
Cache layer returns data before reaching the mocked API call. Test needs to force cache miss to verify integration path.

### Solution Template
```python
from unittest.mock import patch

def test_integration_with_cache_layer(handler_config):
    """Test integration by forcing cache behavior."""
    
    handler = SomeHandler(config=handler_config)
    
    # Force cache miss to test API integration
    with patch.object(handler.cache, "get", return_value=None):
        with patch.object(handler.api_client, "fetch_data") as mock_fetch:
            mock_fetch.return_value = {"data": "test"}
            
            result = handler.process("item123")
            
            # Now the integration path is tested
            mock_fetch.assert_called_once()
            assert result == {"data": "test"}
```

### Pattern: Nested Mocking
```python
# Outer mock: Control cache behavior
with patch.object(handler.cache, "get", return_value=None):
    # Inner mock: Verify integration call
    with patch.object(handler.api, "method") as mock_api:
        # Test now exercises the integration path
        result = handler.process(...)
```

### When to Use
- Integration tests with caching layers
- Testing fallback/retry logic
- Verifying API call patterns
- Cache miss scenarios

### Real Example (P2-4.5)
```python
def test_integration_with_youtube_feature_handler(handler_config, ...):
    """Test rate limit integration with cache disabled."""
    handler = YouTubeFeatureHandler(config=handler_config)
    
    # Force cache miss to test rate limit integration
    with patch.object(handler.transcript_cache, "get", return_value=None):
        with patch.object(handler.rate_limit_handler, "fetch_with_retry") as mock_retry:
            mock_retry.return_value = [{"text": "transcript"}]
            
            result = handler._fetch_transcript("video123")
            
            mock_retry.assert_called_once()  # ✅ Now called!
            assert result == [{"text": "transcript"}]
```

### Duration: 15 minutes
**Breakdown**: 8 min RED + 5 min GREEN + 2 min REFACTOR

---

## 6. Fixture Configuration

### Problem Signature
**Error Pattern**:
```python
ERROR at setup of test_name
fixture 'fixture_name' not found
```

**Recognition**:
- Test can't find pytest fixtures
- Function at module level but uses class fixtures
- Incorrect `self` parameter placement
- Scope mismatch (class fixture in module function)

### Root Cause
**Scope Mismatch**: Module-level functions can't access class-scoped fixtures. Test structure must match fixture scope.

### Solution Template
```python
import pytest

class TestSuite:
    @pytest.fixture
    def my_fixture(self):
        """Class-scoped fixture."""
        return "value"
    
    # ❌ WRONG: Module-level function can't access class fixture
    # def test_something(my_fixture):
    #     assert my_fixture == "value"
    
    # ✅ CORRECT: Class method accesses class fixture
    def test_something(self, my_fixture):
        assert my_fixture == "value"
```

### Diagnostic Questions
1. **Where is the fixture defined?** (class, module, conftest)
2. **Where is the test defined?** (class method, module function)
3. **Do scopes match?**
4. **Does the test have `self` if accessing class fixtures?**

### Common Fixes
```python
# FIX 1: Move test into class (if fixture is class-scoped)
class TestSuite:
    @pytest.fixture
    def handler_config(self):
        return {...}
    
    def test_handler(self, handler_config):  # ✅ Now has self
        pass

# FIX 2: Move fixture to module/conftest (if multiple tests need it)
@pytest.fixture
def handler_config():  # Module-level fixture
    return {...}

def test_handler(handler_config):  # ✅ Module function with module fixture
    pass
```

### Fixture Scopes
```python
# Class fixtures - accessible only to class methods
class TestSuite:
    @pytest.fixture
    def class_fixture(self):
        return "value"
    
    def test_method(self, class_fixture):  # ✅ Works
        pass

# Module fixtures - accessible to all tests in module
@pytest.fixture
def module_fixture():
    return "value"

def test_function(module_fixture):  # ✅ Works
    pass

class TestClass:
    def test_method(self, module_fixture):  # ✅ Also works
        pass

# conftest.py fixtures - accessible to all tests in directory tree
# (defined in conftest.py)
@pytest.fixture
def global_fixture():
    return "value"
```

### Real Example (P2-4.6)
```python
# BEFORE: Module-level function with self parameter
@patch("src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher")
def test_handler_handles_transcript_save_failure(
    self,  # ❌ self in module function
    mock_fetcher_class,
    handler_config,  # ❌ Can't access class fixture
    ...
):
    pass

# AFTER: Moved into class
class TestYouTubeHandlerTranscriptIntegration:
    @pytest.fixture
    def handler_config(self):
        return {...}
    
    @patch("src.ai.youtube_transcript_fetcher.YouTubeTranscriptFetcher")
    def test_handler_handles_transcript_save_failure(
        self,  # ✅ self in class method
        mock_fetcher_class,
        handler_config,  # ✅ Accesses class fixture
        ...
    ):
        pass  # ✅ Works!
```

### Duration: 10 minutes
**Breakdown**: 3 min RED + 5 min GREEN + 2 min REFACTOR

---

## Quick Reference Table

| Pattern | Recognition | Fix Time | Key Tool |
|---------|-------------|----------|----------|
| **YAML Wikilink** | Quotes around `[[...]]` | 25 min | Custom YAML representer |
| **Date Mocking** | Today's date vs expected | 8 min | `patch("module.datetime")` |
| **Logging** | Can't verify log output | 20 min | `caplog` fixture |
| **Error Handling** | Wrong-level mock breaks | 8 min | `patch.object(instance, "method")` |
| **Cache Integration** | Mock not called (cache hit) | 15 min | Nested `patch.object` |
| **Fixture Config** | "fixture not found" | 10 min | Move test to match scope |

---

## Pattern Selection Flowchart

```
Test Failure
    │
    ├─ YAML output has quotes? ────────────────────────→ Pattern 1: YAML Wikilink
    │
    ├─ Date/timestamp mismatch? ───────────────────────→ Pattern 2: Date Mocking
    │
    ├─ Need to verify log messages? ───────────────────→ Pattern 3: Logging
    │
    ├─ Mock breaks before target code? ────────────────→ Pattern 4: Error Handling
    │
    ├─ Mock not called (cache hit)? ───────────────────→ Pattern 5: Cache Integration
    │
    └─ "fixture not found" error? ─────────────────────→ Pattern 6: Fixture Config
```

---

## Success Metrics from P2-4

- **Total Tests Fixed**: 6
- **Total Duration**: 86 minutes
- **Average**: 14.3 minutes per test
- **Pass Rate**: 172/177 → 178/178 (100% + bonus!)
- **Zero Regressions**: All existing tests maintained
- **Reusability**: All patterns applied successfully

---

## Best Practices

### 1. RED Phase First
Always document the error before fixing:
- Exact error message
- Stack trace
- Log output
- Root cause hypothesis

### 2. Targeted Mocking
Patch at the right level:
- ✅ Specific handler methods
- ❌ Shared utilities (too broad)

### 3. Pattern Recognition
Ask diagnostic questions:
- What's the error signature?
- Where does code break?
- What's the scope mismatch?
- Is caching involved?

### 4. Test Isolation
Each test should:
- Set up its own fixtures
- Not depend on execution order
- Clean up after itself
- Mock external dependencies

### 5. Documentation
For each fix, document:
- Problem signature
- Root cause
- Solution applied
- Lessons learned

---

## Related Documentation

- **Source**: `Projects/COMPLETED-2025-10/p2-4-automation-patterns/`
- **Methodology**: `.windsurf/guides/tdd-methodology-patterns.md`
- **Rules**: `.windsurf/rules/updated-development-workflow.md`
- **CI Report**: `Projects/ACTIVE/ci-failure-report-2025-10-29.md`

---

**Last Updated**: 2025-10-30  
**Status**: ✅ Complete - 178/178 automation tests passing  
**Next**: Apply patterns to remaining test failures (287 baseline)
