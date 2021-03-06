#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USAGE
# python -matx -s ESLKJXX gui

import argparse
import functools
import json
import sys
import inspect
from contextlib import contextmanager

import atx.androaxml as apkparse

from atx.cmds import run
from atx.cmds import iosdeveloper
from atx.cmds import install


def inject(func, kwargs):
    '''
    This is a black techonology of python. like golang martini inject

    Usage:
    allargs = dict(name='foo', message='body')
    def func(name):
        print 'hi', name

    inject(func, allargs)
    # will output
    # hi foo
    '''
    args = []
    for name in inspect.getargspec(func).args:
        args.append(kwargs.get(name))
    return func(*args)


def load_main(module_name):
    def _inner(parser_args):
        module_path = 'atx.cmds.'+module_name
        __import__(module_path)
        mod = sys.modules[module_path]
        pargs = vars(parser_args)
        return inject(mod.main, pargs)
    return _inner


def _apk_parse(args):
    (pkg_name, activity) = apkparse.parse_apk(args.filename)
    print json.dumps({
        'package_name': pkg_name,
        'main_activity': activity,
    }, indent=4)


def _version(args):
    import atx
    print atx.version


def main():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("-s", "--serial", "--udid", required=False, help="Android serial or iOS unid")
    ap.add_argument("-H", "--host", required=False, default='127.0.0.1', help="Adb host")
    ap.add_argument("-P", "--port", required=False, type=int, default=5037, help="Adb port")

    subp = ap.add_subparsers()

    @contextmanager
    def add_parser(name):
        yield subp.add_parser(name, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    with add_parser('tcpproxy') as p:
        p.add_argument('-l', '--listen', default=5555, type=int, help='Listen port')
        p.add_argument('-f', '--forward', default=26944, type=int, help='Forwarded port')
        p.set_defaults(func=load_main('tcpproxy'))

    with add_parser('gui') as p:
        p.set_defaults(func=load_main('tkgui'))

    with add_parser('record') as p:
        p.set_defaults(func=load_main('record'))

    with add_parser('minicap') as p:
        p.set_defaults(func=load_main('minicap'))

    with add_parser('apkparse') as p:
        p.add_argument('filename', help='Apk filename')
        p.set_defaults(func=_apk_parse)

    with add_parser('monkey') as p:
        p.set_defaults(func=load_main('monkey'))

    with add_parser('install') as p:
        p.add_argument('path', help='<apk file path | apk url path> (only support android for now)')
        p.add_argument('--start', action='store_true', help='Start app when app success installed')
        p.set_defaults(func=load_main('install'))

    with add_parser('screen') as p:
        p.add_argument('-s', '--scale', required=False, default=0.5, help='image scale')
        p.add_argument('--simple', action='store_true', help='disable interact controls')
        p.set_defaults(func=load_main('screen'))

    with add_parser('screencap') as p:
        p.add_argument('--scale', required=False, type=float, default=1.0, help='image scale')
        p.add_argument('-o', '--out', required=False, default='screenshot.png', help='output path')
        p.add_argument('-m', '--method', required=False, default='minicap', choices=('minicap', 'screencap'), help='screenshot method')
        p.set_defaults(func=load_main('screencap'))

    with add_parser('screenrecord') as p:
        p.add_argument('-o', '--output', default='out.avi', help='video output path')
        p.add_argument('--overwrite', action='store_true', help='overwrite video output file.')
        p.add_argument('--scale', type=float, default=0.5, help='image scale for video')
        p.add_argument('-q', '--quiet', dest='verbose', action='store_false', help='display screen while recording.')
        p.add_argument('--portrait', action='store_true', help='set video framesize to portrait instead of landscape.')
        p.set_defaults(func=load_main('screenrecord'))

    with add_parser('web') as p:
        p.add_argument('--no-browser', dest='open_browser', action='store_false', help='Not open browser')
        p.add_argument('--web-port', required=False, type=int, help='web listen port')
        p.set_defaults(func=load_main('webide'))

    with add_parser('run') as p:
        p.add_argument('-f', dest='config_file', default='atx.yml', help='config file')
        p.set_defaults(func=load_main('run'))

    with add_parser('version') as p:
        p.set_defaults(func=_version)

    args = ap.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
