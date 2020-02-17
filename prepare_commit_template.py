#!/usr/bin/env python3
import sys
import os
from subprocess import check_output
# Collect the parameters
commit_msg_filepath = sys.argv[1]
if len(sys.argv) > 2:
    commit_type = sys.argv[2]
else:
    commit_type = ''
if len(sys.argv) > 3:
    commit_hash = sys.argv[3]
else:
    commit_hash = ''
# Figure out which branch we're on
branch = check_output(['git', 'symbolic-ref', '--short', 'HEAD']).strip().decode('utf-8')

if commit_type != 'message':
    smommit_dir = os.path.join(os.getcwd(), '.smommit')
    if os.path.exists(smommit_dir):
        branch_dir = os.path.join(smommit_dir, branch)
        smommit_branch = os.path.join(branch_dir, branch + '.txt')
        if os.path.exists(branch_dir) and os.path.exists(smommit_branch) and os.path.isfile(smommit_branch):
            print('Smommit for the current branch exists. Using that as a template.')
            # Open smommit for branch
            with open(commit_msg_filepath, 'r+') as f:
                with open(smommit_branch, 'r') as smommit:
                    content = f.read()
                    smommit_lines = smommit.readlines()
                    smommit_lines[-1] = smommit_lines[-1].strip('\n')
                    smommit_content = ''.join(smommit_lines)
                    f.seek(0, 0)
                    # Leave two newlines for title
                    f.write("\n\n%s %s" % (smommit_content, content))
                smommit.close()
            f.close()
        else:
            print('No smommit for the current branch. Use "smommit add" while on this branch to a small commit.')
    else:
        print('No .smommit found. If you are not using smommit then consider deleting ".git/hooks/prepare-commit-msg"')
else:
    print('Commit type is equal to "message". Aborting smommit insertion...')
