class Simpledb:
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return ("<" + self.__class__.__name__ + " file=" + str(self.filename) + ">")

    def insert(self, key, value):
        filename = self.filename
        # tab or \t will be the delimiter.
        t = open(self.filename, "a")
        t.write(key + '\t' + value + '\n')
        t.close()

    def select_one(self, key):
        filename = self.filename
        f = open(filename, 'r')
        for row in f:
            (k, v) = row.split('\t', 1)
            if k == key:
                return v[:-1]
        f.close()

    def delete(self, key):
        filename = self.filename
        f = open(filename, 'r')
        result = open('result.txt', 'w')
        for (row) in f:
            (k, v) = row.split('\t', 1)
            if k != key:
                result.write(row)
        f.close()
        result.close()
        import os
        os.replace('result.txt', filename)

    def update(self, key, value):
        filename = self.filename
        f = open(filename, 'r')
        result = open('result.txt', 'w')
        for (row) in f:
            (k, v) = row.split('\t', 1)
            if k == key:
                result.write(key + '\t' + value + '\n')
            else:
                result.write(row)
        f.close()
        result.close()
        import os
        os.replace('result.txt', filename)
