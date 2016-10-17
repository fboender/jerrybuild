#!/bin/sh

#
# git_wrapper.sh
#
# A wrapper for Git that sets the SSH (deploy) key.
#
# Usage:
#   export SSH_KEY=/path/to/ssh_key.rsa
#   export GIT_SSH=git_wrapper.sh
#   git pull
#

if [ -z "$SSH_KEY" ]; then
    echo "Please set SSH_KEY to the private deployment key" >&2
    exit 1
fi

ssh -i $SSH_KEY $*

