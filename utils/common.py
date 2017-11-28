# coding:utf-8
# Created by yang
import hashlib
import time


def hash_str(*args):
    md = hashlib.md5()
    for i in args:
        md.update(bytes(str(i), encoding="utf-8"))
    return md.hexdigest()


if __name__ == '__main__':
    s = hash_str("xx")
    print(s)
