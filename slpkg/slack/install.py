#!/usr/bin/python
# -*- coding: utf-8 -*-

# install.py

# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Utility for easy management packages in Slackware

# https://github.com/dslackw/slpkg

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import getpass
import subprocess

from colors import colors
from url_read import url_read
from messages import pkg_not_found, s_user
from __metadata__ import slpkg_tmp, pkg_path

from pkg.find import find_package
from pkg.manager import pkg_upgrade, pkg_reinstall

from mirrors import mirrors

def install(slack_pkg):
    '''
    Install packages from official Slackware distribution
    '''
    try:
        s_user(getpass.getuser())
        dwn_list, dwn_packages = [], []
        install_all, package_name, package_location = [], [], []
        pkg_path = slpkg_tmp + "packages/"
        if not os.path.exists(pkg_path):
            if not os.path.exists(slpkg_tmp):
                os.mkdir(slpkg_tmp)
                os.mkdir(pkg_path)
        print("\nPackages with name matching [ {0}{1}{2} ]\n".format(
                colors.CYAN, slack_pkg, colors.ENDC)) 
        sys.stdout.write ("Reading package lists ...")
        sys.stdout.flush()
        PACKAGE_TXT = url_read(mirrors(name="PACKAGES.TXT", location=""))
        index, toolbar_width = 0, 600
        for line in PACKAGE_TXT.splitlines():
            index += 1
            if index == toolbar_width:
                sys.stdout.write(".")
                sys.stdout.flush()
                toolbar_width += 600
                time.sleep(0.05)
            if line.startswith("PACKAGE NAME"):
                package_name.append(line.replace("PACKAGE NAME:  ", ""))
            if line.startswith('PACKAGE LOCATION'):
                package_location.append(line.replace("PACKAGE LOCATION:  ./", ""))
        for loc, name in zip(package_location, package_name):
            dwn_list.append("{0}{1}/{2}".format(mirrors("",""), loc, name))
        sys.stdout.write("Done\n\n")
        for pkg in package_name:
            if slack_pkg in pkg:
                if pkg.endswith(".txz"):
                    print("{0}[ install ] --> {1}{2}".format(
                            colors.GREEN, colors.ENDC, pkg.replace(".txz", "")))
                    install_all.append(pkg)
                elif pkg.endswith(".tgz"):
                    print("{0}[ install ] --> {1}{2}".format(
                            colors.GREEN, colors.ENDC, pkg.replace(".tgz", "")))
                    install_all.append(pkg)
        if install_all == []:
            bol, eol = "", "\n"
            message = "No matching"
            pkg_not_found(bol, slack_pkg, message, eol)
        else:
            read = raw_input("\nWould you like to install [Y/n]? ")
            if read == "Y" or read == "y":
                for install in install_all:
                    for dwn in dwn_list:
                        if install in dwn:
                            subprocess.call("wget -N --directory-prefix={0} {1}".format(
                                       pkg_path, dwn), shell=True)
                for install in install_all:
                    if not os.path.isfile(pkg_path + install):
                        print("{0}[ installing ] --> {1}{2}".format(
                                colors.GREEN, colors.ENDC, install))
                        pkg_upgrade((pkg_path + install).split())
                    else:
                        print("{0}[ reinstalling ] --> {1}{2}".format(
                                colors.GREEN, colors.ENDC, install))
                        pkg_reinstall((pkg_path + install).split())

                read = raw_input("Removal downloaded packages [Y/n]? ")
                if read == "Y" or read == "y":
                    for remove in install_all:
                        os.remove(pkg_path + remove)
                    if os.listdir(pkg_path) == []:
                        print("Packages removed")
                    else:
                        print("\nThere are packages in directory {0}\n".format(
                                pkg_path))
                else:
                    print("\nThere are packages in directory {0}{1}\n".format(
                            pkg_path))
    except KeyboardInterrupt:
        print # new line at exit
        sys.exit()