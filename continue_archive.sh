#!/bin/bash
# Continue archiving (YouTube files already moved)
set -e

echo "🤖 Moving Automation Daemon completed work..."

git mv "Projects/ACTIVE/automation-daemon-file-watcher-integration-tdd-iteration-2-p1-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-daemon-logging-tdd-iteration-2-p1.4-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-daemon-tdd-iteration-1-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-daemon-tdd-iteration-1-planning.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-event-handler-tdd-iteration-2-p1.2-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-logging-infrastructure-tdd-iteration-2-p1.3-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/daemon-systemd-service-tdd-iteration-8-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/terminal-dashboard-tdd-iteration-7-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/feature-handler-configuration-performance-tdd-lessons-learned.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/tdd-iteration-5-complete-summary.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-system-implementation-summary.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/next-session-prompt-daemon-integration.md" \
       "Projects/COMPLETED-2025-10/"

echo "  ✅ 12 Automation files moved"

echo "📦 Moving other completed work..."

git mv "Projects/ACTIVE/centralized-storage-verification-checklist.md" \
       "Projects/COMPLETED-2025-10/"

git mv "Projects/ACTIVE/automation-epic-gap-analysis.md" \
       "Projects/COMPLETED-2025-10/"

echo "  ✅ 2 other files moved"

echo "🗄️  Moving superseded to Archive..."

git mv "Projects/ACTIVE/executive-report-stakeholders-draft-3.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/adr-001-workflow-manager-refactoring.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/automation-completion-retrofit-manifest.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/automation-coding-discipline.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/logging-monitoring-requirements-automation.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/workflow-demo-extraction-status.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/workflow-demo-deprecation-plan.md" \
       "Projects/Archive/"

git mv "Projects/ACTIVE/inneros-gamification-discovery-manifest.md" \
       "Projects/Archive/"

echo "  ✅ 8 superseded files moved"
echo ""
echo "✅ CLEANUP COMPLETE!"
echo ""
echo "📁 Files remaining in ACTIVE:"
ls -1 Projects/ACTIVE/
