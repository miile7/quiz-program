# Quiz-program
A simple program that asks you pre-defined questions, for example for learning vocabulary.

## Key Features

- Asks you questions randomly sorted, asks every question one time
- Shows previously saved answers, **does not check the answers**, this is up to you
- Shows how many questions are answered already
- Questions are defined in a json file
- Current session will be saved in a json file

## Command Reference
The following commands are available:
+ `h`, `help`: Print the help.
+ `n`, `new`: Print a new random topic to ask.
+ `s`, `solution`: Show a hint or solution for the previous topic.
+ `q`, `quit`: Quit the program.

Use the following commands to check out the topics:
+ `topics`: Print all the topics.
+ `topics --asked`: Print all the topics that have been asked.
+ `topics --not-asked`: Print all the topics that have not been asked yet.
+ `topics --asked <topi1c1> [,<topic2> ...]`: Add the <topic> to the asked topics.
+ `topics --not-asked <topic1> [,<topic2> ...]`: Remove the <topic> from the asked topics.
+ `topics --reset`: Reset the asked topics.
+ `topics --load [<path>]`: Load the json file with the topics. If the path is not given the directory finder will be opened.

Use the following commands to control your session:
+ `session --save [<file>]`: Save the session. If a file is given, this file is used. Normally this uses the extesion .sess.
+ `session --open [<file>]`: Load the session of the given path. If the file is not given the directory finder will be opened.

Use the following commands to enable or disable autosave:
+ `autosave`: Tells whether autosave is enabled or disabled.
+ `autosave --on`: Switches autosave to on.
+ `autosave --off`: Swites autosave to off.
+ `autosave --path <path>`: Sets the autosave path.

Use the following commands to print out in the command line:
+ `print <text>`: Prints the given text to the command line.
