import os, sys, subprocess, cmd, ConfigParser
vars = {"PATH":"/usr/bin:/bin", "MODULES":""}

def getModules(vars):
    parser = ConfigParser.ConfigParser()
    parser.open(".jshc")
    vars["MODULES"] = parser.get("jsh", "MODULES")


class jsh(cmd.Cmd):
    def __init__(self, vars):
        cmd.Cmd.__init__(self)
        self.vars = vars
    def help_help(self):
        print "Usage: help [cmd]"
        print "help: show commands or get help on a command"

def main(vars):
    getModules(vars)
    m = jsh(vars)
    m.cmdloop()

if __name__ == '__main__':
    main(vars)
