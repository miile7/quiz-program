import os
import sys
import math
import json
import random
import datetime

programname = "Quiz-Program"
version = "1.1"
title = None
topics = []
solutions = {}
asked = []
autosave = True
autosave_path = None
current_topic = None
working_directory = os.path.dirname(os.path.abspath(__file__))

def program_cycle(msg = None, commands = None):
    global title, topics, solutions, current_topic
    
    if isinstance(msg, str) and len(msg) > 0:
        msg = "\n" + msg
    else:
        msg = ""
    
    cls()
    if not isinstance(topics, list) or len(topics) == 0:
        text = (programname + "\n" + 
                "=" * len(programname) + "\n" + 
                "Load a .json file to initialize the topics." + 
                msg)
        
        path = find_file(text, extensions=".json")
        
        print(path)
        
        if path == None:
            sys.exit(0)
        try:
            title, topics, solutions = load_topic_file(path)
            msg = ""
        except BaseException as e:
            msg = str(e)
            title = None
            topics = None
            solutions = None
        
        if solutions == None:
            solutions = {}
        
        if topics is None:
            program_cycle("\nError:\nCould not load file '{}': {}\n".format(path, msg))
        else:
            name = os.path.basename(path)
            name = os.path.splitext(name)[0] + ".sess"
            path = os.path.join(os.path.dirname(path), name)
            
            program_cycle(msg, (("autosave", "--path", path),
                                ("session", "--open", path)))
    else:
        print(title + " - " + programname)
        print("=" * len(title) + "===" + "=" * len(programname) + "\n")
        print(("This program will ask you about {}. It will select the topic " + 
               "randomly out of {} loaded topics (in your .json topic file). " + 
               "To quit press [Q]. For a new random topic press [N]. For the " + 
               "corresponding solution (if given) press [S]." + 
               "For further commands type 'help' or [h].").format(title, len(topics)))
        print(msg, end="")
    
    ret = None
    command = None
    
    if isinstance(commands, (list, tuple)):
        multiple_commands = False
        for command in commands:
            if isinstance(command, (list, tuple)):
                multiple_commands = True
                execute(*command)
        
        if not multiple_commands:
            execute(*commands)
    
    while True:
        if isinstance(command, str):
            command = command.split(" ")
            ret = execute(*command)
        
        if ret == False:
            sys.exit(0)
        
        if (isinstance(solutions, dict) and len(solutions) > 0 and 
            isinstance(current_topic, str) and current_topic in solutions and
            str(solutions[current_topic]).strip() != ""):
            solutions_txt = ", [S]olution"
        else:
            solutions_txt = ""
            
        command = input("\n\n[N]ew topic" + solutions_txt + ", [H]elp or [Q]uit? ")
    
    sys.exit(0)

