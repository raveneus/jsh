import os, sys, subprocess, cmd
vars = {"PATH":"/usr/bin:/bin", "MODULES":""}

def getModules(vars):
    pass

class jsh(cmd.Cmd):
    def __init__(self, vars):
        cmd.Cmd.__init__(self)
        self.vars = vars

def main(vars):
    getModules(vars)
    m = jsh(vars)
    m.cmdloop()

if __name__ == '__main__':
    main(vars)
