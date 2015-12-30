"""The SRP Command Line Interface.
"""

import argparse
import sys

from pprint import pprint # FIXME: this was for debug...?

import srp


desc = """\
{}, version {}
(C) 2001-{} Michael D Labriola <michael.d.labriola@gmail.com>
""".format(srp.config.prog, srp.config.version, srp.config.build_year)

epi = """\
example: srp -v --build foo.notes,src=/path/to/src,copysrc=True

example: srp --build foo.notes,-src=foo.tar.xz,extradir=/path/to/extra/files

example: srp -i --options=strip_debug,strip_docs,strip_man foo.i686.brp

example: srp --query=info,size,pkg=foo

example: srp -i foo.brp bar.brp baz.brp

example: srp -l "perl*" | srp --action=strip_debug,strip_docs,commit
"""


p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                            prog='srp',
                            description=desc.rstrip(),
                            epilog=epi.rstrip()
                            )

# one and only one of the following options is required
g = p.add_argument_group("MODE", "Operational Mode of Doom")

# FIXME: add some way to list a description of BuildParameters

# FIXME: --help-build, --help-install, --help-query, etc

# FIXME: maybe derive my own argparse.Action to keep track of command line
#        ordering (i.e., --build foo --install foo --build bar must BUILD,
#        INSTALL, and then BUILD again).

g.add_argument('-b', '--build', metavar="NOTES[,key=val,...]",
               action="append",
               help="""Build package specified by the supplied NOTES file (and
               optional keyword arguments).  Valid keyword args for build are in
               srp.core.BuildParameters.  Resulting binary package will be
               written to PWD.""")

g.add_argument('-i', '--install', metavar="PKG[,key=val,...]",
               action="append",
               help="""Install package specified by the supplied PKG file (and
               optional keyword arguments).  Valid keyword args for install are
               in srp.core.InstallParameters.  If a different version of
               PACKAGE is already installed, it will be upgraded unless
               upgrade=False is set.  Note that upgrade and downgrade are
               not differentiated (i.e., you can upgrade from version 3 to
               version 2 of a package even though you'd probably think of
               that as a downgrade (unless version 3 is broken, of
               course)).""")

g.add_argument('-B', '--build-and-install', metavar="NOTES[,key=val,...]",
               action="append",
               help="""Build and install the package specified by the supplied
               NOTES file (and
               optional keyword arguments).  Valid keyword wargs are defined in
               srp.core.BuildParameters and srp.core.InstallParameters.
               If the package already exists in PWD and is newer than the
               NOTES file, the previously built package is installed w/out
               triggering a re-build.""")

g.add_argument('-u', '--uninstall', metavar="PKG[,key=val,...]",
               action="append",
               help="""Uninstall the provided PACKAGE(s).  If PACKAGE isn't
                    installed, this will quietly return successfully (well,
                    it DID get uninstalled at some point).""")

# FIXME: some way to display all registered query types and criteria?
#
g.add_argument('-q', '--query', metavar="QUERY",
               help="""Perform a QUERY.  Format of QUERY is
               type[,type,..],criteria[,criteria,...].  For example,
               info,files,pkg=foo would display info and list of files for
               all packages named "foo".""")

g.add_argument('-a', '--action', metavar="ACTIONS",
               help="""Perform some sort of action on an installed PACKAGE.
                    ACTIONS is a comma-delimited list of actions to be
                    performed (e.g.,
                    --action=strip_debug,strip_docs,commit).""")

# FIXME: need to document supported actions somewhere.  here's a list of the
#        planned ones for now:
#
#        strip_debug - run strip --strip-unneeded on all installed files
#
#        strip_doc - remove installed files in PREFIX/share/doc
#
#        strip_man - remove installed manpages (PREFIX/share/man/)
#
#        strip_info - remove installed info pages (PREFIX/share/info/)
#
#        strip_locale - remove all internationalization translation files
#        (PREFIX/share/locale)
#
#        strip_all - alias to list of all supported strip_* actions
#
#        repair - revert any modified files back to their installed state
#
#        add_file=file - add the specified file to the package's file list
#
#        rm_file=file - remove the specified file from the package's file
#        list
#
#        add_dep_prog=file
#        rm_dep_prog=file
#
#        update_dep_libs - recalculate package library deps by scanning the
#        (potentially updated) list of installed files.
#
#        commit - re-checksum and record package changes

g.add_argument('-l', '--list', metavar="PATTERN", nargs='?', const='*',
               help="""List installed packages matching Unix shell-style
                    wildcard PATTERN (or all packages if PATTERN not
                    supplied).""")

# FIXME: this isn't needed, is it?
#
#g.add_argument('-I', '--init', action='store_true',
#               help="Initialize metadata.")

p.add_argument('-V', '--version', action='version',
               version="{} version {}".format(
                   srp.config.prog, srp.config.version))

# the following options are independent of the exclusive group (at least as
# far as the ArgumentParser is concerned).
p.add_argument('-v', '--verbose', action='count', default=0,
               help="""Be verbose.  Can be supplied multiple times for
                    increased levels of verbosity.""")

