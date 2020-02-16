# smommit
The CLI tool for forgetful gits. 

### What is it? 
- If you don't want to `git commit` just yet then why not make a smommit (small commit)
- If your're like me and can't remember what you have changed in a commit then whenever you have made a change just call `smommit add -m <change>`. This will create a `.smommit` directory and a "smommit" file (for the current branch your on) which stores all your small commits ready for the big one.
- Then when you call `git commit` the commit message will be filled out with all those lovely smommits that you have collected (the smommit file will also be overwritten ready for your new smommits)
- Smommits also come with a `config.json` which allows you to access the formatting options for the smommit for that branch
  - Current supported formatting options:
    - `datetime`: if true then will add a timestamp at the end of the message in the format `("%d/%m/%Y - %X")`
    - `list-hyphons`: if true then will add a hyphon to the start of the message (like a list item)

#### Available commands:
```
    # For adding a smommit message to the smommit file of the current branch
    smommit add [-v | --verbose] [(-m <message>)]
    # For removing a smommit message from the smommit file of the current branch
    smommit rm [-v | --verbose] [(<line> [-f | --force])]
    # Initialises all the files required for smommit (this is called by all other functions)
    smommit refresh [-v | --verbose]
    # View all smommit messages from the smommit file of the current branch
    smommit view [-v | --verbose]
    # Edit the smommit file or config file for the current branch in the default editor
    smommit edit [-v | --verbose] [-f | --force]
    # Show help or version
    smommit -h | --help | --version
Options:
    -m --message  The smommit message (if not present then default editor will be opened)
    -f --force    Force/Don't ask for permission
    -v --verbose  Verbose
    -h --help     Shows help
    --version     Show version
    <message>     The smommit message
    <line>        Line number
```

#### Install:
Currently there is no way of installing other than cloning this github and placing `smommit` on your path. I have only tested the tool on Ubuntu 18.04 but it should work on all Unix based systems.

#### Requirments:
- docopt
- numpy
- gitpython
