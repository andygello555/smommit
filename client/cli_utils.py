from os import getcwd, path
from urllib.parse import urlparse
import requests
import platform
import subprocess
import git

class UndefinedSystem(Exception):
    """ Raised when the user's system is unhandled/unrecognized """
    def __init__(self, message):
        super().__init__(message)

def create_file_withpath(filepath: str, body: str):
    """ Creates a file with the given body at the given path
    """
    tmp_f = open(filepath, "w+")
    tmp_f.write(body)
    tmp_f.close()

def create_file_incwd(filename: str, body: str):
    """ Creates a file with the given body in current working dir
    """
    file_path = path.join(getcwd(), filename)
    create_file_withpath(file_path, body)

def open_default_editor(filename: str) -> subprocess.Popen:
    """ Opens a given filename inside the default editor of the os. Returns
        a subprocess.Popen which can be manipulated in any way the invoker sees
        fit. If the specified file does not exist then create it.
    """
    if not path.exists(filename):
        create_file_incwd(filename, "")
    
    sys = platform.system()
    args = {
        "Windows": [filename],
        "Linux": ["xdg-open", filename],
        "Darwin": ["open", filename]
    }

    if path.exists(filename) and path.isfile(filename):
        try:
            msg_input = subprocess.Popen(args[sys])
            return msg_input
        except TypeError:
            # If there's no system which matches the user's system in the args dict
            raise UndefinedSystem("Sorry your system is not supported yet")
    else:
        raise FileNotFoundError("Filename specified does not exist")

def ask_for(question: str, answers: list):
    """ Given a question and a list of answers it will return the answer. If the list of answers has only 2 elements then
        if the answer is equal to the first element it will return True and False otherwise
    """
    answer = str(input(question + " " + str(answers) + ": ")).lower()
    while answer not in answers:
        print("Don't understand that input")
        answer = str(input(question + " " + str(answers))).lower()
    return answer if len(answers) > 2 else answers[0] == answer

def check_if_404(url: str) -> bool:
    """ Checks if URL returns a 404
        - url: URL to check
        - returns: true if 404 found, false otherwise
    """
    check = requests.get(url)
    return check.status_code == 404

def find_hostname(url: str) -> str:
    """ Finds the hostname of the given URL and splits it on the first dot (used to form filename)
    """
    if not check_if_404(url):
        urlname = urlparse(url)
        urlhost = urlname.hostname
        # Strips everything after the first dot
        a = urlname.hostname.split(".")[0]
        pos = urlhost.find(a)
        return urlhost[:pos + len(a)]
    else:
        return None

def print_dict(args: dict):
    for arg in args.keys():
        print(str(arg) + ": " + str(args[arg]))

def is_git_repo():
    try:
        _ = git.Repo(getcwd()).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

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
