# jhbuild - a tool to ease building collections of source packages
# Copyright (C) 2012 Carl-Anton Ingmarsson <ca.ingmarsson@gmail.com>
#
#   envinfo.py: Retrieve information about the jhbuild environment.
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
from optparse import make_option

from jhbuild.commands import Command, register_command

class cmd_envinfo(Command):
    doc = N_('Retrieve information about the jhbuild environment')

    name = 'envinfo'
    usage_args = N_('[ options ... ]')

    def __init__(self):
        Command.__init__(self, [
            make_option('-e', '--env',
                        action='store_true', dest='print_environment', default=False,
                        help=_('get the environment variables used inside jhbuild')),
			make_option('-p', '--prefix',
                        action='store_true', dest='print_prefix', default=False,
                        help=_('get the jhbuild prefix')),
            make_option('-l', '--libdir',
                        action='store_true', dest='print_libdir', default=False,
                        help=_('get the jhbuild libdir')),
            ])

    def run(self, config, options, args, help=None):
        if options.print_environment:
            for k, v in os.environ.items():
                print "%s=%s" % (k, v)

        if options.print_prefix:
            print config.prefix

        if options.print_libdir:
            print config.libdir

register_command(cmd_envinfo)

