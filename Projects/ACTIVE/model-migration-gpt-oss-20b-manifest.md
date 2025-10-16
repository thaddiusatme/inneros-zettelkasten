# 🔄 Model Migration: llama3 → gpt-oss:20b

**Status**: 📋 **PLANNED** - Ready for TDD implementation  
**Priority**: P1 - **IMPROVES AI QUALITY** for auto-promotion workflow  
**Timeline**: 8-10 hours (TDD approach with JSON hardening)  
**Branch**: `feat/model-migration-gpt-oss-20b` (to be created)  
**Risk Level**: 🟡 **MEDIUM** - JSON parsing brittleness in 2 critical components

---

## 🎯 **Problem Statement**

### **Current Limitations (llama3:latest - 8B)**
- **Quality ceiling**: 8B parameter model limits tagging/extraction accuracy
- **JSON reliability**: ~15% failure rate in `youtube_quote_extractor` due to format drift
- **Context limits**: Long transcripts (>4000 tokens) truncate in quote extraction
- **Auto-promotion impact**: Lower quality scores affect workflow automation

### **Target Benefits (gpt-oss:20b)**
- ✅ **2.5x parameters** (20B vs 8B) → better instruction following
- ✅ **Native JSON mode** → structured outputs eliminate regex parsing
- ✅ **8K context** (configurable) → handles longer transcripts
- ✅ **16GB VRAM** requirement → fits consumer hardware
- ✅ **Local/private** → maintains privacy-first architecture
- ✅ **OpenAI-published** → first-party Ollama support

---

## 🏗️ **Architecture Overview**

### **Core Strategy**
1. **Environment variable foundation** - Enable instant rollback
2. **JSON mode hardening** - Eliminate brittle regex parsing
3. **Schema-constrained outputs** - Guarantee format compliance
4. **Per-component configuration** - Gradual rollout capability
5. **Extended context variant** - Handle long transcripts

### **Critical Components (High Risk)**
| Component | Current Risk | Mitigation |
|-----------|-------------|------------|
| `tagger.py` | 🔴 Regex JSON parsing | JSON mode + schema |
| `youtube_quote_extractor.py` | 🔴 Complex JSON structure | Structured outputs |
| `enhancer.py` | 🟡 Multiple JSON responses | JSON mode |
| `summarizer.py` | 🟢 Free-form text | No changes needed |

---

## 📋 **Implementation Phases**

### **Phase 1: Environment Variable Foundation** (1 hour)
**Goal**: Enable instant rollback via environment variable

**Changes**:
- `development/src/ai/ollama_client.py` - Add `INNEROS_DEFAULT_MODEL` env var
- `development/tests/unit/test_ollama_client.py` - Parameterize model assertions

**Rollback**: `export INNEROS_DEFAULT_MODEL=llama3:latest`

---

### **Phase 2: JSON Mode Hardening** (3 hours)
**Goal**: Eliminate regex parsing with native JSON mode

#### **2A: OllamaClient Enhancement**
Add `generate_completion_json()` method with:
- `format: "json"` for basic JSON mode
- `format: schema` for structured outputs
- Automatic `json.loads()` with error handling
- Lower temperature (0.2) for reliability

#### **2B: Tagger Component**
- Replace regex parsing with JSON mode
- Increase `max_tokens` from 100 → 256
- Add schema validation for `{"tags": [...]}`

#### **2C: YouTube Quote Extractor** (CRITICAL)
- Define strict JSON Schema for quotes
- Use structured outputs API
- Fixed `max_tokens: 2048` (remove dynamic calculation)
- Schema enforces: `text`, `start`, `end`, `reason` fields

---

### **Phase 3: Context Window Expansion** (1 hour)
**Goal**: Handle long transcripts without truncation

**Modelfile**: `config/gpt-oss-20b-ctx8k.Modelfile`
```
FROM gpt-oss:20b
PARAMETER num_ctx 8192
PARAMETER num_predict -1
PARAMETER temperature 0.2
```

**Usage**: Auto-select extended context for transcripts >4000 tokens

---

### **Phase 4: Per-Component Configuration** (1 hour)
**Goal**: Enable gradual rollout and component-specific tuning

**New File**: `config/ai.yaml`
```yaml
models:
  default: gpt-oss:20b
  fallback: llama3:latest
  component_overrides:
    tagger: gpt-oss:20b
    youtube_extractor: gpt-oss-20b-ctx8k
    summarizer: gpt-oss:20b
    enhancer: gpt-oss:20b
```

