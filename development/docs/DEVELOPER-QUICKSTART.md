# Developer Quick Start - YouTube Integration

## 🚀 First Time Setup

### 1. Install Dependencies
```bash
pip3 install -r development/requirements.txt
```

**Critical:** Ensure `youtube-transcript-api >= 1.2.3` is installed.

### 2. Verify Installation
```bash
cd development
pytest tests/test_youtube_transcript_api_compat.py -v
```

All 6 tests should pass ✅

### 3. Start YouTube API Server
```bash
python3 development/run_youtube_api_server.py
```

Server runs on http://localhost:8080

---

## 🧪 Testing Workflow

### Before Making Changes
```bash
# Run all tests
cd development
pytest tests/ -v

# Or just YouTube tests
pytest tests/test_youtube_transcript_api_compat.py -v
```

### After Making Changes
```bash
# 1. Run compatibility tests
pytest tests/test_youtube_transcript_api_compat.py -v

# 2. Test real transcript fetching
python3 development/tests/manual_test_transcript.py

# 3. Test full API workflow
curl -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d '{"note_path": "knowledge/Inbox/YouTube/YOUR-TEST-NOTE.md.md"}'
```

---

## 📦 Dependency Management

### Checking Current Version
```bash
pip3 show youtube-transcript-api
```

### Upgrading Safely
```bash
# 1. Check release notes first!
# 2. Update requirements.txt
# 3. Install new version
pip3 install --upgrade youtube-transcript-api

# 4. Run tests immediately
pytest tests/test_youtube_transcript_api_compat.py -v

# 5. If tests fail, see migration guide
cat development/docs/youtube-transcript-api-migration.md
```

---

## 🐛 Common Issues

### "no element found: line 1, column 0"
**Cause:** Library too old or YouTube blocking  
**Fix:** `pip3 install --upgrade youtube-transcript-api`

### "ImportError: cannot import name 'TooManyRequests'"
**Cause:** Using old error class names  
**Fix:** Update imports in your code (see migration guide)

### Tests fail after upgrade
**Action:** Read migration guide and update code accordingly  
**File:** `development/docs/youtube-transcript-api-migration.md`

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/ai/youtube_transcript_fetcher.py` | Main transcript fetching logic |
| `tests/test_youtube_transcript_api_compat.py` | Compatibility tests |
| `requirements.txt` | Pinned dependency versions |
| `docs/youtube-transcript-api-migration.md` | Breaking changes guide |
| `run_youtube_api_server.py` | API server for Obsidian integration |

---

## 🔄 Git Workflow

The pre-commit hook automatically:
- Checks youtube-transcript-api version
- Runs tests if YouTube files changed
- Prevents commits that break compatibility

**Override if needed:**
```bash
git commit --no-verify
```
(Use sparingly!)

---

## 🎯 Quick Reference

**Run all tests:** `pytest tests/ -v`  
**Run YouTube tests only:** `pytest tests/test_youtube_transcript_api_compat.py -v`  
**Start API server:** `python3 development/run_youtube_api_server.py`  
**Check dependencies:** `pip3 list | grep youtube`  
**Update deps:** `pip3 install -r development/requirements.txt --upgrade`  

---

**Questions?** See `development/docs/youtube-transcript-api-migration.md`
