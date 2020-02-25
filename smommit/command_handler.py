# -*- coding: utf-8 -*-
from smommit import cli_utils
from smommit.file_compare import check_if_equal
from smommit.small_commit import initialiseSmommit, format_message, remove_line_from_file, get_smommit_folder
import os
import time

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
    
    # Append message to smommit
    if v:
        print("Appending message to smommit...")

    # Initialise smommit
    paths = initialiseSmommit(v)
    
    if paths is not None:
        branch_smommit = paths['branch_smommit']
        branch_smommit_file = open(branch_smommit, "a+")
        # Add newline if the message is not the first message in smommit
        message = format_message(paths['config'], str(args_norm['message']))
        message += '\n'
        branch_smommit_file.write(message)
        branch_smommit_file.close()
        print('Added "' + message.strip('\n') + '" to ' + paths['branch_name'] + ' smommit')

def remove(args: dict):
    # {0} {1} [-v | --verbose] [(<line> [-f | --force])]
    args_norm = {
        "verbose": False,
        "force": False,
        "line": None
    }

    # Check if theres verbose
    args_norm["verbose"] = check_bool_option(args, "--verbose")
    v = args_norm["verbose"]
    # Check if there's force
    args_norm['force'] = check_bool_option(args, '--force')
    try:
        args_norm['line'] = args['<line>']
    except KeyError:
        if v:
            print("Couldn't find line number")
    # Check if line number is a number
    if args_norm['line'] is not None:
        try:
            args_norm["line"] = int(args_norm["line"])
        except ValueError:
            print("Line number is not a number. Aborting...")
            return

    if v:
        cli_utils.print_dict(args_norm)

    # Initialise smommit
    paths = initialiseSmommit(v)

    if paths is not None:
        branch_smommit = paths['branch_smommit']
        with open(branch_smommit, "r") as f:
            lines = f.readlines()
            if len(lines) > 0:
                if args_norm['force']:
                    if args_norm['line'] <= len(lines) and args_norm['line'] - 1 >= 0:
                        remove_line_from_file(branch_smommit, args_norm['line'], lines)
                    else:
                        print('Line number is out of range. Aborting...')
                        return
                else:
                    if args_norm['line'] is not None:
                        if args_norm['line'] <= len(lines) and args_norm['line'] - 1 >= 0:
                            if cli_utils.ask_for('Are you sure you want to delete "' + lines[args_norm['line'] - 1].strip('\n'), ['y', 'n']):
                                remove_line_from_file(branch_smommit, args_norm['line'], lines)
                            else:
                                print('Aborting...')
                                return
                        else:
                            print('Line number is out of range. Aborting...')
                            return
                    else:
                        # Pick which line to delete
                        print(paths['branch_name'] + ' smommit contains:')
                        for line_no in range(len(lines)):
                            print(str(line_no + 1) + ': ' + lines[line_no].strip('\n'))
                        while True:
                            try:
                                line_no = int(input(('Which line do you want to delete?: ')))
                                if line_no > len(lines) or line_no - 1 < 0:
                                    print('List number is out of range. Try again.')
                                else:
                                    if cli_utils.ask_for('Are you sure?', ['y', 'n']):
                                        break
                            except ValueError:
                                print('Line number is not a integer. Try again.')
                        remove_line_from_file(branch_smommit, line_no, lines)
            else:
                print(paths['branch_name'] + ' smommit doesn\'t contain any lines')
        print('Done!')
        f.close()

def refresh(args: dict):
    # {0} {1} [-v | --verbose]
    # Check if theres verbose
    v = check_bool_option(args, "--verbose")

    # Initialise smommit
    paths = initialiseSmommit(v)
    if paths is not None:
        print('Done!')

def view(args: dict):
    # {0} {1} [-v | --verbose] [-c | --config]
    # Check if theres verbose
    v = check_bool_option(args, "--verbose")
    # Check if there's config
    c = check_bool_option(args, '--config')

    # Initialise smommit
    paths = initialiseSmommit(v)
    if paths is not None:
        branch_smommit = paths['branch_smommit']
        with open(branch_smommit, "r") as f:
            lines = f.readlines()
            if len(lines) > 0:
                print(paths['branch_name'] + ' smommit contains:')
                for line in lines:
                    print(line.strip('\n'))
                if c:
                    print('\n' + paths['branch_name'] + ' config details:')
                    cli_utils.print_dict(paths['config'])
            else:
                print(paths['branch_name'] + ' smommit doesn\'t contain any lines')
        print('\nDone!')


def edit(args: dict):
    # {0} {1} [-v | --verbose] [-c | --config]
    # Check if theres verbose
    v = check_bool_option(args, "--verbose")
    # Check if there's config
    c = check_bool_option(args, '--config')

    # Initialise smommit
    paths = initialiseSmommit(v)
    if paths is not None:
        file_to_open = paths['branch_smommit'] if not c else os.path.join(get_smommit_folder(), paths['branch_name'], 'config.json')
        cli_utils.open_default_editor(file_to_open).wait()
    print('Done!')
