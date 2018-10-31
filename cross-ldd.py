#!/usr/bin/python
# -*- coding: utf-8 -*

import os
import sys
import getopt
import re
import subprocess

s_LD_LIBRARY_PATH = []
s_TARGET_FILE = ""

def pretty_print(depArray):
    print("Deps of " + os.path.abspath(s_TARGET_FILE))
    for libs in depArray:
        print("     %s" % (libs["target"]))
        if len(libs["deps"]) == 0:
            print("          no deps")
        else:
            for sub in libs["deps"]:
                print("          %s" % (sub))

def usage():
    print("""Usage: cross-ldd.py [OPTION]... target-file
List depend shared library of target-file.

Mandatory arguments to long options are mandatory for short options too.
  -l, --ld-path              library search paths seperated by ‘:’, same as LD_LIBRARY_PATH.
""")

def parseArgs():
    global s_TARGET_FILE
    global s_LD_LIBRARY_PATH

    try:
        options,args = getopt.getopt(sys.argv[1:],"hl:", ["help","ld-path="])
    except getopt.GetoptError:
        usage()
        sys.exit()

    for name,value in options:
        if name in ("-h","--help"):
            usage()
            sys.exit()
        elif name in ("-l","--ld-path"):
            s_LD_LIBRARY_PATH = value.split(":")

    if(len(args) > 0):
        s_TARGET_FILE = args[0]
    else:
        usage()
        sys.exit()

def FindLibrary():
    libmap = {}

    for path in s_LD_LIBRARY_PATH:
        listfile=os.listdir(path)
        for file in listfile:
            #print(path+file)
            if not libmap.has_key(file):
                libmap[file] = os.path.abspath(path+file)

    return libmap

def FindDep(file,deps=None):
    if not deps:
        deps = []
    pattern = re.compile(r'\(NEEDED\)[ ]* Shared library:[ ]*\[(.*)\]')

    proc = subprocess.Popen("readelf -a " + file,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in proc.stdout.readlines():
        #print("=="+line+"--")
        match = pattern.search(line)
        if match:
            #print "=="+match.group(1)+"--"
            deps.append(match.group(1))

    return deps

s_depList = []
def SearchDeps(file,libmap,depArray):
    global s_depList
    targetname = os.path.basename(file)
    index = len(depArray)
    if not targetname in s_depList:
        depArray.append({"target":targetname,"deps":[]})
        s_depList.append(targetname)
    else:
        return

    deps = FindDep(file)
    deeperDeps = []
    for dep in deps:
        if dep not in libmap:
            depArray[index]["deps"].append(dep + " ==> Not Found")
        else:
            depArray[index]["deps"].append(dep + " ==> " + libmap[dep])
            deeperDeps.append(libmap[dep])

    for dep in deeperDeps:
        SearchDeps(dep,libmap,depArray)

if __name__=="__main__":
    parseArgs()

    libmap = FindLibrary()
    #print(libmap)

    depList = []
    depArray = []
    SearchDeps(s_TARGET_FILE,libmap,depArray)
    pretty_print(depArray)


