
# shinerainsoftsevencommon
# Released under the LGPLv3 License

import ordering

prefix = r'''# shinerainsoftsevencommon
# Released under the LGPLv3 License'''


if __name__ == '__main__':
    prefix = prefix.strip()
    ordering.addHeaderToPyFiles('.', importStar=False, prefix=prefix, isPackage=True)
    ordering.addHeaderToPyFiles('../files', importStar=True, prefix=prefix, isPackage=True)
    ordering.addHeaderToPyFiles('../jslike', importStar=True, prefix=prefix, isPackage=True)
    ordering.addHeaderToPyFiles('..', importStar=True, prefix=prefix, isPackage=True)

