#! /usr/bin/env python
# Modified by Lauren Miller from unknown author

import pexpect
import time
from local_defs import mydefs
import re


# The login creds
user = 'lauren'
password= 'F0undry15'
host = '10.0.1.180'

def ssh_command (user, host, password, command):

    """This runs a command on the remote host."""
    print("Ssh connection attempted to", host)

    ssh_newkey = 'Are you sure you want to continue connecting'
    child = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    if i == 0: # Timeout
        print('ERROR!')
        print('SSH could not login. Here is what SSH said:')
        print(child.before, child.after)
        return None
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        child.expect ('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            print('9ERROR!')
            print('SSH could not login. Here is what SSH said:')
            print(child.before, child.after)
            return None
    child.sendline(password)
    return child

def main(c_file, m_path, icx_plat):
    md = mydefs()
    new_result = []
    print('ICX plat is', icx_plat)
    my_str = '#'
    if icx_plat == "7XB":
        my_gdbclient = 'ARMv7BE'
    elif icx_plat == "SW":
        my_gdbclient = 'PPC'
    elif icx_plat == "6XM":
        my_gdbclient = 'ARMv5'
    else:
        # Well this is as good a default as any..
        my_gdbclient = 'ARMv7LE'
    full_gdbpath = mydefs.GDBROOT + my_gdbclient + '/gdbclient'
    print('gdbpath', full_gdbpath)
    print('mpath', m_path)
    print('crashfile', c_file)
    my_cmd = full_gdbpath + ' ' + m_path + ' -c ' + c_file
    # my_cmd = './sarma/ARMv7LE/gdbclient ' + 'FastIron_SPR08030q.debug -c doc/dev/python/decoder/ss_core'
    child = ssh_command (user, host, password, my_cmd)
    child.expect('\(gdb\)')
    time.sleep(5)
    child.sendline('bt')

    time.sleep(5)
    # output = child.before.decode()
    # noutput = child.after.decode()
    #
    # print('l1')
    # print(output)
    # print(noutput)
    child.expect('\(gdb\)')
    # output = child.before.decode()
    # noutput = child.after.decode()
    # print('l2')
    # print(output)
    # print(noutput)
    child.sendline('quit')
    # result = child.before.decode()[3:]
    result = child.before.decode()
    # noutput = child.after.decode()
    # print('l3')
    print('Expect result is:', result)
    # print(noutput)
    child.expect('$')
    # output = child.before.decode()
    # noutput = child.after.decode()
    # print('4')
    # print(output)
    # print(noutput)
    child.sendline('exit')
    child.close()
    for line in result:
        print('line is', line)
        if line == '#':
            print('my_Str', my_str)
            new_result.append(my_str)
            my_str = '#'
        else:
            my_str = my_str + line
            print('my_Str', my_str)
    print('new result is', new_result)
    return new_result

if __name__ == "__main__":
    main()
