#!/bin/sh

#
# git-co-commit.sh
#
# Reset repo to a good clean state, fetch all new changes and check out the
# commit given in the `commit` environment variable.
#
# Usage:
#   export SSH_KEY=/path/to/deploy_key.rsa
#   export GIT_SSH=git_wrapper.sh
#   git-co-commit.sh
#

if [ -z "$GIT_SSH" ]; then
    echo "GIT_SSH env var is not set. No git wrapper will be used!" >&2
fi

git reset --hard
git clean -f -d
git fetch --all
git checkout $commit
