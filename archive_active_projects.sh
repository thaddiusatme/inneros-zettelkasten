#!/bin/bash
# Archive completed projects from ACTIVE to COMPLETED-2025-10
# Generated: 2025-10-08
# Purpose: Clean up ACTIVE directory (39 → 8 files)

set -e  # Exit on error

echo "🗂️  Archiving completed projects..."
echo ""

# ============================================================================
# YOUTUBE HANDLER - COMPLETED (Iteration 9)
# ============================================================================
echo "📹 Moving YouTube Handler completed work..."

git mv "Projects/ACTIVE/youtube-cli-integration-red-phase-summary.md" \
       "Projects/COMPLETED-2025-10/youtube-cli-integration-red-phase-summary.md"

git mv "Projects/ACTIVE/youtube-cli-integration-status.md" \
       "Projects/COMPLETED-2025-10/youtube-cli-integration-status.md"

git mv "Projects/ACTIVE/youtube-cli-tdd-iteration-2-green-phase-prompt.md" \
       "Projects/COMPLETED-2025-10/youtube-cli-tdd-iteration-2-green-phase-prompt.md"

git mv "Projects/ACTIVE/youtube-cli-tdd-iteration-3-prompt.md" \
       "Projects/COMPLETED-2025-10/youtube-cli-tdd-iteration-3-prompt.md"

git mv "Projects/ACTIVE/youtube-cli-tdd-iteration-3-red-phase-complete.md" \
       "Projects/COMPLETED-2025-10/youtube-cli-tdd-iteration-3-red-phase-complete.md"

git mv "Projects/ACTIVE/youtube-cli-user-context-feature.md" \
       "Projects/COMPLETED-2025-10/youtube-cli-user-context-feature.md"

git mv "Projects/ACTIVE/youtube-feature-handler-integration.md" \
       "Projects/COMPLETED-2025-10/youtube-feature-handler-integration.md"

git mv "Projects/ACTIVE/youtube-handler-daemon-integration-manifest.md" \
       "Projects/COMPLETED-2025-10/youtube-handler-daemon-integration-manifest.md"

git mv "Projects/ACTIVE/youtube-integration-next-session-prompt.md" \
       "Projects/COMPLETED-2025-10/youtube-integration-next-session-prompt.md"

git mv "Projects/ACTIVE/youtube-template-ai-integration-manifest.md" \
       "Projects/COMPLETED-2025-10/youtube-template-ai-integration-manifest.md"

git mv "Projects/ACTIVE/youtube-handler-production-validation-report.md" \
       "Projects/COMPLETED-2025-10/youtube-handler-production-validation-report.md"

echo "  ✅ 11 YouTube files moved"
echo ""

# ============================================================================
# AUTOMATION DAEMON - COMPLETED (Iterations 1-8)
# ============================================================================
echo "🤖 Moving Automation Daemon completed work..."

git mv "Projects/ACTIVE/automation-daemon-file-watcher-integration-tdd-iteration-2-p1-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/automation-daemon-file-watcher-integration-tdd-iteration-2-p1-lessons-learned.md"

git mv "Projects/ACTIVE/automation-daemon-logging-tdd-iteration-2-p1.4-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/automation-daemon-logging-tdd-iteration-2-p1.4-lessons-learned.md"

git mv "Projects/ACTIVE/automation-daemon-tdd-iteration-1-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/automation-daemon-tdd-iteration-1-lessons-learned.md"

git mv "Projects/ACTIVE/automation-daemon-tdd-iteration-1-planning.md" \
       "Projects/COMPLETED-2025-10/automation-daemon-tdd-iteration-1-planning.md"

git mv "Projects/ACTIVE/automation-logging-infrastructure-tdd-iteration-2-p1.3-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/automation-logging-infrastructure-tdd-iteration-2-p1.3-lessons-learned.md"

git mv "Projects/ACTIVE/daemon-systemd-service-tdd-iteration-8-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/daemon-systemd-service-tdd-iteration-8-lessons-learned.md"

