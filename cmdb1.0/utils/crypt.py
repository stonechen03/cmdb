#encoding: utf-8
import hashlib

def md5_str(string, salt=''):
    md5 = hashlib.md5()
    if salt != '':
        string = '%s$$%s' % (salt, string)
    md5.update(str(string))
    return md5.hexdigest()

def md5_file(path):
    fhandler = open(path, 'rb')
    md5 = hashlib.md5()
    for line in fhandler:
        md5.update(str(line))

    fhandler.close()
    return md5.hexdigest()

if __name__ == '__main__':
    for i in range(10):
        print md5_str('abc', i)

    print md5_str('abc', '1')
