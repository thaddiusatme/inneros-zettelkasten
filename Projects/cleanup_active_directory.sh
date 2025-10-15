#!/bin/bash
# Projects/ACTIVE Directory Cleanup - Oct 15, 2025
# Moves completed documentation to appropriate archive locations

set -e

echo "🧹 Starting Projects/ACTIVE cleanup..."
echo ""

# Create archive directories
mkdir -p "Projects/COMPLETED-2025-10/adr-002-lessons-learned"
mkdir -p "Projects/COMPLETED-2025-10/status-snapshots"
mkdir -p "Projects/Archive/deprecated-2025-10"

echo "📁 Moving completed phase lessons learned..."
mv "Projects/ACTIVE/adr-002-phase2-connection-coordinator-extraction-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase3-analytics-coordinator-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-4-promotion-engine-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-5-review-triage-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-6-note-processing-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-7-safe-image-processing-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-8-orphan-remediation-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-9-fleeting-analysis-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-10-workflow-reporting-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-11-batch-processing-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-12a-configuration-coordinator-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-12b-fleeting-note-coordinator-lessons-learned.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"

echo "📸 Moving status snapshots..."
mv "Projects/ACTIVE/PROJECT-STATUS-UPDATE-2025-10-12.md" \
   "Projects/COMPLETED-2025-10/status-snapshots/"
mv "Projects/ACTIVE/PROJECT-STATUS-UPDATE-2025-10-13.md" \
   "Projects/COMPLETED-2025-10/status-snapshots/"
mv "Projects/ACTIVE/CONTEXT-UPDATE-RECOMMENDATIONS-2025-10-12.md" \
   "Projects/COMPLETED-2025-10/status-snapshots/"
mv "Projects/ACTIVE/PBI-PLANNING-SESSION-2025-10-14.md" \
   "Projects/COMPLETED-2025-10/status-snapshots/"

echo "🗑️  Moving obsolete plans..."
mv "Projects/ACTIVE/adr-002-phase-12b-fleeting-note-coordinator-plan.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/adr-002-phase-5-extraction-analysis.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"

echo "📋 Moving completed ADRs and merges to reference..."
mv "Projects/ACTIVE/ADR-002-PHASE-1-12-MERGE-SUMMARY.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"
mv "Projects/ACTIVE/ADR-002-note-lifecycle-manager-extraction.md" \
   "Projects/COMPLETED-2025-10/adr-002-lessons-learned/"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  - 12 phase lessons learned → COMPLETED-2025-10/adr-002-lessons-learned/"
echo "  - 4 status snapshots → COMPLETED-2025-10/status-snapshots/"
echo "  - 2 obsolete plans → archived"
echo "  - 2 completed ADRs → reference archive"
echo ""
echo "Remaining in ACTIVE/:"
ls -1 Projects/ACTIVE/ | grep -v '.DS_Store' | wc -l | xargs echo "  Files:"
echo ""
