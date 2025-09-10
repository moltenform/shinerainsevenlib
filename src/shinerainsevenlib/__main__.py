
import sys

def main(argv):
    if '--lint-wrapper' in argv:
        from shinerainsevenlib.plugins.tools_any_project import lintWrapper
        retcode = lintWrapper.main(argv)
    else:
        print('Usage:')
        print('python -m shinerainsevenlib --lint-wrapper')
        retcode = 1
    
    return retcode

if __name__ == '__main__':
    retcode = main(sys.argv)
    sys.exit(retcode)

