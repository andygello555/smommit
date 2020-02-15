from client import cli_utils
from client.file_compare import check_if_equal
import os
import time
import datetime

def check_bool_option(args: dict, option: str) -> bool:
    """ Check if theres a boolean option with the given name
        - args: the args to check for the option
        - option: the name of the option to check for
        - return: whether option is True or False
    """
    try:
        return args[option] > 0 if type(args[option]) == int else args[option]
    except KeyError:
        return False
    
def check_string_option(args: dict, option: str, arg: str) -> str:
    """ Check if theres a boolean option with the given name
        - args: the args to check for the option
        - option: the name of the option to check for
        - return: whether the string that follows the option or None if not found
    """
    try:
        equal = False if type(args[option]) == bool else 0
        if args[option] != equal:
            if args["<" + arg + ">"] != "":
                return args["<" + arg + ">"] 
    except KeyError:
        return None

def handle_message(args: dict, verbose: bool) -> dict:
    """ Handles the message if no message option is specified in make and update subcommands
        - args: the dictionary of arguments from the input command
        - verbose: whether or not the verbose option was included in the args or not
        - return: dictionary of the message where 'title' is the title of the message and 'description' is the description
    """
    # Template used in temporary message files to explain to the user that they need to add a
    # message in order to add the file
    tmp_msg_body: str = "\n# Enter your smommit message here (smommits are accompanied by the date and time)"
    tmp_msg_lines: int = tmp_msg_body.count("\n")
    message: str = ""
    
    try:
        if args["<message>"] == "":
            raise KeyError
        else:
            message = args["<message>"]
            if verbose:
                print("Message defined in command: " + message)
    except KeyError:
        if verbose:
            print("Message NOT defined in command starting default editor")
        tmp_file_path = os.path.join(os.getcwd(), "message.txt")
        # Will generate a new temp message filename if a file with that name already exists
        while os.path.exists(tmp_file_path) and os.path.isfile(tmp_file_path):
            tmp_file_path = os.path.join(os.path.dirname(tmp_file_path), os.path.splitext(tmp_file_path)[0] + "_tmp.txt")
        
        changed = False
        message_complete = False
        
        # Create tmp message file then open it in default editor. Then check if there were changes made to the message file
        while not message_complete:
            cli_utils.create_file_incwd(os.path.basename(tmp_file_path), tmp_msg_body)
            while not changed:
                # Opens the default editor for text files and waits for it to exit before opening another
                process = cli_utils.open_default_editor(tmp_file_path).wait()
                message_file = open(tmp_file_path, "rb").read()
                if not check_if_equal(bytearray(tmp_msg_body, "utf-8"), message_file):
                    changed = True
            with open(tmp_file_path, "r") as mf:
                mf_lines = mf.readlines()
                if len(mf_lines) >= tmp_msg_lines:
                    # If the template and the read message have equal line length then the user just input the title
                    message = mf_lines[0:-1]
                    diff = len(mf_lines) - (tmp_msg_lines + 1)
                    message[diff] = message[diff].replace('\n', '')
                    message = ''.join(message)
                    message_complete = True
                else:
                    print("Don't delete the template message (any text with #)")
            mf.close()
            # Delete temp message file. Sleep is kinda jank
            time.sleep(3)
            os.remove(tmp_file_path)
    return message

def add(args: dict):
    # {0} {1} [-v | --verbose] [(-m <message>)]
    args_norm = {
        "verbose": False,
        "message": None
    }
    # print(args)

    # Check if theres verbose
    args_norm["verbose"] = check_bool_option(args, "--verbose")
    v = args_norm["verbose"]
    # If message is not present then open the default editor
    args_norm["message"] = handle_message(args, args_norm["verbose"])
    if v:
        cli_utils.print_dict(args_norm)
    
    # Check if inside a git repo
    if cli_utils.is_git_repo():
        # Check if root git directory has a .smommit folder
        smommit_root = cli_utils.get_smommit_folder()
        if not os.path.exists(smommit_root):
            # Create .smommit folder
            if v:
                print(".smommit folder not found. Creating...") 
            os.makedirs(smommit_root)
        
        # Check if .gitignore contains .smommit
        contains = cli_utils.check_gitignore_for(".smommit")
        if not contains:
            if cli_utils.ask_for("This will add '.smommit' to .gitignore (and create .gitignore if it doesn't exist). Do you want to continue?", ["y", "n"]):
                # Add .smommit to gitignore
                if v:
                    print(".smommit is not in gitignore. Adding...")
                gitignore = open(os.path.join(cli_utils.get_git_root(), ".gitignore"), "a+")
                gitignore.write("\n\n# Smommit ignore\n.smommit/")
                gitignore.close()
            else:
                print("Aborting...")
                return

        # Check if smommit for the current branch exists
        branch_name = str(cli_utils.get_branch())
        branch_root = os.path.join(smommit_root, branch_name)
        if not os.path.exists(branch_root):
            # Create branch folder
            if v:
                print("Smommit for branch doesn't exist. Creating...")
            os.makedirs(branch_root)
        
        branch_smommit = os.path.join(branch_root, branch_name + ".txt")
            
        # Append message to smommit
        if v:
            print("Appending message to smommit...")
        
        time = datetime.datetime.now().strftime("%d/%m/%Y - %X")
        message = ""
        branch_smommit_file = open(branch_smommit, "a+")
        # Add newline if the message is not the first message in smommit
        if os.stat(branch_smommit).st_size != 0:
            message += "\n"
        message += str(args_norm["message"])
        branch_smommit_file.write(message + " (" + time + ")")
        branch_smommit_file.close()
    else:
        print("You are not inside a git directory. Use 'git init' or 'git clone' to create a git directory")
        return
    
def remove(args: dict):
    # {0} {1} [-v | --verbose] [<line> [-f | --force]]
    print(args)
    
def edit(args: dict):
    # {0} {1} [-v | --verbose] [-f | --force]
    print(args)

def config(args: dict):
    # {0} {1} [-v | --verbose]
    print(args)
