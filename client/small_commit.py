""" "Backend" stuff for smommit cli tool
"""
from client import cli_utils, file_compare
from os import path, getcwd, makedirs, stat, chmod, devnull
import json
import datetime
import git
import subprocess
from stat import S_IEXEC

config_template = {
    'datetime': True,
    'list-hyphons': True
}

prepare_commit_msg_hook_template = r'''#!/usr/bin/env python3
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
'''

post_commit_hook_template = r'''#!/usr/bin/env python3
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
'''

def is_git_repo(path='.'):
    return subprocess.call(['git', '-C', path, 'status'], stderr=subprocess.STDOUT, stdout=open(devnull, 'w')) == 0

def get_git_root():
    git_repo = git.Repo(getcwd(), search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root

def get_smommit_folder():
    return path.join(get_git_root(), ".smommit")

def get_branch():
    git_repo = git.Repo(getcwd(), search_parent_directories=True)
    return git_repo.active_branch.name

def check_gitignore_for(keyword: str) -> bool:
    git_root = get_git_root()
    gitignore = path.join(git_root, ".gitignore")
    if not path.exists(gitignore) or not path.isfile(gitignore):
        return False
    else:
        # Check file for keyword
        gitignore_file = open(gitignore, "r")
        gitignore_file_lines = gitignore_file.readlines()
        gitignore_file.close()
        for line in gitignore_file_lines:
            if keyword in line and "#" not in line:
                return True
        return False

def format_message(config: dict, message: str) -> str:
    final_message = ''
    if config['list-hyphons']:
        final_message += '- '
    final_message += message
    if config['datetime']:
        final_message += ' (' + datetime.datetime.now().strftime("%d/%m/%Y - %X") + ')'
    return final_message

def remove_line_from_file(filename: str, line_delete: int, lines: list):
    with open(filename, "w") as f:
        for line_no in range(len(lines)):
            line = lines[line_no]
            if line_no != line_delete - 1:
                f.write(line)
    f.close()

def initialiseSmommit(v: bool) -> dict:
    if v:
        print("Initialising smommit..")
    # Check if inside a git repo
    if is_git_repo():
        # Check if .gitignore contains .smommit
        contains = check_gitignore_for(".smommit")
        if not contains:
            if cli_utils.ask_for("This will add '.smommit' to .gitignore (and create .gitignore if it doesn't exist). Do you want to continue?", ["y", "n"]):
                # Add .smommit to gitignore
                if v:
                    print(".smommit is not in gitignore. Adding...")
                gitignore = open(path.join(get_git_root(), ".gitignore"), "a+")
                gitignore.write("\n\n# Smommit ignore\n.smommit/")
                gitignore.close()
            else:
                print("Aborting...")
                return None

        # Check for prepare-commit-msg in .git/hooks
        commit_msg_hook = path.join(get_git_root(), '.git', 'hooks', 'prepare-commit-msg')
        if not path.exists(commit_msg_hook) or not path.isfile(commit_msg_hook):
            # Create prepare-commit-msg
            if v:
                print('prepare-commit-msg not found in ".git/hooks". Creating...')
            with open(commit_msg_hook, 'w+') as hook:
                hook.write(prepare_commit_msg_hook_template)
            st = stat(commit_msg_hook)
            chmod(commit_msg_hook, st.st_mode | S_IEXEC)
            hook.close()
        else:
            # Check if prepare-commit-msg matches the template
            with open(commit_msg_hook, 'rb+') as hook:
                if not file_compare.check_if_equal(hook.read(), bytearray(prepare_commit_msg_hook_template, 'utf-8')):
                    if v:
                        print('prepare-commit-msg hook in ".git/hooks" does not match the template. Recreating...')
                    hook.seek(0)
                    hook.write(bytearray(prepare_commit_msg_hook_template, 'utf-8'))
                    hook.truncate()
            st = stat(commit_msg_hook)
            chmod(commit_msg_hook, st.st_mode | S_IEXEC)
            hook.close()
        
        # Check for post-commit in .git/hooks
        post_commit_hook = path.join(get_git_root(), '.git', 'hooks', 'post-commit')
        if not path.exists(post_commit_hook) or not path.isfile(post_commit_hook):
            # Create prepare-commit-msg
            if v:
                print('post-commit hook not found in ".git/hooks". Creating...')
            with open(post_commit_hook, 'w+') as hook:
                hook.write(post_commit_hook_template)
            st = stat(post_commit_hook)
            chmod(post_commit_hook, st.st_mode | S_IEXEC)
            hook.close()
        else:
            # Check if prepare-commit-msg matches the template
            with open(post_commit_hook, 'rb+') as hook:
                if not file_compare.check_if_equal(hook.read(), bytearray(post_commit_hook_template, 'utf-8')):
                    if v:
                        print('post-commit hook in ".git/hooks" does not match the template. Recreating...')
                    hook.seek(0)
                    hook.write(bytearray(post_commit_hook_template, 'utf-8'))
                    hook.truncate()
            st = stat(post_commit_hook)
            chmod(post_commit_hook, st.st_mode | S_IEXEC)
            hook.close()

        # Check if root git directory has a .smommit folder
        smommit_root = get_smommit_folder()
        if not path.exists(smommit_root):
            # Create .smommit folder
            if v:
                print(".smommit folder not found. Creating...") 
            makedirs(smommit_root)

        # Check if smommit for the current branch exists
        branch_name = str(get_branch())
        branch_root = path.join(smommit_root, branch_name)
        if not path.exists(branch_root):
            # Create branch folder
            if v:
                print("Smommit for branch doesn't exist. Creating...")
            makedirs(branch_root)
        
        branch_smommit = path.join(branch_root, branch_name + ".txt")
        branch_config = path.join(branch_root, 'config.json')
        config = {}
        # Create smommit (if not there already)
        branch_smommit_file = open(branch_smommit, "a+")
        branch_smommit_file.close()
        # Check if config file exists
        if path.exists(branch_config) and path.isfile(branch_config):
            # Load config into dictionary
            if v:
                print('Opening config...')
            with open(branch_config) as json_file:
                config = json.load(json_file)
                if config.keys() != config_template.keys():
                    if v:
                        print('Config file is not the same schema as template. Substituting in config template...')
                    config = config_template
                    json.dump(config_template, json_file)
            json_file.close()
        else:
            if v:
                print('No config file found for branch so creating one from template...')
            with open(branch_config, 'w') as outfile:
                json.dump(config_template, outfile)
            outfile.close()
            config = config_template

        return {'branch_smommit': branch_smommit, 'branch_name': branch_name, 'config': config}
    else:
        print("You are not inside a git directory. Use 'git init' or 'git clone' to create a git directory")
        return None
