#!/usr/bin/python3

import sys
import os
import re
import gzip
import q_jira
import gdb_expect
# import re
# global d_result
# d_result = []
# raw_stack = []

def search(fh, value, is_b, is_fx):
    lo = 0
    hi = os.stat(fh.fileno()).st_size
    raw_stack = ''
    d_result = ''
    full_line = ''

    while True:
        mid = int((lo + hi) / 2)
        if mid:
            fh.seek(mid-1)
            junk = fh.readline()
        else:
            fh.seek(mid)
        start = fh.tell()
        tokens = fh.readline().split()
        # rec = hex(tokens[0])
        if not tokens:
            return
        if is_fx:
            rec = tokens[1]
        else:
            rec = tokens[0]
        # print("Value is ", value)
        # print("Rec is", rec)
        if hi == lo:
            # fh.seek(start)
            if hi > 0:
                fh.seek(hi-1)
            tokens = fh.readline().split()
            # print(rec, tokens[0], tokens[2])
            if is_fx:
                my_t = tokens[0]
            else:
                my_t = tokens[2]
            if is_b:
                print("my_T is:", my_t.decode())
                if (my_t.decode()) not in {'memcpy', 'genGetRem'}:
                    full_line = my_t.decode()
                    raw_stack = my_t.decode()
                    # d_result.append(my_t.decode())
                    # raw_stack.append(my_t.decode())
            else:
                full_line = value + ' ' + my_t
                raw_stack = my_t
                # d_result.append(full_line)
                # raw_stack.append(my_t)
                # print(d_result)
            return [rec, full_line, raw_stack]

        if value > rec.lower():
            lo = mid + 1
        else:
            hi = mid


def decode_t(m_file, c_file, file_flag, m_time, m_path, is_fx, is_j):
    mapFile = open(m_file, 'r')
    raw_stack = []
    d_result = []
    j_str = []
    # if raw_stack:
    #     raw_stack.clear()
    is_b = 0
    print('file flag', file_flag)
    if file_flag:
        print('checkpoint1')
        texttodecode_file = open(c_file, 'r')
        file_open = 1

    flag = False
    lines = []
    i = 0
    j = 0
    regex_refcnt = re.compile("(.*)(cnt=)([0-9]+)")
    regex_symbol = re.compile("([0-9a-f]{8})")

    while 1:
        if file_flag and file_open:
            line = texttodecode_file.read()
        else:
            line = c_file
            line = c_file + ' END'
        print('Line is', line)
        if not line:
            break
        # line = line.rstrip(b'\n')
        # tokens = re.split(rb'\s+\n*', line)
        tokens = line.split()
        for token in tokens:
            print("Token is ", token)
            if token == "END":
                flag = True
                print("Flag is", flag)
                break
            lines.append(token)
        if flag:
            break

        if file_flag:
            texttodecode_file.close()
            file_open = 0

    for num in lines:
        print("num is ", num)
        print("Match refcnt", re.match(regex_refcnt, num))
        print("Match symbol", re.match(regex_symbol, num))
        # print("lines is ", lines)
        if (i == 0) and (j == 0):
            d_result.clear()
            d_result.append('#######################')
            d_result.append('Decoder Information:')
            d_result.append('Using symbol file in: ' + m_path)
            d_result.append('This prod.map was built on: ' + m_time)
            d_result.append('#######################')
        if re.match(regex_symbol, num) is not None:
            j += 1
            search(mapFile, num, is_b, is_fx)
            foo = search(mapFile, num, is_b, is_fx)
            if foo is not None:
                print('foo1', foo[1])
                print('foo2', foo[2])
                d_result.append(foo[1])
                raw_stack.append(foo[2])
                print('raw_stack', raw_stack)
                print('decoder result', d_result)
            mapFile.seek(0)
        elif re.match(regex_refcnt, num) is not None:
            i += 1
            d_result.append('########################')
            d_result.append('Stacktrace ' + str(i) + ' ' + num)
            d_result.append('########################')
    mapFile.close()
    print("Result in python is ", d_result)
    if not raw_stack:
        d_result.append('No matches found in Symbol File!')
        return d_result
    else:
        if is_j:
            print('Raw Stack', raw_stack)
            j_result = q_jira.jsearch(raw_stack)
            if not j_result:
                d_result.append('########################')
                d_result.append('No Jira match, this could be a new defect')
                d_result.append('########################')
            else:
                d_result.append('########################')
                d_result.append('Jira Matches:')
                for j_element in j_result:
                    print('j_element', j_element)
                    d_result.append(j_element)
                d_result.append('########################')
                print("Jira result is: ", j_result)
    return d_result

