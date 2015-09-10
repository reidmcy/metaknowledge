#!/usr/bin/env python3

"""This is intended for metaknowledge only and may not work with anything else"""
import inspect
import argparse
import os
import time
import metaknowledge
import importlib

documentedModules = ['tagFuncs','visual', 'journalAbbreviations']

docsPrefix = time.strftime("%Y-%m-%d-")


def makeHeader(title, excerpt):
    return """---
layout: page
title: {}
categories: docs
excerpt: {}
---
""".format(title, excerpt)


jekyllyHeader ="""---
layout: page
title: metaknowledge Docs
categories: docs
excerpt: the full documentation
---
<a name="metaknowledge"></a>"""

def argumentParser():
    parser = argparse.ArgumentParser(description="A simple script to genrate docs for metaknowledge")
    parser.add_argument("--output", "-o", default = 'metaknowledgeDocs.md', nargs='?')
    parser.add_argument("dir", default = os.path.normpath('.') ,nargs='?', help = 'Directory to write files to')
    return parser.parse_args()

def cleanargs(obj):
    argStr = inspect.formatargspec(*inspect.getfullargspec(obj))
    argStr =  argStr.replace(", *args", '').replace(", **kwargs", '').replace('self, ', '').replace('self', '')[1:-1]
    if len(argStr) > 0:
        return "(_{0}_)".format(argStr)
    else:
        return '()'


def cleanedDoc(obj, lvl):
    ds = inspect.getdoc(obj)
    lns = ds.split('\n')
    nds = ''
    for line in lns:
        if len(line) < 1:
            nds += '\n'
        elif line[0] == '#':
            nds += '#' * (lvl + 1) + "&nbsp;" * 3 + line[1:] + '\n'
        elif line[0] == '>':
            nds += "&nbsp;" * 12 + line[1:] + '\n'
        else:
            nds += "&nbsp;" * 6 + line + '\n'
    return '{}\n\n'.format(nds)

def writeFunc(fn, f, prefix = 'metaknowledge.', level = 4):
    #print("Writing {0}{1}".format(prefix, fn[0]))
    s = '<a name="{0}{1}"></a>{0}**{1}**{2}:\n\n'.format(prefix, fn[0], cleanargs(fn[1]))
    f.write(s)
    try:
        f.write(cleanedDoc(fn[1], lvl = level))
    except AttributeError:
        f.write("# Needs to be written\n\n")
        print("\033[93m{0}{1} had no docs\033[0m".format(prefix, fn[0]))

def writeClass(cl, f, prefix = 'metaknowledge.', level = 4):
    #print("Writing {0}{1}".format(prefix, cl[0]))
    s = '<a name="{0}{1}"></a>{0}**{1}**{2}:\n\n'.format(prefix, cl[0], cleanargs(cl[1].__init__))
    f.write(s)
    try:
        f.write(cleanedDoc(cl[1], lvl = level))
    except AttributeError:
        f.write("# Needs to be written\n\n")
        print("\033[93m{0}{1} had no docs\033[0m".format(prefix, cl[0]))

def writeMod(md, f, prefix = 'metaknowledge.', level = 3):
    #print("Writing {0}{1}".format(prefix, md[0]))
    f.write('{0} <a name="{1}{2}"></a>{1}**{2}**:\n\n'.format('#' * level, prefix, md[0]))
    f.write(cleanedDoc(md[1], lvl = level))
    for m in inspect.getmembers(md[1], predicate = inspect.isfunction):
        f.write("- - -\n\n")
        if m[0][0] != '_':
            writeFunc(m, f, prefix = '{0}{1}.'.format(prefix, md[0]), level = 4)

def proccessClass(cl, f):
    writeClass(cl, f)
    baseMems = inspect.getmembers(cl[1].__bases__[0])
    for m in inspect.getmembers(cl[1]):
        if m[0][0] == '_' or m in baseMems:
            pass
        elif inspect.isfunction(m[1]):
            writeFunc(m, f, prefix = '{}.'.format(cl[0]), level = 4)

def writeClassFile(name, typ):
    fname = docsPrefix + "{}.md".format(name)
    f = open(fname, 'w')
    f.write(makeHeader(name, "The {} Class".format(name)))
    proccessClass((name, typ), f)

def writeModuleFile(mod):
    fname = docsPrefix + "{}.md".format(mod)
    f = open(fname, 'w')
    f.write(makeHeader(mod, "The {} Module".format(mod)))
    module = importlib.__import__('metaknowledge.{}'.format(mod))
    funcs = []
    for m in inspect.getmembers(module):
        if inspect.isbuiltin(m[1]) or m[0][0] == '_':
            pass
        elif inspect.isfunction(m[1]):
            funcs.append(m)
    first = True
    for fnc in funcs:
        if first:
            first = False
        else:
            f.write("- - -\n\n")
        writeFunc(fnc, f)

def writeMainBody(funcs, vrs, exceptions):
    f = open(docsPrefix + "metaknowledge.md", 'w')
    f.write(makeHeader("metaknowledge", "The metaknowledge Package"))
    first = True
    for fnc in funcs:
        if first:
            first = False
        else:
            f.write("- - -\n\n")
        writeFunc(fnc, f)
    first = True
    for excpt in exceptions:
        if first:
            first = False
        else:
            f.write("- - -\n\n")
        proccessClass(excpt, f)


def main(args):
    wDir = os.path.expanduser(os.path.normpath(args.dir))
    print(wDir)
    if not os.path.isdir(wDir):
        try:
            os.mkdir(wDir)
        except OSError:
            print('Creating the directory {} failed'.format(os.dir))
            return 1
    os.chdir(wDir)
    classes = []
    funcs = []
    vrs = []
    exceptions = []
    builtins = []
    for m in inspect.getmembers(metaknowledge):
        if inspect.isbuiltin(m[1]) or m[0][0] == '_':
            builtins.append(m)
        elif inspect.isclass(m[1]):
            if issubclass(m[1], Exception):
                exceptions.append(m)
            else:
                classes.append(m)
        elif inspect.isfunction(m[1]):
            funcs.append(m)
        else:
            vrs.append(m)

    writeMainBody(funcs, vrs, exceptions)
    for cls in classes:
        writeClassFile(*cls)
    for mod in documentedModules:
        writeModuleFile(mod)


def mkDocs():
    args = argumentParser()
    main(args)

if __name__ == '__main__':
    mkDocs()