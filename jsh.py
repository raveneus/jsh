import os, sys, subprocess, cmd, ConfigParser, imp, pwd, time, re
from socket import gethostname
global var
var = {"PATH":"/usr/bin:/bin", "MODULES":"", "HOME":"", "PROMPT":"/u@/h:/c* ", "status":"", "eval_dbg":""}
global y
global true
global null
true = "TRUE"
null = "NULL"
y = {}

"""
To-Do:
prepend "jsh: " to all errors
pipes
redirection of stdout to files
"""

class customStderr(file):
    def __init__(self):
        pass
    def write(self, stuff):
        sys.stderr.write(self, "jsh: " + stuff)
    def fileno(self):
        return sys.stderr.fileno()
stderr = customStderr()
    
def getToken(line, delimeter):
    token = ""
    if " " not in line:
        return line
    for letter in line:
        if letter != delimeter:
            token += letter
        else:
            return token
def getTokenList(line, delimeter):
    tokens = [""]
    for j in range(40):
        tokens.append("")
    i = 0
    for letter in line:
        if letter != delimeter:
            tokens[i] += letter
        else:
            i = i + 1
    return tokens
def fatal_error(msg, code):
    sys.stderr.write("fatal: jsh: " + msg + "\n")
    sys.quit(code)
def error(msg):
    sys.stderr.write("jsh: " + msg + "\n")
def variable(name, var):
    bad_char = ["!", "@", "#", "$", "%", "^", "&", "*", "-", "+", "=", "[", "]", "{", "}", "\\", "|", ";", ":", "\"", "'", ",", "<", ".", ">", "/", "?", "`", "~"]
    real_name = ""
    if "#" == name[0]:
        for letter in name[1:]:
            if letter not in bad_char:
                real_name += letter
            elif real_name == name[1:]:
                break
            else:
                break
        g = 0
        for b in bad_char:
            if b in name:
                g += 1
        if g == 0:
            real_name = name[1:]
        try:
            t = var[real_name]
            n = name.replace("#" + real_name, var[real_name])
            return n
        except:
            return null
    elif "@" == name[0]:
        for letter in name[2:]:
            if letter not in bad_char:
                real_name += letter
            elif real_name == name[2:]:
                break
            else:
                break
        try:
            t = var[real_name]
            n = name.replace("#" + real_name, var[real_name])
            return n
        except:
            return null
    else:
        return null
def sub(line, var):
    newline = ""
    for i, token in enumerate(getTokenList(line, " ")):
        for letter in token:
            if letter == "#":
                tmp = variable(token, var)
                if tmp == null:
                    error("the variable %s is uninitialized." % token[1:])
                    return null
                else:
                    token = tmp
                break
        if i == len(getTokenList(line, " ") ) - 1:
            newline += token
        else:
            newline += token + " "
    return newline
def prompt(line):
    user = pwd.getpwuid(os.getuid()).pw_name
    line = line.replace("/u", user)
    host = gethostname()
    line = line.replace("/h", host)
    cwd = os.getcwd().replace("/home/" + user, "~")
    line = line.replace("/c", cwd)
    t = time.strftime("%I:%M")
    line = line.replace("/t", t)
    d = time.strftime("%m/%d/%Y")
    line = line.replace("/d", d)
    line.replace("//", "/")
    return line
def construct(string_list):
    string = ""
    for i in range(len(string_list)):
        string += string_list[i] + " "
    string = string.rstrip(" ")
    return string
def num_handle(num):
    # only working with integers
    num = str(num)
    if num[0] != "@":
        return int(num)
    else:
        if " " in num:
            error("the contents of the \"@\" directive cannot have spaces inside.")
            return
        else:
            try:
                s = eval(num[1:])
                return str(s)
            except:
                error("@: error near " + num)
                return null
def handle(string_list):
    string = construct(string_list)
    quoted = re.findall(r'"([^"]*)"', string)
    tmp = string
    for quote in quoted:
        tmp = tmp.replace('"' + quote + '"', "/h")
    tmp = tmp.replace(" ", "\x90")
    for quote in quoted:
        tmp = tmp.replace("/h", quote, 1)
    return getTokenList(tmp, "\x90")
def construct1(args):
    ## only concatenate the elements of the list.
    result = ""
    for e in args:
        result += e
    return result
def evaluate(args, var):
    args = args[1:len(args) - 1]
    args = sub(args, var) # take care of variables
    args = args.rstrip()
    string = ""
    tmp = getTokenList(args, " ")
    tmp = handle(tmp) # take care of quotes
    tmp = filter(None, tmp)
    k = 0
    b = 0
    for k in range(len(tmp)):
        if "@" not in tmp[k] and "+" not in tmp[k] and "`" not in tmp[k] and "*" not in tmp[k] and "~" not in tmp[k]:
            b += 1
    if b < len(tmp):
        good = true
    else:
        var["eval_dbg"] = true
        string = args
        good = null
    for i, e in enumerate(tmp):
        if "@" in e:
            s = str(num_handle(e))
            if s == null:
                return
            tmp[i] = s
        if "`" in e:
            try :
                tmp[i] = subprocess.check_output(tmp[0][1:len(tmp[0]) - 1])
            except:
                tmp[i] = null
        if e == "+":
            tmp[i] = tmp[i - 1] + tmp[i + 1]
            tmp.__delitem__(i - 1)
            tmp.__delitem__(i)
        elif e == "*":
            tmp_str = ""
            for j in range(num_handle(tmp[i + 1])):
                tmp_str += tmp[i - 1]
            tmp.insert(i, tmp_str)
            tmp.__delitem__(i - 1)
            tmp.__delitem__(i)
            tmp.__delitem__(i)
        elif e == "~":
            if re.search(tmp[i - 1], tmp[i + 1]):
                tmp[i] = true
            else:
                tmp[i] = null
            tmp.__delitem__(i - 1)
            tmp.__delitem__(i)
    if good == true:
        string = construct1(tmp)
    return string
