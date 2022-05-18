from tkinter.filedialog import askdirectory
import os

opath = askdirectory(title='Select Project Folder')

existing = False

for path, subdirs, files in os.walk(opath):

    if len(files) > 0:
        fname = path.replace(opath, '')[1:]
        fname = fname.replace('\', '-')
        if existing:
            outs.close()
        outs = open(opath + '\' + fname + '.txt', 'w')
        existing = True
    for name in files:
        if name.upper()[-3:] == 'DGN':
            proper = os.path.join(path, name)
            proper = proper.replace('/', '\')
            outs.write(proper + '\n')