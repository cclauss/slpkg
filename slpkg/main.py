#!/usr/bin/python
# -*- coding: utf-8 -*-

# main.py file is part of slpkg.

# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import getpass

from messages import Msg
from desc import PkgDesc
from config import Config
from queue import QueuePkgs
from repoinfo import RepoInfo
from repolist import RepoList
from repositories import Repo
from tracking import track_dep
from blacklist import BlackList
from version import prog_version
from arguments import options, usage
from slpkg_update import it_self_update
from init import (
    Update,
    Initialization,
    check_exists_repositories
)
from __metadata__ import MetaData as _m

from pkg.build import BuildPackage
from pkg.manager import PackageManager

from sbo.check import sbo_upgrade
from sbo.views import SBoNetwork
from sbo.slackbuild import SBoInstall

from slack.patches import Patches
from binary.check import pkg_upgrade
from binary.install import BinaryInstall


class Case(object):

    def __init__(self, package):
        self.package = package
        self.release = _m.slack_rel

    def sbo_install(self):
        SBoInstall(self.package).start(False)

    def binary_install(self, repo):
        BinaryInstall(self.package, repo, self.release).start(False)

    def sbo_upgrade(self):
        SBoInstall(sbo_upgrade()).start(True)

    def slack_upgrade(self):
        Patches(self.release).start()

    def binary_upgrade(self, repo):
        BinaryInstall(pkg_upgrade(repo), repo, self.release).start(True)


def main():

    Msg().s_user(getpass.getuser())
    args = sys.argv
    args.pop(0)
    blacklist = BlackList()
    queue = QueuePkgs()

    # all_args = [
    #     'update', 're-create', 'repo-add', 'repo-remove',
    #     'repo-list', 'repo-info',
    #     '-h', '--help', '-v', '-a', '-b',
    #     '-q', '-g', '-l', '-c', '-s', '-t', '-p', '-f',
    #     '-n', '-i', '-u', '-o', '-r', '-d'
    # ]

    without_repos = [
        '-h', '--help', '-v', '-a', '-b',
        '-q', '-g', '-f', '-n', '-i', '-u',
        '-o', '-r', '-d'
    ]

    if len(args) == 1 and args[0] == 'update':
        Update().repository()

    if len(args) == 2 and args[0] == 'update' and args[1] == 'slpkg':
        it_self_update()

    if len(args) == 1 and args[0] == 'repo-list':
        RepoList().repos()

    if len(args) == 0:
        usage('')
    elif (len(args) == 1 and args[0] == '-h' or
            args[0] == '--help' and args[1:] == []):
        options()

    if (len(args) == 1 and args[0] == '-v' or
            args[0] == '--version' and args[1:] == []):
        prog_version()

    if len(args) == 3 and args[0] == 'repo-add':
        Repo().add(args[1], args[2])

    if len(args) == 2 and args[0] == 'repo-remove':
        Repo().remove(args[1])

    # checking if repositories exists
    check_exists_repositories()

    if len(args) == 1 and args[0] == 're-create':
        Initialization().re_create()

    if (len(args) == 2 and args[0] == 'repo-info' and
            args[1] in RepoList().all_repos):
        del RepoList().all_repos
        RepoInfo().view(args[1])
    elif (len(args) == 2 and args[0] == 'repo-info' and
          args[1] not in RepoList().all_repos):
        usage(args[1])

    if len(args) == 3 and args[0] == '-a':
        BuildPackage(args[1], args[2:], _m.path).build()
    elif (len(args) == 3 and args[0] == '-l' and args[2] == '--index' and
            args[1] in _m.repositories):
        PackageManager(None).list(args[1], True)
    elif len(args) == 2 and args[0] == '-l' and args[1] in _m.repositories:
        PackageManager(None).list(args[1], False)
    elif len(args) == 3 and args[0] == '-c' and args[2] == '--upgrade':
        if args[1] in _m.repositories and args[1] not in ['slack', 'sbo']:
            Case('').binary_upgrade(args[1])
        elif args[1] in ['slack', 'sbo']:
            upgrade = {
                'sbo': Case('').sbo_upgrade,
                'slack': Case('').slack_upgrade
            }
            upgrade[args[1]]()
        else:
            usage(args[1])
    elif len(args) >= 3 and args[0] == '-s':
        if args[1] in _m.repositories and args[1] not in ['sbo']:
            Case(args[2:]).binary_install(args[1])
        elif args[1] == 'sbo':
            Case(args[2:]).sbo_install()
        else:
            usage(args[1])
    elif (len(args) == 3 and args[0] == '-t' and args[1] in _m.repositories):
        track_dep(args[2], args[1])
    elif len(args) == 2 and args[0] == '-n' and 'sbo' in _m.repositories:
        SBoNetwork(args[1]).view()
    elif len(args) == 2 and args[0] == '-b' and args[1] == '--list':
        blacklist.listed()
    elif len(args) > 2 and args[0] == '-b' and args[-1] == '--add':
        blacklist.add(args[1:-1])
    elif len(args) > 2 and args[0] == '-b' and args[-1] == '--remove':
        blacklist.remove(args[1:-1])
    elif len(args) == 2 and args[0] == '-q' and args[1] == '--list':
        queue.listed()
    elif len(args) > 2 and args[0] == '-q' and args[-1] == '--add':
        queue.add(args[1:-1])
    elif len(args) > 2 and args[0] == '-q' and args[-1] == '--remove':
        queue.remove(args[1:-1])
    elif len(args) == 2 and args[0] == '-q' and args[1] == '--build':
        queue.build()
    elif len(args) == 2 and args[0] == '-q' and args[1] == '--install':
        queue.install()
    elif len(args) == 2 and args[0] == '-q' and args[1] == '--build-install':
        queue.build()
        queue.install()
    elif len(args) > 1 and args[0] == '-i':
        PackageManager(args[1:]).install()
    elif len(args) > 1 and args[0] == '-u':
        PackageManager(args[1:]).upgrade()
    elif len(args) > 1 and args[0] == '-o':
        PackageManager(args[1:]).reinstall()
    elif len(args) > 1 and args[0] == '-r':
        PackageManager(args[1:]).remove()
    elif len(args) > 1 and args[0] == '-f':
        PackageManager(args[1:]).find()
    elif len(args) == 3 and args[0] == '-p' and args[1] in _m.repositories:
        PkgDesc(args[2], args[1], '').view()
    elif len(args) == 4 and args[0] == '-p' and args[3].startswith('--color='):
        colors = ['red', 'green', 'yellow', 'cyan', 'grey']
        tag = args[3][len('--color='):]
        if args[1] in _m.repositories and tag in colors:
            PkgDesc(args[2], args[1], tag).view()
        else:
            usage(args[1])
    elif len(args) > 1 and args[0] == '-d':
        PackageManager(args[1:]).display()
    elif len(args) == 2 and args[0] == '-g' and args[1].startswith('--config'):
        editor = args[1][len('--config='):]
        if args[1] == '--config':
            Config().view()
        elif editor:
            Config().edit(editor)
        else:
            usage('')
    else:
        if len(args) > 1 and args[0] not in without_repos:
            usage(args[1])
        else:
            usage('')

if __name__ == '__main__':
    main()
