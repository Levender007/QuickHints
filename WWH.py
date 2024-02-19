import hashlib


def checkHash(path, h):
    x = getFileHash(path)
    return x == h


def getFileHash(path):
    x = -1
    try:
        x = hashlib.md5(open(path, 'rb').read()).hexdigest()
    except Exception as e:
        print(e.args)
    return x
