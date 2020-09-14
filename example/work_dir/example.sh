#!/bin/sh

# Show all commands being executed
set -x

# Setup environment so we can clone and pull
export PROJECT_NAME="jerrybuild"
export REPO="git@github.com:fboender/$PROJECT_NAME.git"
export SSH_KEY="/home/fboender/Documents/fboender/proj/jerrybuild/jerrybuild-deploy.rsa"
export GIT_SSH_COMMAND='ssh -i $SSH_KEY -o IdentitiesOnly=yes'

if [ ! -d "$PROJECT_NAME" ]; then
    # Clone repo if it doesn't exist yet in the working dir
    echo "Repo doesn't exist yet. Cloning"
    git clone "$REPO"
    cd $PROJECT_NAME
else
    # Update repo
    echo "Repo exists. Updating"
    cd $PROJECT_NAME

    # Clean the repo of any artifacts
    git clean -f -d

    # This example uses the 'generic' provider, so we just pull any changes and
    # fast-forward the default branch.
    git pull --ff-only

    # If your provider was something like 'github', you might want to just
    # fetch and check out the commit given by the webhook callback instead
    #git fetch
    #git checkout $commit
fi

# You'll want to do some building or testing here
ls -l 
