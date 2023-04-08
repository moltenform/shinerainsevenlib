
class PersistedDict(object):
    data = None
    handle = None
    counter = 0
    persistEveryNWrites = 1

    def __init__(self, filename, warnIfCreatingNew=True,
            keepHandle=False, persistEveryNWrites=5):
        from .files import exists, writeall
        from .common_ui import alert
        self.filename = filename
        self.persistEveryNWrites = persistEveryNWrites
        if not exists(filename):
            if warnIfCreatingNew:
                alert("creating new cache at " + filename)
            writeall(filename, '{}')
        self.load()
        if keepHandle:
            self.handle = open(filename, 'w')
            self.persist()

    def load(self):
        import json
        from .files import readall
        txt = readall(self.filename, encoding='utf-8')
        self.data = json.loads(txt)

    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None

    def persist(self):
        import json
        from .files import writeall
        txt = json.dumps(self.data)
        if self.handle:
            self.handle.seek(0, os.SEEK_SET)
            self.handle.write(txt)
            self.handle.truncate()
        else:
            writeall(self.filename, txt, encoding='utf-8')

    def afterUpdate(self):
        self.counter += 1
        if self.counter % self.persistEveryNWrites == 0:
            self.persist()

    def set(self, key, value):
        self.data[key] = value
        self.afterUpdate()

    def setSubdict(self, subdictname, key, value):
        if subdictname not in self.data:
            self.data[subdictname] = {}
        self.data[subdictname][key] = value
        self.afterUpdate()

    def setSubsubdict(self, subdictname, key1, key2, value):
        if subdictname not in self.data:
            self.data[subdictname] = {}
        self.data[subdictname][key1][key2] = value
        self.afterUpdate()
        