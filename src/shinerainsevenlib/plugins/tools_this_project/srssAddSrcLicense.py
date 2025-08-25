#!/usr/bin/env python3

from shinerainsevenlib.standard import *
from . import toolsThisProject

def main():
    toolsThisProject.chDirToProjectRoot()
    tools_any_project.ruffWrapper.cleanupAfterRuffAll('../test')
    tools_any_project.ruffWrapper.cleanupAfterRuffAll('../src')

if __name__ == '__main__':
    main()
