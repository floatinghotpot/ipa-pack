#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys, os, subprocess
from tkinter.tix import Tree
from .version import __version__

sys.path.append(os.getcwd())

def runCmd(cmd, capture_output= False):
    #print(cmd)
    ret = subprocess.run( cmd, shell=True, capture_output= capture_output )
    return ret.returncode, ret.stdout.decode() if capture_output else ''

def cli_main_help():
    syntax_tips = '''
Usage:
    __argv0__ [-s signature] application [-o output_directory]
    [-verbose] [-plugin plugin] || -man || -help

    Options:

        -s <signature>  certificate name to resign application before packaging
        -o              specify output filename
        -plugin         specify an optional plugin
        -help           brief help message
        -man            full documentation
        -v[erbose]      provide details during operation
'''.replace('__argv0__', sys.argv[0])
    print(syntax_tips)

def cli_main_manpage():
    manpage = '''
NAME
    __argv0__ - prepare an application for submission to AppStore
    or installation by iTunes.

SYNOPSIS
    __argv0__ [-s signature] application [-o output_directory]
    [-verbose] [-plugin plugin] || -man || -help

    Options:

        -s <signature>  certificate name to resign application before packaging
        -o              specify output filename
        -plugin         specify an optional plugin
        -help           brief help message
        -man            full documentation
        -v[erbose]      provide details during operation

OPTIONS
    -s      Optional codesigning certificate identity common name. If
            provided, the application is will be re-codesigned prior to
            packaging.

    -o      Optional output filename. The packaged application will be
            written to this location.

    -plugin Specify optional plugin. The packaged application will include
            the specified plugin(s).

    -help   Print a brief help message and exits.

    -man    Prints the manual page and exits.

    -verbose
            Provides additional details during the packaging.

DESCRIPTION
    This program will package the specified application for submission to
    the AppStore or installation by iTunes.
'''.replace('__argv0__', sys.argv[0])
    print(manpage)

def option_format_from_strlist(option_format_list):
    option_format = {}
    for str in option_format_list:
        if '=' in str:
            items = str.split('=')
        else:
            items = [str, '']
        if '|' in items[0]:
            keys = items[0].split('|')
        else:
            keys = [items[0]]
        for key in keys:
            option_format[ key ] = items[1]
    return option_format

# -option value
def parse_perl_params_options(argv, option_format_list):
    option_format = option_format_from_strlist(option_format_list)
    params = []
    options = {}
    i = 1
    n = len(argv)
    while i < n:
        str = argv[i]
        if str[0] == '-':
            option_key = str[1:]
            if option_key in option_format:
                option_type = option_format[ option_key ]
                if option_type: # -option arg
                    i += 1
                    if i < n:
                        options[ '-' + option_key ] = argv[ i ]
                    else:
                        cli_main_help()
                        exit()
                    pass
                else: # -option
                    options[ '-' + option_key ] = ''
        else:
            params.append(str)
        i += 1

    return params, options

def confirm_installed( bin ):
    status, output = runCmd( 'which ' + bin )
    print(status, output)
    pass

def cli_main_params_options(params, options):
    if ('-help' in options):
        cli_main_help()
        return

    if ('-man' in options):
        cli_main_manpage()
        return

    if len(params) == 0:
        cli_main_help()
        print('error: An application was not specified.')
        return

    origApp = params[0]
    verbose = ('-v' in options) or ('-verbose' in options)
    if verbose:
        print( "Packaging application: '" + origApp + "'\n" )
        print( 'Arguments: ')
        for key, value in options.items():
            print( key, '=', value)
        print('\n')

    # check any plugins that might be specified

    # setup the output name if it isn't specified
    if '-o' in options:
        output = options['-o']
    elif '-output' in options:
        output = options['-output']
    else:
        output = os.path.dirname(origApp) + '/' + os.path.basename(origApp).replace('.app', '.ipa')
    if verbose:
        print("Output directory: '" + output + "'\n")

    # Make sure we have a temp dir to work with
    tmpDir = './tmp'
    if verbose:
        print( "Temporary Directory: '" + tmpDir + "'")

    ################## Start Packaging #####################

    ### Step One : Make a copy of the application (and any plugins)

    appName = os.path.basename(origApp)
    destAppDir = tmpDir + '/Payload'
    destApp = destAppDir + '/' + appName

    os.mkdir(destAppDir)
    if not os.path.exists(destAppDir):
        print("Unable to create directory : '{}'", destAppDir)
        return

    runCmd('/bin/cp -Rp ' + origApp + ' ' + destAppDir)
    if not os.path.exists(destApp):
        print("Unable to copy application '{}' into '{}'", origApp, destAppDir)
        return

    plugins = options['-plugin'].split(',') if '-plugin' in options else []
    for plugin in plugins:
        pluginName = os.path.basename(plugin)
        destPlugin = destAppDir + '/' + pluginName
        status, output = runCmd('/usr/bin/codesign --verify -vvvv ' + plugin, capture_output= True)
        if 'valid on disk' not in output:
            print("Codesign check fails : {}\n", output)
            return

        runCmd('/bin/cp -Rp ' + plugin + ' ' + destAppDir)
        if not os.path.exists(destPlugin):
            print("Unable to copy application '{}' into '{}'", plugin, destAppDir)
            return

    if '-symbols' in options:
        symbols = options['-symbols']
        destSymbols = tmpDir + '/Symbols'
        runCmd('/bin/cp -Rp ' + symbols + ' ' + destSymbols)
        if not os.path.exists(destSymbols):
            print("Unable to copy symbols '{}' into '{}'", symbols, destSymbols)
            return

    ### Step Two : recode sign it if necessary

    ### Step Three : zip up the package

def cli_main():
    params, options = parse_perl_params_options(sys.argv, ['sign|s=s','embed|e=s','output|o=s','symbols=s','verbose|v','help|h|?','man','plugin=s'])
    cli_main_params_options(params, options)

if __name__ == "__main__":
    cli_main()