def handle_cmd(cmd, var):
    cmd = sub(cmd, var)
    to_eval = [""]
    evaled = [""]
    for j in range(10):
        to_eval.append("")
        evaled.append("")
    i = 0
    while cmd.find("(") != -1:
        to_eval[i] = cmd[cmd.find("("):cmd.find(")") + 1]
        cmd = cmd.replace(to_eval[i], "/h")
        i += 1
    to_eval = filter(None, to_eval)
    i = 0
    for to in to_eval:
        evaled[i]  = evaluate(to, var)
    cmd = cmd.replace(" ", "\x90")
    i = 0
    while cmd.find("/h") != -1:
        cmd = cmd.replace(cmd[cmd.find("/h"):cmd.find("/h") + 2], evaled[i])
    cmd_list = getTokenList(cmd, "\x90")
    cmd_list = filter(None, cmd_list)
    return cmd_list
def execute(cmd, var):
    cmd_list = handle_cmd(cmd, var)
    var["status"] = str(subprocess.call(cmd_list, stdin=sys.stdin, stdout=sys.stdout, stderr=stderr))
    
def init(var):
    global y
    parser = ConfigParser.ConfigParser()
    parser.read(".jshc")
    var["MODULES"] = parser.get("jsh", "MODULES")
    var["HOME"] = parser.get("jsh", "HOME")
    try :
        tmp = parser.get("jsh", "PATH")
        var["PATH"] = sub(tmp)
    except:
        pass
    try:
        tmp = parser.get("jsh", "PROMPT")
        p = prompt(tmp)
    except:
        p = prompt(var["PROMPT"])
    shell = jsh(p, var)
    for module in getTokenList(var["MODULES"], ", "):
        if module in y.keys():
            fatal_error(".jshc: the module %s already exists." % module, 1)
        if module == null:
            break
        else:
            y[module] = imp.load_source(module, self.var["HOME"] + "/modules/" + module + ".py")
    for module, m in y:
        if m and module:
            pass
        else:
            return
        setattr(shell, "do_" + module, m.run)
        setattr(shell, "help_" + module, m.help)
    return shell

class jsh(cmd.Cmd):
    def __init__(self, prompt, var):
        cmd.Cmd.__init__(self)
        self.var = var
        self.prompt = prompt
    def help_help(self):
        print "Usage: help [cmd]"
        print "help: show commands or get help on a command"
    def do_man(self, args):
        args = construct(handle_cmd(args, self.var))
        if os.path.isfile(self.var["HOME"] + "/.man/%s" % args) == False:
            error("that manpage is not found.")
            self.var["status"] = "1"
            return
        f = open(self.var["HOME"] + "/.man/%s" % args, "r")
        print f.read()
        f.close()
    def help_man(self):
        print "Usage: man [topic]"
        print "topic    the topic to get help on"
        print "man: extended help on a topic."
    def default(self, args):
        if args[0] == "(" and args[len(args) - 1] == ")":
            print evaluate(args, self.var)
        elif args[0] == "@":
            print num_handle(args)
        else:
            n = 0
            for p in getTokenList(self.var["PATH"], ":"):
                if os.path.isfile(p + "/" + getToken(args, " ")):
                    execute(args, var)
                else:
                    n = n + 1
            if n == len(getTokenList(self.var["PATH"], ":")):
                error(getToken(args, " ") + " is not a recognized command, module, or executable on the path.")
                self.var["status"] = 1
        self.prompt = prompt(var["PROMPT"])
    def do_exit(self, args):
        if args:
            error("exit requires 0 arguments.")
        else:
            return True
    def help_exit(self):
        print "Usage: exit"
        print "exit: exit jsh"
    def do_cd(self, args):
        if args[0] == "~":
            args = args.replace("~", "/home/" + pwd.getpwuid(os.getuid()).pw_name, 1)
        args = construct(handle_cmd(args, self.var))
        try:
            os.chdir(args)
        except:
            error("cd: no such directory " + args)
            self.var["status"] = "1"
        self.prompt = prompt(var["PROMPT"])
    def help_cd(self):
        print "Usage: cd [dir]"
        print "dir    the directory to change to"
        print "cd: change the current working directory"
    def do_set(self, args):
        args_list = handle_cmd(args, self.var)
        if "=" not in args_list:
            self.var["status"] = "1"
            error("equals sign missing.")
            return
        if args_list[0] == "status":
            self.var["status"] = "1"
            error("you may not set the value of #status.")
            return
        if args_list[0].find("_dbg"):
            self.var["status"] = "1"
            error("you may not set the value of " + args_list[0])
        if args_list[0][0] == "#":
            self.var["status"] = "1"
            error("you do not use the \"#\" symbol while assigning variables.")
            return
        self.var[args_list[0]] = args_list[2]
    def help_set(self):
        print "Usage: set [var] = [val]"
        print "var    variable to set"
        print "val    value to set the variable to"
        print "set: set the values of variables"
def main(var):
    menu = init(var)
    menu.cmdloop()

if __name__ == '__main__':
    main(var)
