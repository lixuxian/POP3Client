import base64
import getpass
import re
import socket
import sys

__author__ = 'Alexander.Chukharev'

port = 110
login = ''
password = ''


def print_help():
    path = sys.argv[0].split("/")
    name = path[len(path) - 1]
    print("{0} host port".format(name))


def get_args():
    global port, host, login, password
    if len(sys.argv) == 1:
        print_help()
        sys.exit(0)
    else:
        host = sys.argv[1]
        if len(sys.argv) == 3:
            port = int(sys.argv[2])
    login = input('LOGIN: ')
    password = getpass.getpass('PASS: ')


def send_m(m, s):
    print(m)
    s.send((m + '\r\n').encode('utf-8'))


def send_and_print(mes, s):
    send_m(mes, s)
    print(s.recv(2048).decode('utf-8'))


def get_subj(s):
    result = ''
    for ln in s:
        g = re.match('.*=\?([^\?]+)\?([^\?]+)\?([^\?]+)\?=', ln)
        encoding = g.group(1)
        text = g.group(3)
        text = base64.b64decode(text).decode(encoding)
        result += text
    return result


def get_result(m):
    subj = ''
    addr = ''
    lines_in_m = m.split('\n')
    for ln in lines_in_m:
        if ln.startswith('From:'):
            addr = ln
            break
    for i in range(0, len(lines_in_m)):
        if lines_in_m[i].startswith('Subject:'):
            j = i + 1
            while lines_in_m[i].startswith(' '):
                ++j
            subj = 'Subject: ' + get_subj(lines_in_m[i: j])
            break
    return [subj, addr]


def main():
    global host, port, auto
    get_args()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception as e:
        print('can\'t connect to {0} on {1} port \r\n{3}'.format(host, port, e.__repr__()))
    print(sock.recv(1024))
    auto = [
        'user {0}'.format(login),
        'pass {0}'.format(password),
    ]
    for m in auto:
        send_and_print(m, sock)
    send_m('list', sock)
    mail_list = ''
    m = sock.recv(2048)
    while not m.endswith(b'\r\n.\r\n'):
        m = m.decode('utf-8')
        mail_list += m
        m = sock.recv(2048)
    mail_list += m.decode('utf-8')
    messages = mail_list.split('\r\n')
    messages = messages[1: len(messages)]
    for m in messages:
        if m != '' and m != '.':
            number = m.split(' ')[0]
            send_m('top {0} 0'.format(number), sock)
            ans = sock.recv(2048)
            while not ans.endswith(b'\r\n.\r\n'):
                ans += sock.recv(2048)
            subj, addr = get_result(ans.decode('cp852'))
            print('{0}\n{1}'.format(addr, subj))


main()