# This function is deprecated because it doesn't work :(
# Keeping it in for now.. It is the old decodeBacktrace script
def decode_corefile(m_file, c_file, m_time, m_path, is_fx, is_j):
    raw_stack = []
    d_result = []
    mapFile = open(m_file, 'rb')
    is_b = 1
    if c_file.endswith('.gz'):
        crashFile = gzip.open(c_file, 'rb')
    else:
        crashFile = open(c_file, 'rb')
    # d_result.clear()
    flag = False
    lines = []
    while 1:
        line = crashFile.read()
        if not line:
            break
        # line = line.rstrip(b'\n')
        # tokens = re.split(rb'\s+\n*', line)
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
        search(mapFile, num.lower(), is_b, is_fx)
        mapFile.seek(0)
    mapFile.close()
    print("Result in python is ", d_result)
    if not raw_stack:
        d_result.append('No matches found in Symbol File!')
        return d_result
    else:
        if is_j:
            j_result = q_jira.jsearch(raw_stack)
            if not j_result:
                d_result.append('########################')
                d_result.append('No Jira match, this could be a new defect')
                d_result.append('########################')
            else:
                d_result.append('########################')
                d_result.append('Jira Matches:')
                for j_element in j_result:
                    print('j_element', j_element)
                    d_result.append(j_element)
                d_result.append('########################')
                print("Jira result is: ", j_result)
    return d_result

def decode_gdb(gdb_path, c_file, m_time, m_path, im_type, is_j):
    icx_plat = ''
    # mapFile = open(m_file, 'rb')
    is_b = 0
    # ToDo Check file begins with ss_core
    if c_file.endswith('.gz'):
         print('Found a gzipped file..')
         # TODO Check file is Elf format and valid core
         crashFile = gzip.open(c_file, 'rb')
         temp_content = crashFile.read()
         f_name, f_ext = os.path.splitext(c_file)
         f = open(f_name,'wb+')
         f.write(temp_content)
         f.close()
         c_file = f_name

    # d_result.clear()
    flag = False
    # crashFile.close()
    print('IM type',im_type)
    # if plat_o == 'GUESS':
    if im_type == "/SP/Router/" or im_type == "/SP/Switch/":
        icx_plat = '7XB'
    elif im_type == "/SW/Router/" or im_type == "/SW/Switch/":
        icx_plat = 'SW'
    elif im_type == "/KX/Router/" or im_type == "/KX/Switch/":
        icx_plat = '6XM'
    elif im_type == "/FX/Router/" or im_type == "/FX/Switch/":
        icx_plat = 'FCX'
        print('Someone chose incorrectly.. fix later')
    else:
        print('Someone broke the app! :) ')
    # else:
    #     print('Override triggered', plat_o)
    #     icx_plat = plat_o

    d_result = gdb_expect.main(c_file, gdb_path, icx_plat)
    d_result.append('#######################')
    d_result.append('Decoder Information:')
    d_result.append('Using FastIron.debug in: ' + m_path)
    # d_result.append('This image was built on: ' + m_time)
    d_result.append('#######################')
    print("Result in python is ", d_result)
    # if not raw_stack:
    #     d_result.append('No matches found in Symbol File!')
    #     return d_result
    if is_j:
        j_result = 'Jira query not currently supported for GDB, Sorry!'
        # j_result = q_jira.jsearch(raw_stack)
        if not j_result:
            d_result.append('########################')
            d_result.append('No Jira match, this could be a new defect')
            d_result.append('########################')
        else:
            d_result.append('########################')
            d_result.append('Jira Matches:')
            # for j_element in j_result:
            #     print('j_element', j_element)
            #     d_result.append(j_element)
            d_result.append(j_result)
            d_result.append('########################')
            print("Jira result is: ", j_result)
    return d_result


if __name__ == "__main__":
    main()
