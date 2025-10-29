#!/bin/bash
# Sync commits to both private and public repos

set -e  # Exit on error

BRANCH=${1:-main}  # Default to main branch

echo "🔄 Syncing to both repos..."
echo ""

# Push to private repo (origin)
echo "📤 Pushing to private repo (origin)..."
git push origin "$BRANCH"
echo "✅ Private repo updated"
echo ""

# Push to public repo  
echo "📤 Pushing to public repo (public)..."
git push public "$BRANCH"
echo "✅ Public repo updated"
echo ""

echo "🎉 Successfully synced to both repos!"
echo ""
echo "Private: https://github.com/thaddiusatme/inneros-zettelkasten"
echo "Public:  https://github.com/thaddiusatme/inneros-zettelkasten-public"
