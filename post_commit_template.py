#!/usr/bin/env python3
import os
from subprocess import check_output
# Figure out which branch we're on
branch = check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip().decode('utf-8')

smommit_dir = os.path.join(os.getcwd(), '.smommit')
if os.path.exists(smommit_dir):
    branch_dir = os.path.join(smommit_dir, branch)
    smommit_branch = os.path.join(branch_dir, branch + '.txt')
    if os.path.exists(branch_dir) and os.path.exists(smommit_branch) and os.path.isfile(smommit_branch):
        # Delete smommit for this branch
        os.remove(smommit_branch)
