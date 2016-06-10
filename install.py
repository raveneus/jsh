import os, pwd, subprocess, sys, ConfigParser

def replace_config():
    user = pwd.getpwuid(os.getuid()).pwname
    f = open(".jshc", "r")
    old_contents = f.read()
    f.close()
    new_contents = old_contents.replace("^u", user)
    f = open(".jshc", "w")
    f.write(new_contents)
    f.close()
def getHome():
    p = ConfigParser.ConfigParser()
    p.read(".jshc")
    return p.get("jsh", "HOME")
def move():
    home = getHome()
    code = subprocess.call(["mv", "*", home])
    subprocess.call(["chmod", "a+x", "jsh"])
    if code != 0:
        subprocess.check_output(["mv", "*", home], stderr=sys.stdout)
    else:
        print "Please enter your password so this can install a link to /usr/bin/jsh"
        code = subprocess.call(["sudo", "ln", "-s", "jsh", "/usr/bin"])
        if code == 0:
            print "Done!"
            sys.quit(0)
        else:
            print "The sudo command failed."
if __name__ == '__main__':
    replace_config()
    move()
