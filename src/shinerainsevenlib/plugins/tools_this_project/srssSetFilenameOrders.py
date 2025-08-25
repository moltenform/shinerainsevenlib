#!/usr/bin/env python3

# you can change the order the lists below,
# then run the script and it will
# 1) rename the files with different order prefixes
# 2) print out a new data structure to be copied back into this file.

sourceCode = [
{'dir': './files', 
 'files': strToList('''
m0_files_wrappers.py
m1_files_listing.py
m2_files_higher.py
 ''')},
{'dir': './core', 
 'files':
strToList('''
m0_text_io.py
m1_core_util.py
m2_core_data_structures.py
m3_core_nonpure.py
m4_core_ui.py
m5_batch_util.py
m6_jslike.py
''')},
]

if __name__ == '__main__':
    setFilenameOrders(sourceCode, previewOnly=True)

