#!/usr/bin/env bash

# Run vc and git in parallel to compare the effects of given commands
#
# This script needs the environment variable CTG_VC_PROJECT_ROOT to be set correctly.

if [[ -z $CTG_VC_PROJECT_ROOT ]]; then
    echo "Please set the VC_PROJECT_ROOT environment variable to point to the root of the project."
    exit 1
fi

echo "############# vc #############"
PYTHONPATH=$CTG_VC_PROJECT_ROOT:$PYTHONPATH python3 -m vc "$@"
echo "############# git #############"
git "$@"
