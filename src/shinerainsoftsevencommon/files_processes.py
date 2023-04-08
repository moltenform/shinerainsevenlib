
import subprocess

# returns tuple (returncode, stdout, stderr)
def run(listArgs, *, shell=False, createNoWindow=True,
        throwOnFailure=RuntimeError, stripText=True, captureOutput=True, silenceOutput=False,
        wait=True):
    
    import subprocess
    assertTrue(isfile(listArgs[0]) or 'which' not in dir(shutil) or shutil.which(listArgs[0]) or shell, 'file not found?', listArgs[0])
    kwargs = {}

    if sys.platform.startswith('win') and createNoWindow:
        kwargs['creationflags'] = 0x08000000

    if captureOutput and not wait:
        raise ValueError('captureOutput implies wait')

    if throwOnFailure and not wait:
        raise ValueError('throwing on failure implies wait')

    retcode = -1
    stdout = None
    stderr = None

    if captureOutput:
        sp = subprocess.Popen(listArgs, shell=shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

        comm = sp.communicate()
        stdout = comm[0]
        stderr = comm[1]
        retcode = sp.returncode
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()

    else:
        if silenceOutput:
            stdoutArg = open(os.devnull, 'wb')
            stderrArg = open(os.devnull, 'wb')
        else:
            stdoutArg = None
            stderrArg = None

        if wait:
            retcode = subprocess.call(listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs)
        else:
            subprocess.Popen(listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs)

    if throwOnFailure and retcode != 0:
        if throwOnFailure is True:
            throwOnFailure = RuntimeError

        exceptionText = 'retcode is not 0 for process ' + \
            str(listArgs) + '\nretcode was ' + str(retcode) + \
            '\nstdout was ' + str(stdout) + \
            '\nstderr was ' + str(stderr)
        raise throwOnFailure(getPrintable(exceptionText))

    return retcode, stdout, stderr


def runWithTimeout(args, *, shell=False, createNoWindow=True,
                  throwOnFailure=True, captureOutput=True, timeout=None, addArgs=None):
    addArgs = addArgs if addArgs else {}
    
    assertTrue(throwOnFailure is True or throwOnFailure is False or throwOnFailure is None,
        "we don't yet support custom exception types set here, you can use CalledProcessError")

    retcode = -1
    stdout = None
    stderr = None
    if sys.platform.startswith('win') and createNoWindow:
        addArgs['creationflags'] = 0x08000000

    import subprocess
    ret = subprocess.run(args, capture_output=captureOutput, shell=shell, timeout=timeout,
        check=throwOnFailure, **addArgs)

    retcode = ret.returncode
    if captureOutput:
        stdout = ret.stdout
        stderr = ret.stderr
    
    return retcode, stdout, stderr

def runWithoutWait(listArgs):
    p = subprocess.Popen(listArgs, shell=False)
    return p.pid
