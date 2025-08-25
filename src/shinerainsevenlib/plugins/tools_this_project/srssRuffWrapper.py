#!/usr/bin/env python3

from shinerainsevenlib.standard import *
from . import toolsThisProject

def main():
    toolsThisProject.chDirToProjectRoot()
    tools_any_project.addSrcLicense.go(['./src', './test'], newHeaderToWrite=newHeaderToWrite,
                                      excerptIndicatingDuplicate='Ben Fisher', 
                                      fileExts=['py'])

if __name__ == '__main__':
    main()
