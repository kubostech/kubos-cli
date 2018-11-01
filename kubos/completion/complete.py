#!/usr/bin/python

import json
import sys
import os


def main():
    '''
    This script works by coming up with a list of possible completions and printing
    those suggestions, separated by spaces to stdout
    '''
    completer = Completer()
    completions = completer.get_completions()
    if completions is not None:
        for c in completions:
            print str(c) + '  ',
    else:
        sys.exit(0)


class Completer(object):
    JSON_FILE = os.path.join(os.path.expanduser(
        '~'), '.kubos', 'completion', 'options.json')

    def __init__(self):
        if os.path.isfile(self.JSON_FILE):
            with open(self.JSON_FILE, 'r') as _fil:
                self.arg_data = json.loads(_fil.read())
        else:
            self.arg_data = None
        # chop off the initial 'python kubos' arguments
        self.args = sys.argv[2:]
        self.subcommands = self.get_current_subcommands()
        self.load_targets()

    def load_targets(self):
        '''
        Load the available targets, based on the current project's platform type
        '''
        platform = self.get_platform()
        targets = self.load_target_list(platform)
        self.arg_data['subcommands']['target']['set_target']['choices'] = targets

    def get_completions(self):
        # Only completing the subcommands and their args is supported right now.
        # Completing the global options (--config, --target, etc.) should be supported in the future.
        return self.eval_subcommands()

    def eval_subcommands(self):
        '''
        Returns list of possible subcommand, and subcommand specific arguments based
        on the currently provided arguments

        This works by starting with the first argument, removing arguments from 
        the front of the self.args list, as subcommand and arguments are processed.
        '''
        num_args = len(self.args)
        if num_args == 0:
            # nothing has been entered - return every subcommand
            return self.subcommands
        else:
            possible_arguments = []
            # get all the possible subcommand completions for the entered text
            possible_subcommands = self.get_current_subcommand_completion()
            subcommand = self.get_current_subcommand()
            if subcommand is not None:
                # gets all possible argument values for the subcommand
                possible_arguments = self.get_valid_subcommand_argument_list(
                    subcommand)
                # try to get an argument following the subcommand
                arg = self.get_next_arg()
                if arg is not None:
                    # drop other subcommand completions - they're already typing an argument for the subcommand
                    possible_subcommands = []
                    possible_arguments = self.get_completions_from_list(
                        arg, possible_arguments)
                    if self.is_valid_subcommand_arg(subcommand, arg):
                        # if we've already completed a complete and valid argument, stop suggesting it.
                        return []
            return possible_arguments + possible_subcommands

    def get_completions_from_list(self, val, option_list):
        '''
        Generic function for returning all values from option_list that start with
        the value of val
        '''
        ret_list = []
        for option in option_list:
            if option.startswith(val):
                ret_list.append(option)
        return ret_list

    def get_current_subcommand_completion(self):
        '''
        Returns all possible subcommand name completions for the next argument
        '''
        arg_val = self.args[0]  # we should get the subcommand name first
        return self.get_completions_from_list(arg_val, self.subcommands)

    def get_next_arg(self):
        '''
        pop the next arg off the front of the provided arguments and return it
        '''
        if len(self.args) > 0:
            return self.args.pop(0)
        return None

    def get_current_subcommand(self):
        '''
        Returns the subcommand name if next argument is a valid subcommand or None if it isn't
        '''
        val = self.args.pop(0)
        if val in self.subcommands:
            return val
        else:
            return None

    def is_valid_subcommand_arg(self, subcommand, arg):
        '''
        Returns True if arg is a valid argument for subcommand, otherwise it returns False
        '''
        valid_args = self.get_valid_subcommand_argument_list(subcommand)
        if arg in valid_args:
            return True
        return False

    def get_valid_subcommand_argument_list(self, subcommand):
        '''
        Returns a list of the valid argument completions for subcommand.
        The list is constructed of argument names that start with '--' and the
        choices for positional arguments (like target names)
        '''
        args = self.arg_data['subcommands'][subcommand]
        choices = []
        for arg in args:
            if arg.startswith('--'):
                choices.append(arg)
            else:
                if 'choices' in args[arg] and args[arg]['choices'] is not None:
                    choices += args[arg]['choices']
        return choices

    def get_current_subcommands(self):
        '''
        This function contains the try/except because it's the first function
        that would encounter a type error in the case the options.json file
        does not exist.
        '''
        try:
            subcommands = self.arg_data['subcommands']
            return subcommands.keys()
        except TypeError:
            sys.exit(1)

    ################################################################
    #                  CLI DUPLICATED FUNCTIONS
    ################################################################
    '''
    Importing the following functions from the CLI slows down the execution of this
    script by a factor of about 20.
    '''

    def get_platform(self):
        module_json = os.path.join(os.getcwd(), 'module.json')
        if os.path.isfile(module_json):
            with open(module_json, 'r') as module_file:
                data = json.loads(module_file.read())
            if 'dependencies' in data:
                deps = data['dependencies']
                if 'kubos-rt' in deps:
                    return 'rt'
                else:
                    return 'linux'
            else:
                # This project doesn't have a dependencies field. This is most likely running in a unit testing context
                return None
        else:
            # There is no module.json
            return None

    def load_target_list(self, platform):
        KUBOS_TARGET_CACHE_FILE = os.path.join(
            os.path.expanduser('~'), '.kubos', 'targets.json')
        if not os.path.isfile(KUBOS_TARGET_CACHE_FILE):
            return None
        with open(KUBOS_TARGET_CACHE_FILE, 'r') as json_file:
            data = json.loads(json_file.read())
        linux_targets = data['linux-targets']
        rt_targets = data['rt-targets']
        if platform == None:  # if no platform is listed in the module.json, dont restrict the target type
            return linux_targets + rt_targets
        elif platform == 'linux':
            return linux_targets
        elif platform == 'rt':
            return rt_targets


if __name__ == '__main__':
    main()
