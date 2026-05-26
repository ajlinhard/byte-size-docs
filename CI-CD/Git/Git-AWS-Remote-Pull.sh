#!/bin/bash
set -e

BUCKET="s3://prod-sagemaker-models-s3/git-branches"

BRANCH=${1:-$(read -p "Enter branch name to pull: " b && echo "$b")}
DEST=${2:-.}

if [ -z "$BRANCH" ]; then
    echo "Error: Branch name required."
    echo "Usage: ./pull.sh <branch> [destination]"
    exit 1
fi

SOURCE="${BUCKET}/${BRANCH}/"

echo "========================================"
echo " PULL"
echo " Remote: ${SOURCE}"
echo " Local:  ${DEST}"
echo "========================================"
echo ""
echo "Dry run first..."
echo ""

aws s3 sync "$SOURCE" "$DEST" --delete --exclude ".git/*" --dryrun   ## changed

echo ""
read -p "Proceed with sync? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ]; then
    aws s3 sync "$SOURCE" "$DEST" --delete --exclude ".git/*"        ## changed

    # initilize local git branch to keep track of any changes in sagemaker
    # Note: this does not connect to gitlab, its just to easily see
    # local changes since last pull
    rm -rf "$DEST/.git/"
    git init -b sagemaker-local-$BRANCH
    git add -A
    git commit -m "Code since last pull from s3"

    echo "Pull complete."
else
    echo "Aborted."
fi

## you should be in claims-data-scientists/
chmod +x domain_swap_util_scripts/list_branches_in_s3.sh 
chmod +x domain_swap_util_scripts/push_package_to_s3.sh 
chmod +x domain_swap_util_scripts/push_branch_to_s3.sh 
chmod +x domain_swap_util_scripts/pull_package_from_s3.sh 
chmod +x domain_swap_util_scripts/pull_branch_from_s3.sh 
