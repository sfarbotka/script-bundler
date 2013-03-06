#!/usr/bin/env python

import os
import shutil
from argparse import ArgumentParser
import plistlib


class InfoBuilder(object):
    def __init__(self, bundle_name):
        self.bundle_name = bundle_name
        self.executable = self.bundle_name
        self.display_name = None
        self.icon = None

    def build(self):
        ret = {}

        ret['CFBundleExecutable'] = self.executable
        ret['CFBundleName'] = self.bundle_name
        if self.display_name is not None:
            ret['CFBundleDisplayName'] = self.display_name
        if self.icon is not None:
            ret['CFBundleIconFile'] = self.icon

        return ret


class ScriptBundler(object):
    def __init__(self, script_path, bundle_name, display_name, icon):
        self.script_path = script_path
        self.script_name = get_fname(script_path)
        self.bundle_name = bundle_name
        self.display_name = display_name
        self.icon = icon
        self.icon_name = self._icon_name()

    def check(self, app_path):
        if os.path.exists(app_path):
            raise IOError('%s already exists' % app_path)

        if not os.path.exists(self.script_path):
            raise IOError('File %s does not exist' % self.script_path)

        if not os.path.isfile(self.script_path):
            raise IOError('%s is directory, not file' % self.script_path)

    def _build_info(self):
        ibuilder = InfoBuilder(self.bundle_name)
        ibuilder.display_name = self.display_name
        ibuilder.executable = self.script_name
        if self.icon_name is not None:
            ibuilder.icon = self.icon_name

        info = ibuilder.build()

        return info

    def _icon_name(self):
        if self.icon is None:
            return None

        ext = get_fext(self.icon)
        name = 'icon%s' % ext

        return name

    def bundle(self, app_path):
        self.check(app_path)

        contents = os.path.join(app_path, 'Contents', )
        macos = os.path.join(contents, 'MacOS')
        resources = os.path.join(contents, 'Resources')
        info_plist = os.path.join(contents, 'Info.plist')

        exe_path = os.path.join(macos, self.script_name)

        info = self._build_info()

        print 'Creating app directories...'
        os.makedirs(macos)
        os.mkdir(resources)
        print 'Copying executable...'
        shutil.copyfile(self.script_path, exe_path)
        print 'Setting executable attributes...'
        os.lchmod(exe_path, 0755)

        if self.icon is not None:
            print 'Copying icon...'
            icon_dst = os.path.join(resources, self.icon_name)
            shutil.copy(self.icon, icon_dst)

        print 'Creating Info.plist...'
        plistlib.writePlist(info, info_plist)


def get_fdir(path):
    return os.path.split(path)[0]


def get_fname(path):
    return os.path.split(path)[1]


def get_fbase(fname):
    return os.path.splitext(fname)[0]


def get_fext(fname):
    return os.path.splitext(fname)[1]


def get_abspath(path):
    return os.path.expanduser(os.path.abspath(path))


def get_bundle_name(bundle_name, script_path):
    if bundle_name is not None:
        if get_fdir(bundle_name):
            raise Exception('Bundle name must not contain path')
        if get_fext(bundle_name) == '.app':
            return get_fbase(bundle_name)
        return bundle_name

    script_name = get_fname(script_path)
    return get_fbase(script_name)


def get_display_name(display_name, bundle_name):
    if display_name is not None:
        return display_name

    return bundle_name


def get_destdir(destdir, script_path):
    if destdir is not None:
        return get_abspath(destdir)

    return get_fdir(script_path)


def get_app_path(destdir, bundle_name):
    app = '%s.app' % bundle_name
    return os.path.join(destdir, app)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-d', '--display-name', help='App display name')
    parser.add_argument('-b', '--bundle-name', help='App bundle name')
    parser.add_argument('-i', '--icns', help='App icon')
    parser.add_argument('-o', '--dest-dir', help='Destination directory for bundle', dest='destdir')
    parser.add_argument('script', help='Script to be used as app executable')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    script_path = get_abspath(args.script)
    bundle_name = get_bundle_name(args.bundle_name, script_path)
    display_name = get_display_name(args.display_name, bundle_name)
    destdir = get_destdir(args.destdir, script_path)
    app_path = get_app_path(destdir, bundle_name)
    icon = args.icns

    bundler = ScriptBundler(script_path, bundle_name, display_name, icon)
    bundler.bundle(app_path)

    print 'Done: %s' % app_path


if __name__ == '__main__':
    main()