# FIXME: this doesn't force no_deps yet...  only same-version-upgrade...
#
# FIXME: i think this is getting replaced w/ specifie kwargs for whatever
#        we would be forcing... wouldn't want to accidentally force the
#        wrong thing, now would we?
#
#p.add_argument('-F', '--force', action='store_true',
#               help="""Do things anyway.  For example, this will allow you
#                    to 'upgrade' to the same version of what's installed.
#                    It can also be used to force installation even if
#                    dependencies are not met.""")

p.add_argument('-n', '--dry-run', action='store_true',
               help="""Don't actualy do anything, just print what would have
               been done.  Go
               through the motions, but Feature stage funcs are not
               executed.""")

p.add_argument('--root', metavar='ROOTDIR',
               help="""Specifies that we should operate on a filesystem rooted
               at ROOTDIR.
               This is similar to automake's DESTDIR variable, or srp2's
               SRP_ROOT_PREFIX variable""")

# FIXME: this might be going away now, too...
#
#p.add_argument('packages', metavar='PACKAGE', nargs='*',
#               help="""Specifies the PACKAGE(s) for --install, --uninstall,
#               --query, and --action.  Note that PACKAGE can be a Unix
#               shell-style wildcard for modes that act on previously
#               installed packages (e.g., --uninstall, --query, --action).
#               If a specified PACKAGE is '-', additional PACKAGEs are read
#               from stdin.""")

# FIXME: rename this to --show-features if we change --options as
#        mentioned...
#
p.add_argument('--features', action='store_true',
               help="""Display a summary of all registered features and exit""")


# FIXME: i think this is going to end up as a list of features to
#        enable/disable at run-time... and if so, it should get renamed to
#        --features... and the old --features flag should end up as
#        --show-features or something like that...
#
p.add_argument('--options', metavar='OPTIONS', default=[],
               help="""Comma delimited list of extra options to pass into
               --build, --install, or --uninstall.""")


# once we parse our command line arguments, we'll store the results globally
# here
#
args = None


# FIXME: this might be dead code... but we might want to be able to read
#        ARGS from stdin?  maybe?
#
#def parse_package_list():
#    # nothing to do unless - was specified
#    if '-' not in args.packages:
#        return
#
#    # append stdin to supplied package list, after removing the '-'
#    args.packages.remove('-')
#    args.packages.extend(sys.stdin.read().split())
#

def parse_options():
    # nothing to do unless we actually got options
    #
    # FIXME: do i need to compare exlictly against [] here to diferentiate
    #        between [] and None?
    if not args.options:
        return

    # parse --options into a list
    args.options = args.options.split(',')


def main():
    global args
    args = p.parse_args()

    print(args)

    #parse_package_list()
    parse_options()

    # set global params
    srp.params.verbosity = args.verbose
    srp.params.dry_run = args.dry_run
    if args.root:
        srp.params.root = args.root
    srp.params.options = args.options

    # mutually-exclusive arguments/flags
    if args.build:
        for arg in args.build:
            arg = arg.split(',')
            kwargs = {"notes": arg[0]}
            for x in arg[1:]:
                k,v = x.split('=')
                kwargs[k] = v
            srp.params.build = srp.BuildParameters(**kwargs)
            print(srp.params)
            srp.build()

    elif args.install:
        for arg in args.install:
            arg = arg.split(',')
            kwargs = {"pkg": arg[0]}
            for x in arg[1:]:
                k,v = x.split('=')
                kwargs[k] = v
            srp.params.install = srp.InstallParameters(**kwargs)
            print(srp.params)
            srp.install()

    elif args.uninstall:
        for arg in args.uninstall:
            arg = arg.split(',')
            kwargs = {"pkg": arg[0]}
            for x in arg[1:]:
                k,v = x.split('=')
                kwargs[k] = v
            srp.params.uninstall = srp.UninstallParameters(**kwargs)
            print(srp.params)
            srp.uninstall()

    elif args.action:
        if not args.packages:
            p.error("argument --action: requires PACKAGE(s)")

        for x in args.packages:
            print("do_action(package={}, actions={})".format(x, args.action))
            if not args.dry_run:
                do_action(x, args.action)

    elif args.query:
        q_t = []
        q_c = {}
        for x in args.query.split(','):
            if '=' in x:
                x = x.split('=')
                q_c[x[0]] = x[1]
            else:
                q_t.append(x)
        srp.params.query = srp.QueryParameters(q_t, q_c)
        print(srp.params)
        srp.query()

    # NOTE: --list=FOO is just shorthand for --query name,pkg=FOO
    #
    elif args.list != None:
        if not args.list:
            args.list = "*"
        srp.params.query = srp.QueryParameters(["name"],
                                               {"pkg": args.list})
        print(srp.params)
        srp.query()

    #elif args.init:
    #    print("do_init_metadata()")
    #    if not args.dry_run:
    #        pass

    elif args.features:
        m = srp.features.get_stage_map(srp.features.registered_features)
        pprint(m)
