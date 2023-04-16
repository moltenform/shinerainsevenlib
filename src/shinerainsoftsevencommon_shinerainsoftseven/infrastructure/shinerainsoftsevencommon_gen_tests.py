
# shinerainsoftsevencommon
# Released under the LGPLv3 License

# an internal script run by the developers

from shinerainsoftsevencommon.infrastructure import gen_tests

if __name__ == '__main__':
    dirSrcModules = '..'
    dirTests = '../../../tests'
    cfg = 'shinerainsoftsevencommon_gen_tests.cfg'
    gen_tests.goGenTests(dirSrcModules, dirTests, cfg, recurse=True)
    