git mv "Projects/ACTIVE/terminal-dashboard-tdd-iteration-7-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/terminal-dashboard-tdd-iteration-7-lessons-learned.md"

git mv "Projects/ACTIVE/feature-handler-configuration-performance-tdd-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/feature-handler-configuration-performance-tdd-lessons-learned.md"

git mv "Projects/ACTIVE/tdd-iteration-5-complete-summary.md" \
       "Projects/COMPLETED-2025-10/tdd-iteration-5-complete-summary.md"

git mv "Projects/ACTIVE/automation-system-implementation-summary.md" \
       "Projects/COMPLETED-2025-10/automation-system-implementation-summary.md"

git mv "Projects/ACTIVE/next-session-prompt-daemon-integration.md" \
       "Projects/COMPLETED-2025-10/next-session-prompt-daemon-integration.md"

echo "  ✅ 11 Automation Daemon files moved"
echo ""

# ============================================================================
# OTHER COMPLETED WORK
# ============================================================================
echo "📦 Moving other completed/superseded work..."

git mv "Projects/ACTIVE/centralized-storage-verification-checklist.md" \
       "Projects/COMPLETED-2025-10/centralized-storage-verification-checklist.md"

git mv "Projects/ACTIVE/automation-epic-gap-analysis.md" \
       "Projects/COMPLETED-2025-10/automation-epic-gap-analysis.md"

echo "  ✅ 2 other files moved"
echo ""

# ============================================================================
# SUPERSEDED/DEPRECATED - Move to Archive
# ============================================================================
echo "🗄️  Moving superseded documents to Archive..."

git mv "Projects/ACTIVE/executive-report-stakeholders-draft-3.md" \
       "Projects/Archive/executive-report-stakeholders-draft-3.md"

git mv "Projects/ACTIVE/adr-001-workflow-manager-refactoring.md" \
       "Projects/Archive/adr-001-workflow-manager-refactoring.md"

git mv "Projects/ACTIVE/automation-completion-retrofit-manifest.md" \
       "Projects/Archive/automation-completion-retrofit-manifest.md"

git mv "Projects/ACTIVE/automation-coding-discipline.md" \
       "Projects/Archive/automation-coding-discipline.md"

git mv "Projects/ACTIVE/logging-monitoring-requirements-automation.md" \
       "Projects/Archive/logging-monitoring-requirements-automation.md"

git mv "Projects/ACTIVE/workflow-demo-extraction-status.md" \
       "Projects/Archive/workflow-demo-extraction-status.md"

git mv "Projects/ACTIVE/workflow-demo-deprecation-plan.md" \
       "Projects/Archive/workflow-demo-deprecation-plan.md"

git mv "Projects/ACTIVE/inneros-gamification-discovery-manifest.md" \
       "Projects/Archive/inneros-gamification-discovery-manifest.md"

echo "  ✅ 8 superseded files moved to Archive"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "✅ CLEANUP COMPLETE!"
echo ""
echo "📊 Summary:"
echo "  • YouTube Handler: 11 files → COMPLETED-2025-10/"
echo "  • Automation Daemon: 11 files → COMPLETED-2025-10/"
echo "  • Other Completed: 2 files → COMPLETED-2025-10/"
echo "  • Superseded: 8 files → Archive/"
echo "  • Total moved: 32 files"
echo ""
echo "📁 Remaining in ACTIVE (should be ~7 files):"
echo "  ✅ README-ACTIVE.md"
echo "  ✅ daemon-automation-system-current-state-roadmap.md"
echo "  ✅ bug-empty-video-id-frontmatter-templater-2025-10-08.md"
echo "  ✅ bug-youtube-api-rate-limiting-2025-10-08.md"
echo "  ✅ project-todo-v3.md"
echo "  ✅ distribution-productionization-manifest.md"
echo ""
echo "🎯 Next: Review changes and commit:"
echo "   git status"
echo "   git commit -m 'Archive completed YouTube (Iteration 9) and Automation Daemon (Iterations 1-8) work'"
echo ""
