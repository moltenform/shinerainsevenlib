def runWithoutWaitUnicode(listArgs):
    # in Windows in Python2, non-ascii characters cause subprocess.Popen to fail.
    # https://bugs.python.org/issue1759845

    import subprocess
    if isPy3OrNewer or not sys.platform.startswith('win') or all(isinstance(arg, str) for arg in listArgs):
        # no workaround needed in Python3
        p = subprocess.Popen(listArgs, shell=False)
        return p.pid
    else:
        import winprocess
        import types
        if isinstance(listArgs, types.StringTypes):
            combinedArgs = listArgs
        else:
            combinedArgs = subprocess.list2cmdline(listArgs)

        combinedArgs = unicode(combinedArgs)
        executable = None
        close_fds = False
        creationflags = 0
        env = None
        cwd = None
        startupinfo = winprocess.STARTUPINFO()
        handle, ht, pid, tid = winprocess.CreateProcess(executable, combinedArgs,
            None, None,
            int(not close_fds),
            creationflags,
            env,
            cwd,
            startupinfo)
        ht.Close()
        handle.Close()
        return pid