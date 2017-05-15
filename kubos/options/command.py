import argparse
import importlib

class SDKCommand(object):
    def __init__(self, config, base_module, name, module_name, description, help=None):
        self.config = config
        self.base_module = base_module #yotta or kubos - This is the base module we are importing the command from
        self.name = name
        self.module_name = module_name
        self.description = description
        self.help = help or description
        self.track = None

    def addToSubparser(self, subparser):
        subparser.add_parser_async(
            self.name, description=self.description, help=self.help,
            formatter_class=argparse.RawTextHelpFormatter,
            callback=self.onParserAdded)

    def addToSubparserSync(self, subparser):
        subparser.add_parser_sync(
            self.name, description=self.description, help=self.help,
            formatter_class=argparse.RawTextHelpFormatter,
            add_options=self.onParserAdded)


    def execCommand(self, args, following_args):
        return self.module.execCommand(args, following_args)

    def onParserAdded(self, parser):
        self.module = importlib.import_module('.' + self.module_name, self.base_module)
        self.module.addOptions(parser)
        parser.set_defaults(command=self.execCommand)


def add_command(config, subparser, *args, **kwargs):
    m = _command_class(config, *args, **kwargs)
    m.addToSubparser(subparser)

def add_command_sync(config, subparser, *args, **kwargs):
    '''
    For argcomplete to work correctly with the target names we have to synchronously
    load the target command and its options.
    '''
    m = _command_class(config, *args, **kwargs)
    m.addToSubparserSync(subparser)

_command_class = SDKCommand
