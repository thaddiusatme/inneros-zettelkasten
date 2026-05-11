#!/bin/bash
# Design Flaw Audit Script
# Searches codebase for common design flaws that could cause catastrophic incidents
# Created: 2025-10-08 (Post-YouTube incident)

echo "========================================================================"
echo "DESIGN FLAW AUDIT - InnerOS Zettelkasten"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================================================"

CODEBASE="development/src"
TOTAL_ISSUES=0

# Category 1: Unbounded Resource Consumption
echo ""
echo "🔥 CATEGORY 1: UNBOUNDED RESOURCE CONSUMPTION (Critical)"
echo "========================================================================"

echo ""
echo "1.1 While True loops without break condition:"
WHILE_TRUE=$(grep -rn "while True:" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$WHILE_TRUE" ]; then
    echo "$WHILE_TRUE" | head -10
    COUNT=$(echo "$WHILE_TRUE" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT instances"
else
    echo "   ✅ None found"
fi

echo ""
echo "1.2 Retry loops without limit:"
RETRY_LOOPS=$(grep -rn "while.*not.*success\|while.*retry" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$RETRY_LOOPS" ]; then
    echo "$RETRY_LOOPS" | head -10
    COUNT=$(echo "$RETRY_LOOPS" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT instances"
else
    echo "   ✅ None found"
fi

echo ""
echo "1.3 External API calls (need manual review for limits):"
API_CALLS=$(grep -rn "requests\.get\|requests\.post\|\.fetch\|http\.request" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$API_CALLS" ]; then
    echo "$API_CALLS" | head -10
    COUNT=$(echo "$API_CALLS" | wc -l)
    echo "   ⚠️  Found: $COUNT API calls - MANUAL REVIEW NEEDED"
    echo "   ❗ Check each for: timeout, retry limit, circuit breaker"
else
    echo "   ✅ None found"
fi

echo ""
echo "1.4 Recursive functions (check for depth limits):"
RECURSIVE=$(grep -rn "def.*\(.*\):$" "$CODEBASE" --include="*.py" 2>/dev/null | while read line; do
    func_name=$(echo "$line" | sed 's/.*def \([^(]*\).*/\1/')
    file=$(echo "$line" | cut -d: -f1)
    grep -q "    $func_name\|$func_name(" "$file" 2>/dev/null && echo "$line"
done)
if [ ! -z "$RECURSIVE" ]; then
    echo "$RECURSIVE" | head -10
    COUNT=$(echo "$RECURSIVE" | wc -l)
    echo "   ⚠️  Found: $COUNT potentially recursive functions - MANUAL REVIEW"
else
    echo "   ✅ None found"
fi

# Category 2: Missing Error Boundaries
echo ""
echo ""
echo "💥 CATEGORY 2: MISSING ERROR BOUNDARIES (High)"
echo "========================================================================"

echo ""
echo "2.1 Bare except clauses (catches everything silently):"
BARE_EXCEPT=$(grep -rn "except:" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$BARE_EXCEPT" ]; then
    echo "$BARE_EXCEPT" | head -10
    COUNT=$(echo "$BARE_EXCEPT" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT bare except clauses"
else
    echo "   ✅ None found"
fi

echo ""
echo "2.2 API calls outside try/except blocks:"
# This is complex to detect perfectly, showing files with API calls
FILES_WITH_API=$(grep -l "requests\.get\|requests\.post\|\.fetch" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$FILES_WITH_API" ]; then
    echo "$FILES_WITH_API" | head -10
    COUNT=$(echo "$FILES_WITH_API" | wc -l)
    echo "   ⚠️  Found: $COUNT files with API calls - MANUAL REVIEW for try/except"
else
    echo "   ✅ None found"
fi

# Category 3: Data Loss Risks
echo ""
echo ""
echo "💾 CATEGORY 3: DATA LOSS RISKS (Critical)"
echo "========================================================================"

echo ""
echo "3.1 File writes without context manager:"
FILE_WRITES=$(grep -rn "= open(.*'w'\|= open(.*\"w\"" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$FILE_WRITES" ]; then
    echo "$FILE_WRITES" | head -10
    COUNT=$(echo "$FILE_WRITES" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT file writes without 'with' statement"
else
    echo "   ✅ None found"
fi

echo ""
echo "3.2 Destructive operations (need backup checks):"
DESTRUCTIVE=$(grep -rn "shutil\.rmtree\|os\.remove\|Path.*\.unlink\|\.rm\(" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$DESTRUCTIVE" ]; then
    echo "$DESTRUCTIVE" | head -10
    COUNT=$(echo "$DESTRUCTIVE" | wc -l)
    echo "   ⚠️  Found: $COUNT destructive operations - VERIFY BACKUPS"
else
    echo "   ✅ None found"
fi

echo ""
echo "3.3 File operations with 'w' mode (overwrite):"
OVERWRITE=$(grep -rn "open(.*'w'\|open(.*\"w\"" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$OVERWRITE" ]; then
    echo "$OVERWRITE" | head -10
    COUNT=$(echo "$OVERWRITE" | wc -l)
    echo "   ⚠️  Found: $COUNT file overwrites - CHECK FOR BACKUP FIRST"
else
    echo "   ✅ None found"
fi

# Category 4: Resource Leaks
echo ""
echo ""
echo "🚰 CATEGORY 4: RESOURCE LEAKS (Medium)"
echo "========================================================================"

echo ""
echo "4.1 open() calls without 'with' statement:"
OPEN_NO_WITH=$(grep -rn "= open(" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$OPEN_NO_WITH" ]; then
    echo "$OPEN_NO_WITH" | head -10
    COUNT=$(echo "$OPEN_NO_WITH" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT instances - FILE HANDLES MAY LEAK"
else
    echo "   ✅ None found"
fi

echo ""
echo "4.2 Temporary file creation:"
TEMP_FILES=$(grep -rn "tempfile\|mktemp\|NamedTemporaryFile" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$TEMP_FILES" ]; then
    echo "$TEMP_FILES" | head -10
    COUNT=$(echo "$TEMP_FILES" | wc -l)
    echo "   ⚠️  Found: $COUNT temp file creations - VERIFY CLEANUP"
else
    echo "   ✅ None found"
fi

# Category 5: Race Conditions
echo ""
echo ""
echo "🏃 CATEGORY 5: RACE CONDITIONS (Medium)"
echo "========================================================================"

echo ""
echo "5.1 Check-then-act patterns:"
CHECK_THEN_ACT=$(grep -rn "if.*\.exists()\|if.*os\.path\.exists" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$CHECK_THEN_ACT" ]; then
    echo "$CHECK_THEN_ACT" | head -10
    COUNT=$(echo "$CHECK_THEN_ACT" | wc -l)
    echo "   ⚠️  Found: $COUNT instances - POTENTIAL RACE CONDITIONS"
else
    echo "   ✅ None found"
fi

echo ""
echo "5.2 File watcher event handlers:"
FILE_WATCHERS=$(grep -rn "on_modified\|on_created\|on_deleted\|FileSystemEventHandler" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$FILE_WATCHERS" ]; then
    echo "$FILE_WATCHERS" | head -10
    COUNT=$(echo "$FILE_WATCHERS" | wc -l)
    echo "   ⚠️  Found: $COUNT file watcher handlers - CHECK FOR DEBOUNCING"
else
    echo "   ✅ None found"
fi

# Category 6: Performance Issues
echo ""
echo ""
echo "🐌 CATEGORY 6: PERFORMANCE DEGRADATION (Low)"
echo "========================================================================"

echo ""
echo "6.1 Nested loops (potential O(n²) complexity):"
# Simple heuristic: look for two 'for' on consecutive-ish lines
NESTED_LOOPS=$(grep -rn "for.*in.*:" "$CODEBASE" --include="*.py" 2>/dev/null | \
    awk -F: '{print $1":"$2}' | \
    uniq -c | \
    awk '$1 > 1 {print $2}' || echo "")
if [ ! -z "$NESTED_LOOPS" ]; then
    echo "$NESTED_LOOPS" | head -10
    COUNT=$(echo "$NESTED_LOOPS" | wc -l)
    echo "   ⚠️  Found: $COUNT potential nested loops - MANUAL REVIEW"
else
    echo "   ✅ None found"
fi

echo ""
echo "6.2 Database queries without LIMIT:"
DB_QUERIES=$(grep -rn "SELECT.*FROM" "$CODEBASE" --include="*.py" 2>/dev/null | grep -v "LIMIT" || echo "")
if [ ! -z "$DB_QUERIES" ]; then
    echo "$DB_QUERIES" | head -10
    COUNT=$(echo "$DB_QUERIES" | wc -l)
    echo "   ⚠️  Found: $COUNT queries without LIMIT"
else
    echo "   ✅ None found"
fi

# Category 7: Security Issues
echo ""
echo ""
echo "🔒 CATEGORY 7: SECURITY VULNERABILITIES (High)"
echo "========================================================================"

echo ""
echo "7.1 Potential hardcoded secrets:"
SECRETS=$(grep -rn "API_KEY.*=.*['\"].*\|PASSWORD.*=.*['\"].*\|SECRET.*=.*['\"].*\|TOKEN.*=.*['\"]" "$CODEBASE" --include="*.py" 2>/dev/null | \
    grep -v "getenv\|config\|os\.environ" || echo "")
if [ ! -z "$SECRETS" ]; then
    echo "$SECRETS" | head -10
    COUNT=$(echo "$SECRETS" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT potential hardcoded secrets"
else
    echo "   ✅ None found"
fi

echo ""
echo "7.2 Shell command execution:"
SHELL_EXEC=$(grep -rn "os\.system\|subprocess\.call.*shell=True\|subprocess\.run.*shell=True" "$CODEBASE" --include="*.py" 2>/dev/null || echo "")
if [ ! -z "$SHELL_EXEC" ]; then
    echo "$SHELL_EXEC" | head -10
    COUNT=$(echo "$SHELL_EXEC" | wc -l)
    TOTAL_ISSUES=$((TOTAL_ISSUES + COUNT))
    echo "   ⚠️  Found: $COUNT shell executions - INJECTION RISK"
else
    echo "   ✅ None found"
fi

# Summary
echo ""
echo ""
echo "========================================================================"
echo "AUDIT SUMMARY"
echo "========================================================================"
echo "Total potential issues found: $TOTAL_ISSUES"
echo ""
echo "CRITICAL (immediate attention):"
echo "  - Category 1: Unbounded Resource Consumption"
echo "  - Category 3: Data Loss Risks"
echo ""
echo "HIGH (review soon):"
echo "  - Category 2: Missing Error Boundaries"
echo "  - Category 7: Security Vulnerabilities"
echo ""
echo "MEDIUM (review when possible):"
echo "  - Category 4: Resource Leaks"
echo "  - Category 5: Race Conditions"
echo ""
echo "LOW (optimize later):"
echo "  - Category 6: Performance Degradation"
echo ""
echo "NEXT STEPS:"
echo "  1. Review all CRITICAL findings manually"
echo "  2. Create GitHub issues for confirmed problems"
echo "  3. Prioritize fixes: P0 (immediate) > P1 (this week) > P2 (later)"
echo "  4. Implement circuit breaker system (ADR-002)"
echo "  5. Run this audit weekly to catch new issues"
echo ""
echo "DETAILED RESULTS: Review output above for specific file/line numbers"
echo "========================================================================"
