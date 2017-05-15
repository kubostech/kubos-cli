# Copyright 2014-2015 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

# NOTE: argcomplete must be first!
import argcomplete

# standard library modules, , ,
import argparse
import importlib
import logging
import functools
import sdk_config
import sys
import os

from . import options as kubos_options


def splitList(l, at_value):
    r = [[]]
    for x in l:
        if x == at_value:
            r.append(list())
        else:
            r[-1].append(x)
    return r

def setup_yotta(): # override and setup certain yotta functions.
    from . import override
    for module_name in override.file_list:
        module = importlib.import_module('.' + module_name, 'kubos.override')
        module.exec_override()

def main():
    setup_yotta()

    # Everything from yotta.lib needs to be imported after setup_yotta() has been called.
    # Otherwise, default yotta behavior will be imported rather than the overridden kubos
    # behavior that was "injected" into yotta.
    from yotta.lib import lazyregex, errors
    # globalconf, share global arguments between modules, internal
    import yotta.lib.globalconf as globalconf
    import yotta.options as options
    import kubos.options as kubos_options
    # logging setup, , setup the logging system, internal
    from yotta.lib import logging_setup

    logging_setup.init(level=logging.INFO, enable_subsystems=None, plain=False)

    # we override many argparse things to make options more re-usable across
    # subcommands, and allow lazy loading of subcommand modules:
    parser = kubos_options.parser.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Kubos-CLI For working with Kubos Projects.\n'+
        'For more detailed help on each subcommand, run: kubos <subcommand> --help'
    )
    subparser = parser.add_subparsers(dest='subcommand_name', metavar='<subcommand>')

    # add re-usable top-level options which subcommands may also accept
    options.verbosity.addTo(parser)
    options.debug.addTo(parser)
    options.plain.addTo(parser)
    options.noninteractive.addTo(parser)
    options.registry.addTo(parser)
    options.target.addTo(parser)
    options.config.addTo(parser)


    local_config = sdk_config.load_config()
    add_kubos_command = functools.partial(kubos_options.command.add_command, local_config, subparser, 'kubos') #add our own implemented commands
    add_yotta_command = functools.partial(kubos_options.command.add_command, local_config, subparser, 'yotta') #add from the default yotta commands
    add_kubos_command_sync = functools.partial(kubos_options.command.add_command_sync, local_config, subparser, 'kubos') #add our own implemented commands
    add_kubos_command_sync('target', 'target', 'Set or display the current target.')
    add_kubos_command('init', 'init', 'Create a new module.')
    add_yotta_command('build', 'build',
        'Build the current module. Options can be passed to the underlying '+
        'build tool by passing them after --, e.g. to do a verbose build '+
        'which will display each command as it is run, use:\n'+
        '  yotta build -- -v\n\n'+
        'The programs or libraries to build can be specified (by default '+
        'only the libraries needed by the current module and the current '+
        "module's own tests are built). For example, to build the tests of "+
        'all dependencies, run:\n  yotta build all_tests\n\n',
        'Build the current module.'
    )
    add_kubos_command('link', 'link',
        'Symlink a module to be used into another module.\n\n'+
        'Use: "yotta link" in a module to link it globally, then use "yotta '+
        'link <modulename>" to link it into the module where you want to use '+
        'it.\n\n'+
        '"yotta link ../path/to/module" is also supported, which will create '+
        'the global link and a link into the current module in a single step.',
        'Symlink a module'
    )
    add_yotta_command('link-target', 'link_target',
        'Symlink a target to be used into another module.\n\n'+
        'Use: "yotta link" in a target to link it globally, then use "yotta '+
        'link-target <targetname>" to link it into the module where you want to use '+
        'it.\n\n'+
        '"yotta link ../path/to/target" is also supported, which will create '+
        'the global link and a link into the current module in a single step.',
        'Symlink a target'
    )
    add_kubos_command('update', 'update', 'Download newer versions of the KubOS Modules')
    add_yotta_command('debug', 'debug', 'Attach a debugger to the current target.  Requires target support.')
    add_yotta_command('test', 'test_subcommand',
        'Run the tests for the current module on the current target. A build '+
        'will be run first, and options to the build subcommand are also '+
        'accepted by test.\nThis subcommand requires the target to provide a '+
        '"test" script that will be used to run each test. Modules may also '+
        'define a "testReporter" script, which will be piped the output from '+
        'each test, and may produce a summary.',
        'Run the tests for the current module on the current target. Requires target support for cross-compiling targets.'
    )
    add_yotta_command('start', 'start',
        'Launch the compiled program (available for executable modules only). Requires target support for cross-compiling targets.'
    )
    add_yotta_command('list', 'list', 'List the dependencies of the current module, or the inherited targets of the current target.')
    add_yotta_command('outdated', 'outdated', 'Display information about dependencies which have newer versions available.')
    add_yotta_command('remove', 'remove',
        'Remove the downloaded version of a dependency module or target, or '+
        'un-link a linked module or target (see yotta link --help for details '+
        'of linking). This command does not modify your module.json file.',
        'Remove or unlink a dependency without removing it from module.json.'
    )
    add_yotta_command('licenses', 'licenses', 'List the licenses of the current module and its dependencies.')
    add_yotta_command('clean', 'clean', 'Remove files created by yotta and the build.')
    add_yotta_command('config', 'config', 'Display the target configuration info.')
    add_yotta_command('shrinkwrap', 'shrinkwrap', 'Create a yotta-shrinkwrap.json file to freeze dependency versions.')
    add_kubos_command('version', 'version', 'Display the current active version of the cli and KubOS source repo.')
    add_kubos_command('use', 'use', 'Set a new version of the KubOS modules to build your projects against.')
    add_kubos_command('versions', 'versions', 'Display the available versions of the KubOS source.')

    # short synonyms, subparser.choices is a dictionary, so use update() to
    # merge in the keys from another dictionary
    short_commands = {
                'up':subparser.choices['update'],
                'ln':subparser.choices['link'],
                 'v':subparser.choices['version'],
                'ls':subparser.choices['list'],
                'rm':subparser.choices['remove'],
            'unlink':subparser.choices['remove'],
     'unlink-target':subparser.choices['remove'],
              'lics':subparser.choices['licenses'],
               'run':subparser.choices['start'],
             'flash':subparser.choices['start']
    }
    subparser.choices.update(short_commands)

    # split the args into those before and after any '--'
    # argument - subcommands get raw access to arguments following '--', and
    # may pass them on to (for example) the build tool being used
    split_args = splitList(sys.argv, '--')
    following_args = functools.reduce(lambda x,y: x + ['--'] + y, split_args[1:], [])[1:]

    # complete all the things :)
    argcomplete.autocomplete(
         parser,
        exclude = list(short_commands.keys()) + ['-d', '--debug', '-v', '--verbose']
    )

    # when args are passed directly we need to strip off the program name
    # (hence [:1])
    args = parser.parse_args(split_args[0][1:])

    # set global arguments that are shared everywhere and never change
    globalconf.set('interactive', args.interactive)
    globalconf.set('plain', args.plain)

    # finally, do stuff!
    if 'command' not in args:
        parser.print_usage()
        sys.exit(0)

    try:
        status = args.command(args, following_args)
    except KeyboardInterrupt:
        logging.warning('interrupted')
        status = -1

    return status or 0
