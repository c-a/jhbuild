# jhbuild - a build script for GNOME 1.x and 2.x
# Copyright (C) 2001-2004  James Henstridge
#
#   svnmodule.py: rules for building SVN modules.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os

import base
from base import AutogenModule
from base import register_module_type
from jhbuild.utils import svn
from jhbuild.errors import FatalError

class SVNModule(AutogenModule):
    SVNRoot = svn.SVNRoot
    type = 'svn'

    def __init__(self, svnmodule, checkoutdir=None,
                 autogenargs='', makeargs='', dependencies=[], suggests=[],
                 svnroot=None, supports_non_srcdir_builds=True):
        AutogenModule.__init__(self,checkoutdir or os.path.basename(svnmodule),
                               autogenargs, makeargs,
                               dependencies, suggests,
                               supports_non_srcdir_builds)
        self.svnmodule   = svnmodule
        self.checkoutdir = checkoutdir
        self.svnroot     = svnroot

    def get_srcdir(self, buildscript):
        return os.path.join(buildscript.config.checkoutroot,
                        self.checkoutdir or os.path.basename(self.svnmodule))

    def get_builddir(self, buildscript):
        if buildscript.config.buildroot and \
               self.supports_non_srcdir_builds:
            d = buildscript.config.builddir_pattern \
                % (self.checkoutdir or os.path.basename(self.svnmodule))
            return os.path.join(buildscript.config.buildroot, d)
        else:
            return self.get_srcdir(buildscript)

    def get_revision(self):
        # The convention for Subversion repositories is to put the head
        # branch under trunk/, branches under branches/foo/ and tags
        # under tags/bar/.
        # Use this to give a meaningful revision number.
        path_parts = self.svnmodule.split('/')
        for i in range(len(path_parts) - 1):
            if path_parts[i] in ['branches', 'tags', 'releases']:
                return path_parts[i+1]
            elif path_parts[i] == 'trunk':
                break
        return None

    def do_checkout(self, buildscript):
        svnroot = self.SVNRoot(self.svnroot,
                               buildscript.config.checkoutroot)
        srcdir = self.get_srcdir(buildscript)
        builddir = self.get_builddir(buildscript)
        buildscript.set_action('Checking out', self)
        res = svnroot.update(buildscript, self.svnmodule,
                             buildscript.config.sticky_date,
                             checkoutdir=self.checkoutdir)

        if buildscript.config.nobuild:
            nextstate = self.STATE_DONE
        elif buildscript.config.alwaysautogen or \
                 not os.path.exists(os.path.join(builddir, 'Makefile')):
            nextstate = self.STATE_CONFIGURE
        elif buildscript.config.makeclean:
            nextstate = self.STATE_CLEAN
        else:
            nextstate = self.STATE_BUILD
        # did the checkout succeed?
        if res == 0 and os.path.exists(srcdir):
            return (nextstate, None, None)
        else:
            return (nextstate, 'could not update module',
                    [self.STATE_FORCE_CHECKOUT])

    def do_force_checkout(self, buildscript):
        svnroot = self.SVNRoot(self.svnroot,
                              buildscript.config.checkoutroot)
        srcdir = self.get_srcdir(buildscript)
        builddir = self.get_builddir(buildscript)
        if buildscript.config.nobuild:
            nextstate = self.STATE_DONE
        else:
            nextstate = self.STATE_CONFIGURE

        buildscript.set_action('Checking out', self)
        res = svnroot.checkout(buildscript, self.svnmodule,
                               buildscript.config.sticky_date,
                               checkoutdir=self.checkoutdir)
        if res == 0 and os.path.exists(srcdir):
            return (nextstate, None, None)
        else:
            return (nextstate, 'could not checkout module',
                    [self.STATE_FORCE_CHECKOUT])

def parse_svnmodule(node, config, dependencies, suggests, root,
                    SVNModule=SVNModule):
    if root[0] != 'svn':
        raise FatalError('%s is not a Subversion repository' % root[1])
    svnroot = root[1]
    id = node.getAttribute('id')
    module = id
    checkoutdir = None
    autogenargs = ''
    makeargs = ''
    supports_non_srcdir_builds = True
    if node.hasAttribute('module'):
        module = node.getAttribute('module')
    if node.hasAttribute('checkoutdir'):
        checkoutdir = node.getAttribute('checkoutdir')
    if node.hasAttribute('autogenargs'):
        autogenargs = node.getAttribute('autogenargs')
    if node.hasAttribute('makeargs'):
        makeargs = node.getAttribute('makeargs')
    if node.hasAttribute('supports-non-srcdir-builds'):
        supports_non_srcdir_builds = \
            (node.getAttribute('supports-non-srcdir-builds') != 'no')

    # override revision tag if requested.
    autogenargs = config.module_autogenargs.get(module, autogenargs)
    makeargs = config.module_makeargs.get(module, makeargs)

    return SVNModule(module, checkoutdir,
                     autogenargs, makeargs,
                     svnroot=svnroot,
                     dependencies=dependencies,
                     suggests=suggests,
                     supports_non_srcdir_builds=supports_non_srcdir_builds)
register_module_type('svnmodule', parse_svnmodule)
