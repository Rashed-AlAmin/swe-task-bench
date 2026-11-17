#!/usr/bin/env bash
# extract.sh <PR#>  -> tasks/click-<PR#>/{meta.json,gold.patch,test.patch}
set -euo pipefail
ROOT=~/Desktop/swe-task-bench; REPO=$ROOT/repo; PR=$1; T=$ROOT/tasks/click-$PR
mkdir -p "$T"; cd "$REPO"
MERGED=$(gh api repos/pallets/click/pulls/$PR --jq .merge_commit_sha)
BASE=$(git rev-list --parents -n1 "$MERGED" | awk '{print $2}')
git diff "$BASE" "$MERGED" -- 'src/***' > "$T/gold.patch"
git diff "$BASE" "$MERGED" -- 'tests/***' > "$T/test.patch"
gh api repos/pallets/click/pulls/$PR --jq "{pr:.number,title:.title,url:.html_url,merged_at:.merged_at,merge_commit:\"$MERGED\",base_commit:\"$BASE\",body:.body}" > "$T/meta.json"
echo "$PR base=$BASE gold=$(wc -l < "$T/gold.patch") test=$(wc -l < "$T/test.patch")"
