#!/bin/bash
# Usage: ./git-sync.sh [branch]
# If no branch is given, use the current branch

set -e

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
BRANCH=${1:-$CURRENT_BRANCH}

echo "Fetching from origin..."
git fetch --all --prune

echo "Switching to branch: $BRANCH"
git checkout "$BRANCH"

echo "Rebasing on origin/main..."
if ! git rebase origin/main; then
    echo "Rebase conflict detected."
    echo "Resolve conflicts, then run:"
    echo "  git add <files>"
    echo "  git rebase --continue"
    exit 1
fi

echo "Pushing with --force-with-lease..."
git push --force-with-lease

echo "Done. Branch '$BRANCH' is now rebased on origin/main"
