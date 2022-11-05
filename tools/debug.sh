#!/usr/bin/env bash

# Launch the vc program on the 'debug' dir, useful for debugging purposes
# (in conjunction with 'breakpoint()' calls).
#
# This script needs the environment variable VC_PROJECT_ROOT to be set correctly.

if [[ -z $VC_PROJECT_ROOT ]]; then
    echo "Please set the VC_PROJECT_ROOT environment variable to point to the root of the project."
    exit 1
fi

if [[ -z $VC_PROJECT_TEST_DIR ]]; then
    export VC_PROJECT_TEST_DIR=$VC_PROJECT_ROOT/debug
fi

cd $VC_PROJECT_ROOT/debug
export PYTHONPATH=$VC_PROJECT_ROOT
python3 -m vc "$@"
