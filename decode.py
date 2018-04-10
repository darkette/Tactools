#!/usr/bin/python3

import sys
import os
import argparse
#import re
global d_result
d_result = []
def search(fh, value):
    lo = 0
    hi = os.stat(fh.fileno()).st_size

    while True:
        mid = int((lo + hi) / 2)
        if mid:
            fh.seek(mid-1)
            junk = fh.readline()
        else:
            fh.seek(mid)
        start = fh.tell()
        tokens = fh.readline().split()
        #rec = hex(tokens[0])
        if not tokens:
            return
        rec = tokens[0]

        if hi == lo:
            #fh.seek(start)
            if hi > 0:
                fh.seek(hi-1)
            tokens = fh.readline().split()
            #print(num, rec, tokens[0], tokens[2])
            if (tokens[2].decode()) != "memcpy":
                d_result.append(tokens[2].decode())
                # print(result)
                return rec
            else:
                return rec
        if value > rec.lower():
            lo = mid + 1
        else:
            hi = mid


def decode_corefile(m_file,c_file):
    mapFile = open(m_file,'rb')
    crashFile = open(c_file,'rb')
    d_result.clear()
    flag = False
    lines = []
    while 1:
        line = crashFile.read()
        if not line:
            break
        #line = line.rstrip(b'\n')
        #tokens = re.split(rb'\s+\n*', line)
        tokens = line.split()
        for token in tokens:
            if token == b".":
                flag = True
                break
            lines.append(token)
        if flag:
            break

    if crashFile is not sys.stdin:
        crashFile.close()

    for num in lines:
        search(mapFile, num.lower())
        mapFile.seek(0)
    mapFile.close()
    print("Result in python is ",d_result)
    return d_result
if __name__ == "__main__":
    main()