---

### **Phase 5: Testing & Validation** (3 hours)

#### **5A: Unit Test Updates**
- Parameterize model assertions
- Add JSON mode tests
- Update integration tests

#### **5B: JSON Conformance Tests** (NEW)
File: `development/tests/integration/test_json_mode_conformance.py`
- Validate tagger JSON output
- Validate YouTube extractor schema compliance
- Test error handling for malformed JSON

#### **5C: Performance Benchmarks** (NEW)
File: `development/tests/integration/test_model_performance.py`
- Tagger latency: <5s
- YouTube extraction: <15s
- Memory usage monitoring
- Context window stress tests

---

## 🧪 **Testing Strategy**

### **Pre-Migration Validation**
```bash
# 1. Verify hardware
nvidia-smi  # or system_profiler SPDisplaysDataType

# 2. Pull model
ollama pull gpt-oss:20b

# 3. Test basic functionality
ollama run gpt-oss:20b "Output JSON: {\"test\": true}"

# 4. Create backup branch
git checkout -b backup-llama3-baseline
```

### **Incremental Testing**
- Test after each phase before proceeding
- Run full test suite: `pytest development/tests/`
- Validate auto-promotion workflow end-to-end
- Test with 8 inbox notes requiring metadata repair

### **Rollback Testing**
```bash
export INNEROS_DEFAULT_MODEL=llama3:latest
pytest development/tests/integration/
```

---

## 🎯 **Success Metrics**

| Metric | Before (llama3) | Target (gpt-oss:20b) | Validation |
|--------|-----------------|----------------------|------------|
| **Tagger JSON failures** | ~10% | <2% | JSON conformance tests |
| **YouTube extraction failures** | ~15% | <5% | Schema validation |
| **Tagging latency** | 2-3s | 4-6s | Performance benchmarks |
| **Quote extraction latency** | 5-8s | 10-15s | Performance benchmarks |
| **Auto-promotion accuracy** | 0.7 threshold | 0.75+ | Quality score analysis |
| **Context truncation** | >4000 tokens | 8192 tokens | Long transcript tests |

---

## 🚨 **Risk Mitigation**

### **High-Risk Areas**
1. **JSON Parsing Brittleness**
   - **Mitigation**: Ollama's native JSON mode + structured outputs
   - **Fallback**: Retry with stricter instructions

2. **Performance Degradation**
   - **Mitigation**: Performance benchmarks in CI
   - **Fallback**: Per-component model overrides

3. **Context Window Issues**
   - **Mitigation**: Extended context Modelfile variant
   - **Fallback**: Transcript chunking strategy

### **Rollback Plan**
```bash
# Immediate rollback (no code changes)
export INNEROS_DEFAULT_MODEL=llama3:latest

# Verify rollback
python3 -c "from development.src.ai.ollama_client import OllamaClient; print(OllamaClient().model)"

# Permanent rollback
git revert <migration-commit>
```

---

## 📁 **Files Modified**

### **Core Changes**
1. `development/src/ai/ollama_client.py` - Env var + JSON method
2. `development/src/ai/tagger.py` - JSON mode integration
3. `development/src/ai/youtube_quote_extractor.py` - Schema-constrained outputs
4. `development/tests/unit/test_ollama_client.py` - Parameterized assertions

### **New Files**
5. `development/tests/integration/test_json_mode_conformance.py`
6. `development/tests/integration/test_model_performance.py`
7. `config/ai.yaml`
8. `config/gpt-oss-20b-ctx8k.Modelfile`

### **Documentation**
9. `INSTALLATION.md` - Update model pull instructions
10. `CLI-REFERENCE.md` - Update model references
11. `README.md` - Update AI features section

---

## 🔗 **Dependencies**

### **Prerequisites**
- Ollama installed and running
- 16GB+ VRAM or unified memory
- Python 3.9+ with existing dependencies

### **New Dependencies**
None - uses existing Ollama API

### **Model Availability**
- Primary: `ollama pull gpt-oss:20b`
- Extended context: Built via Modelfile
- Fallback: `llama3:latest` (already installed)

---

## 📚 **Technical References**

