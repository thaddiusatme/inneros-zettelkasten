# InnerOS Windsurf Rules v4.0 (Aug 2025)

## 📋 Context Documents (Read First)
1. `Projects/inneros-manifest-v2.md` - Project overview
2. `Projects/project-todo-v2.md` - Current priorities  
3. `Projects/reading-intake-integration-analysis.md` - Integration analysis

## 🚨 CRITICAL BLOCKERS (Must Fix First)
- **Template Bug**: `created: {{date:YYYY-MM-DD HH:mm}}` not processing → Use `/bug-triage-workflow`
- **Image Links**: Disappear during AI automation → System integrity issue
- **Reading Intake Pipeline**: BLOCKED by template bug → Phase 5 extension approach

## 🎯 Core Rules
- **Context First**: Always check manifest/todo before starting work
- **Integration Over Replacement**: Extend existing AI workflows, don't duplicate
- **Preserve Data**: Never overwrite notes without explicit permission
- **Test Coverage**: Maintain 66/66 tests passing
- **Performance**: Keep <10s summarization, <5s similarity benchmarks

## 📁 File Organization
- **Inbox**: All new notes start with `status: inbox`
- **Metadata**: Required YAML frontmatter with type, created, status, visibility
- **Extensions**: Add source/url/saved_at for Reading Intake Pipeline
- **Templates**: Use kebab-case filenames, ISO timestamps (YYYY-MM-DD HH:mm)

## 🤖 AI Status (Phase 5 Complete)
- ✅ Smart tagging, quality scoring, summarization, connections, weekly review
- 🔄 Extensions: Reading Intake Pipeline, template enhancements, import adapters

**Usage:**
```bash
python3 src/cli/workflow_demo.py . --status        # Health check
python3 src/cli/analytics_demo.py . --interactive  # Analytics
python3 src/cli/workflow_demo.py . --weekly-review # Automation
```

## 🏗️ Development Approach
- **TDD**: Red → Green → Refactor → Commit
- **Critical Path**: Fix template bug before new features
- **Integration**: Use `/integration-project-workflow` for Phase extensions
- **Compatibility**: Preserve existing functionality during changes

## 📅 August 2025 Priorities
1. **🔴 Fix Template Processing** (BLOCKING)
2. **🔴 Resolve Image Linking** (CRITICAL) 
3. **🟡 Reading Intake Pipeline** (Phase 5 extension, after bug fixes)
4. **🟢 Phase 6 Prep** (Multi-user, after pipeline complete)

## 🔧 Workflows Available
- `/bug-triage-workflow` - Critical bug resolution
- `/reading-intake-pipeline` - Pipeline development  
- `/integration-project-workflow` - Phase extension methodology
- `/tdd-git-workflow` - Development standards

## 🎯 Success Metrics
- 212+ notes, 50K+ words processed
- 66/66 tests passing
- AI adoption growing (7.1% AI-tagged notes)
- Performance targets met: <10s/<5s/<20s for summarization/similarity/connections

---
**Integration Philosophy**: Extend Phase 5 AI capabilities rather than duplicating. Template processing bug blocks all template-dependent features.