def find_file(text = "Find a file", start_path = None, extensions = None, force_file = True, cache_directory = None):
    """
    Parameters
    ----------
        extensions : list or tuple
            A list of extensions WITH the leading dot
    """
    global working_directory
    
    if not isinstance(start_path, str):
        start_path = working_directory
    
    if isinstance(extensions, str):
        extensions = (extensions, )
    
    if not isinstance(cache_directory, str):
        cache_directory = working_directory
    
    cache_path = os.path.join(cache_directory, ".filecache")
    
    n = 5 # the number of paths to save
    data = {}
    last_paths = []
    try:
        with open(cache_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            if "last-paths" in data:
                last_paths = data["last-paths"]
    except:
        pass
    
    cls()
    print(text, end=" ")
    print("Use /q to quit.", end="\n\n")
    
    if len(last_paths) > 0:
        print("\nLast used files, use /<n> to select the file:")
        
        for i, path in enumerate(last_paths[0:n]):
            print("  /{0:>{2}}: {1}".format(i, path, math.floor(math.log(n, 10))))
        
    available_files = []
    for root, dirs, files in os.walk(start_path):
        print("\n{}".format(start_path))
        print("  ..")
        
        for directory in dirs:
            print("  {}/".format(directory))
        
        for file in files:
            if file == ".filecache" and root == cache_directory:
                continue
            elif isinstance(extensions, (list, tuple)):
                ext = os.path.splitext(file)[1]
                
                if ext not in extensions:
                    continue
            
            available_files.append(file)
            print("  {}".format(file))
    
    cmd = input("\nSelect file: ")
    path = None
    
    if cmd.lower() == "/q":
        return None
    elif cmd[0] == "/":
        try:
            num = int(cmd[1:])
            
            if num >= 0 and num < len(last_paths):
                path = last_paths[num]
        except:
            pass
    elif cmd[-1] == "/" or cmd == "..":
        path = find_file(text, os.path.join(start_path, cmd), extensions)
    elif cmd in available_files:
        path = os.path.join(start_path, cmd)
    
    if path is None and force_file:
        path = find_file(text, start_path, extensions, force_file)
    
    if path is not None:
        if path in last_paths:
            last_paths.remove(path)
        
        last_paths.insert(0, path)
        data["last-paths"] = last_paths[0:n]
        try:
            with open(cache_path, "w", encoding="utf-8") as file:
                json.dump(data, file)
        except Exception as e:
            print("Error when saving to cache: {}".format(e))
    
    return path

def load_topic_file(path):
    title = None
    topics = None
    solutions = None
    
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            if "title" in data and isinstance(data["title"], str):
                title = data["title"]
            else:
                path = os.path.basename(path)
                title = os.path.splitext(path)[0]
            
            if "topics" in data and len(data["topics"]) > 0:
                if isinstance(data["topics"], (list, tuple)):
                    topics = list(data["topics"])
                elif isinstance(data["topics"], dict):
                    topics = list(data["topics"].keys())
                    solutions = dict(data["topics"])
                else:
                    print("Cannot parse the 'topcis'.")
        
        return title, topics, solutions
    except Exception as e:
        raise e

def execute(*command):
    global title, asked, programname, autosave, autosave_path, topics, version, current_topic, solutions
    
    command = list(command)
    
    if len(command) > 0:
        if command[0].lower() == "topics":
            if len(command) > 1:
                if command[1].lower() == "--asked":
                    if len(command) > 2:
                        command[2] = " ".join(command[2:]).split(",")
                        for cmd in command[2]:
                            cmd = cmd.strip()
                            if cmd in topics:
                                index = topics.index(cmd)
                                asked.append(topics[index])
                                print("Added {} to asked questions.".format(
                                        topics[index]))
                            else:
                                print("Did not find the topic '{}'".format(
                                        cmd))
                        exec_autosave()
                    else:
                        print("Asked topics ({}/{}):".format(len(asked),
                                             len(topics)))
                        for topic in asked:
                            print("\t- " + topic)
                elif command[1].lower() == "--not-asked":
                    if len(command) > 2:
                        command[2] = " ".join(command[2:]).split(",")
                        for cmd in command[2]:
                            cmd = cmd.strip()
                            if cmd in topics:
                                if cmd in asked:
                                    index = asked.index(cmd)
                                    print("Removed {} from asked questions.".format(
                                            topics[index]))
                                    del asked[index]
                            else:
                                print("Did not find the topic '{}'".format(
                                        cmd))
                        exec_autosave()
                    else:
                        print("Not asked topics ({}/{}):".format(
                                len(topics) - len(asked), len(topics)))
                        for topic in topics:
                            if topic in asked:
                                continue
                            
                            print("\t- " + topic)
                elif command[1].lower() == "--reset":
                    asked = []
                    exec_autosave()
                elif command[1].lower() == "--load":
                    if len(command) > 2:
                        path = " ".join(command[2:])
                        try:
                            ttl, tpcs, slts = load_topic_file(path)
                        except:
                            ttl = None
                            tpcs = None
                            slts = None
                        
                        if tpcs is not None:
                            topics = tpcs
                            if slts == None:
                                solutions = {}
                            else:
                                solutions = slts
                                
                            print(("Successfully loaded {} topics ({} solutions) " + 
                                   "from file '{}'").format(len(topics), 
                                               len(solutions), path))
                            
                            if isinstance(str, ttl) and ttl != title:
                                title = ttl
                                print("\n= = =\n\nThis program will now ask " + 
                                      "about {}".format(title))
                        else:
                            print("Could not load the topics file.")
                    else:
                        execute(command[0], command[1], find_file(
                                "Load the topics file",
                                extensions=".json"))
                else:
                    print(topics_help())
            else:
                print("Topics ({}): ".format(len(topics)))
                for topic in topics:
                    print("\t- " + topic)
        elif command[0].lower() == "session":
            if len(command) > 1:
                if command[1].lower() == "--save":
                    time = datetime.datetime.today().strftime('%Y-%m-%d')
                    data = {"time": time,
                            "programname": programname,
                            "version": version,
                            "asked-topics": asked}
                    file = None
                    path = None
                    
                    if len(command) > 2:
                        path = " ".join(command[2:])
                    
                    try:
                        file = open(path, "w", encoding="utf-8")
                    except:
                        path = None
                    
                    if path is None:
                        path = os.path.join(os.environ["TMP"], 
                                            programname + "-" + time + ".sess")
                        try:
                            file = open(path, "w", encoding="utf-8")
                        except Exception as e:
                            print("Could not open a file to write: {}".format(e))
                    
                    if file is not None:
                        json.dump(data, file)
                        file.close()
                        
                        print("Saved session to '{}'.".format(path))
                elif command[1].lower() == "--open":
                    if len(command) > 2:
                        path = " ".join(command[2:])
                        
                        try:
                            file = open(path, "r", encoding="utf-8")
                            
                            data = json.load(file)
                            file.close()
                            
                            if ("asked-topics" in data and 
                                isinstance(data["asked-topics"], list)):
                                asked = data["asked-topics"]
                            else:
                                asked = []
                            
                            execute("autosave", "--path", path)
                            print(("Successfully loaded session. {} of {} " + 
                                   "topics are asked already").format(len(asked),
                                                                     len(topics)))
                        except Exception as e:
                            print("Could not open a file to write: {}".format(e))
                    else:
                        execute(command[0], command[1], find_file(
                                "Load the session file",
                                extensions=".sess"))
                else:
                    print(session_help())
        elif command[0].lower() == "autosave":
            if len(command) > 1:
                if command[1].lower() == "--on":
                    if len(command) > 2:
                        execute("autosave", "--path", command[2:])
                    autosave = True
                    print("Autosave is now on.")
                elif command[1].lower() == "--off":
                    autosave = False
                    print("Autosave is now off.")
                elif command[1].lower() == "--path":
                    if len(command) > 2:
                        autosave_path = " ".join(command[2:])
                    else:
                        print("There is no path given.")
                else:
                    print(autosave_help())
            else:
                if autosave:
                    print("Autosave is on. Save file is '{}'".format(
                            autosave_path))
                else:
                    print("Autosave is off.")
        elif command[0].lower() == "print":
            if len(command) > 1:
                print(command[1])
            else:
                print(print_help())
        elif "help" in command[0].lower() or command[0].lower() == "h":
            print(general_help())
        elif (command[0].lower() == "n" or command[0].lower() == "new" or
              command[0] == ""):
            tmp = list(set(topics) - set(asked))
            
            if len(tmp) == 0:
                print("All topics have been asked. To reset the questions use:" + 
                      "\n\t topics --reset")
            else:
                if len(tmp) > 1:
                    current_topic = tmp[random.randint(0, len(tmp) - 1)]
                else:
                    current_topic = tmp[0]
                asked.append(current_topic)
                print(current_topic + "\t\t({}/{})".format(len(asked), len(topics)))
            
                exec_autosave()
        elif command[0].lower() == "s" or command[0].lower() == "solution":
            if (isinstance(current_topic, str) and current_topic in solutions and
                str(solutions[current_topic]).strip() != ""):
                print(solutions[current_topic])
            else:
                print("Sorry, no solution/hint given. :(")
        elif command[0].lower() == "q" or command[0].lower() == "quit":
            return False
        else:
            print("Command {} is not defined.".format(command[0]))

def exec_autosave():
    global autosave, autosave_path
    
    if autosave:
        print("Autosave: ", end="")
        if isinstance(autosave_path, str):
            execute("session", "--save", autosave_path)
        else:
            execute("session", "--save")

def general_help():
    global title
    
    return ("\nThis program will ask you about {}. The following commands are " + 
            "available:" + 
            "\n\th, help: Print the help." + 
            "\n\tn, new: Print a new random topic to ask." + 
            "\n\ts, solution: Show a hint or solution for the previous topic." + 
            "\n\tq, quit: Quit the program." + 
            "\n" + 
            topics_help() + 
            "\n" + 
            session_help() +  
            "\n" + 
            autosave_help() + 
            "\n" + 
            print_help()).format(title)

def topics_help():
    return ("\nUse the following commands to check out the topics:" + 
            "\n\ttopics: Print all the topics." + 
            "\n\ttopics --asked: Print all the topics that have been asked."
            "\n\ttopics --not-asked: Print all the topics that have not been " + 
            "asked yet." + 
            "\n\ttopics --asked <topi1c1> [,<topic2> ...]: Add the <topic> to " + 
            "the asked topics." + 
            "\n\ttopics --not-asked <topic1> [,<topic2> ...]: Remove the <topic> " + 
            "from the asked topics." + 
            "\n\ttopics --reset: Reset the asked topics." + 
            "\n\ttopics --load [<path>]: Load the json file with the topics. If" + 
            "\n\t\tthe path is not given the directory finder will be opened.")

def session_help():
    return ("\nUse the following commands to control your session:" + 
            "\n\tsession --save [<file>]: Save the session. If a file is " + 
            "given, this file is used. \n\t\tNormally this uses the extesion .sess." + 
            "\n\tsession --open [<file>]: Load the session of the given path. If" + 
            "\n\t\tthe file is not given the directory finder will be opened.")

def autosave_help():
    return ("\nUse the following commands to enable or disable autosave:" + 
            "\n\tautosave: Tells whether autosave is enabled or disabled." + 
            "\n\tautosave --on: Switches autosave to on." + 
            "\n\tautosave --off: Swites autosave to off." + 
            "\n\tautosave --path <path>: Sets the autosave path.")

def print_help():
    return ("\nUse the following commands to print out in the command line:" + 
            "\n\tprint <text>: Prints the given text to the command line.")

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
    
if __name__ == "__main__":
    program_cycle();