### **Ollama Documentation**
- [gpt-oss:20b model](https://ollama.com/library/gpt-oss:20b)
- [Structured Outputs API](https://ollama.com/blog/structured-outputs)
- [Modelfile Reference](https://docs.ollama.com/modelfile)
- [API Documentation](https://docs.ollama.com/api)

### **OpenAI Resources**
- [GPT-OSS GitHub](https://github.com/openai/gpt-oss)
- [Run Locally Guide](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama)
- [HuggingFace Model](https://huggingface.co/openai/gpt-oss-20b)

---

## 🎬 **Implementation Checklist**

### **Pre-Migration** (30 min)
- [ ] Verify hardware requirements (16GB+ VRAM)
- [ ] Pull model: `ollama pull gpt-oss:20b`
- [ ] Test model: `ollama run gpt-oss:20b "test"`
- [ ] Create backup branch
- [ ] Document current performance baseline

### **Phase 1: Foundation** (1 hour)
- [ ] Add `INNEROS_DEFAULT_MODEL` env var support
- [ ] Update test assertions
- [ ] Test rollback mechanism
- [ ] Commit: "feat: add environment variable model configuration"

### **Phase 2: JSON Hardening** (3 hours)
- [ ] Add `generate_completion_json()` method
- [ ] Update `tagger.py` with JSON mode
- [ ] Update `youtube_quote_extractor.py` with schema
- [ ] Create JSON conformance tests
- [ ] Run: `pytest tests/integration/test_json_mode_conformance.py`
- [ ] Commit: "feat: add JSON mode hardening for AI components"

### **Phase 3: Context Expansion** (1 hour)
- [ ] Create `gpt-oss-20b-ctx8k.Modelfile`
- [ ] Build variant: `ollama create gpt-oss-20b-ctx8k -f ...`
- [ ] Test with long transcript (>4000 tokens)
- [ ] Commit: "feat: add extended context model variant"

### **Phase 4: Configuration** (1 hour)
- [ ] Create `config/ai.yaml`
- [ ] Add config loading to components
- [ ] Test per-component overrides
- [ ] Commit: "feat: add per-component model configuration"

### **Phase 5: Validation** (3 hours)
- [ ] Run full test suite: `pytest development/tests/`
- [ ] Run performance benchmarks
- [ ] Test auto-promotion workflow end-to-end
- [ ] Validate 8 inbox notes with missing metadata
- [ ] Document performance results
- [ ] Commit: "test: validate gpt-oss:20b migration"

### **Documentation** (30 min)
- [ ] Update `INSTALLATION.md`
- [ ] Update `CLI-REFERENCE.md`
- [ ] Update `README.md`
- [ ] Add migration notes to `CHANGELOG.md`
- [ ] Commit: "docs: update for gpt-oss:20b model"

---

## 🏆 **Expected Outcomes**

### **Quality Improvements**
- **Better instruction following** → More accurate tags and quotes
- **Reduced JSON failures** → More reliable automation
- **Higher quality scores** → More notes auto-promoted (≥0.75)
- **Better context handling** → Complete long transcript processing

### **Workflow Impact**
- **Auto-promotion accuracy** improves from 0.7 → 0.75 threshold
- **Inbox processing** more reliable with better AI quality
- **YouTube workflow** handles longer videos without truncation
- **Weekly review** shows higher-quality recommendations

### **Technical Benefits**
- **Instant rollback** via environment variable
- **Per-component control** for gradual migration
- **Schema validation** prevents format regressions
- **Performance monitoring** catches issues early

---

## 📊 **Project Timeline**

**Total Estimated Time**: 8-10 hours

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Pre-Migration | 30 min | Hardware verification |
| Phase 1: Foundation | 1 hour | None |
| Phase 2: JSON Hardening | 3 hours | Phase 1 complete |
| Phase 3: Context Expansion | 1 hour | Phase 2 complete |
| Phase 4: Configuration | 1 hour | Phase 3 complete |
| Phase 5: Validation | 3 hours | All phases complete |
| Documentation | 30 min | Phase 5 complete |

**Recommended Approach**: Complete one phase per session, validate thoroughly before proceeding.

---

## 🔄 **Integration with Existing Projects**

### **Enables**
- **P1 Inbox Metadata Repair** - Better AI quality improves metadata generation
- **Auto-Promotion Workflow** - Higher quality scores → more automation
- **YouTube Processing** - Better quote extraction with extended context

### **Complements**
- **ADR-002 Completion** - Improved AI quality across all coordinators
- **Fleeting Note Lifecycle** - Better triage recommendations
- **Weekly Review** - More accurate quality assessments

---

**Status**: Ready for implementation. Begin with Phase 1 (environment variable foundation) for lowest-risk entry point.

**Next Action**: Create branch `feat/model-migration-gpt-oss-20b` and start Phase 1 implementation.
