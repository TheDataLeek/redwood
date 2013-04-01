#!/usr/bin/env python

"""

=====================================================
|     _ __ ___  __| |_      _____   ___   __| |     |
|    | '__/ _ \/ _` \ \ /\ / / _ \ / _ \ / _` |     |
|    | | |  __/ (_| |\ V  V / (_) | (_) | (_| |     |
|    |_|  \___|\__,_| \_/\_/ \___/ \___/ \__,_|     |
=====================================================

Redwood is a tool to analyze directory trees and flag all files that are
either too new or too old based on specifications. After it's flagged
the files it will then either just stop there, or it will delete the
flagged files depending on user specification.

"""

import sys
import os
import time
import optparse
import logging
import shutil
import yaml
import subprocess


def main():
    """ Program main
        Gets options, runs code, logs output
    """
    opts = get_args()

    config_file = open('./.redwood.yaml', mode='r')
    config      = yaml.load(config_file)

    log_location = config['logfile']

    if (opts.clean or config['clean']):  # Essentially just erases the old log
        open(log_location, mode='w').close()

    # Defines logfile, log level, and log format
    logging.basicConfig(
                        filename=log_location,
                        level=logging.DEBUG,
                        format='%(levelname)s\t|\t%(asctime)s\t-\t %(message)s')
    logging.debug(opts)  # For debug purposes, write opts to log
    logging.debug(config)  # For debug purposes, write opts to log
    logging.info('START')
    special_directories = declare_special_directories(config)
    old_dirs                 = dir_scan(special_directories, config)
    report                   = open('./report.txt', mode='w')
    report.write('%s\n' %(opts))
    for item in old_dirs:  # Write each file violation to a report
        report.write(time.ctime() + '    ----    ')  # Include time
        report.write(item + "\n")
    if opts.delete:
        cleanser(old_dirs, opts.force, opts.trash)


def cleanser(old_dirs, force, trash):
    """ Deletes files listed in old_dirs
        If the --force option is not supplied it will ask for confirmation
        before deleting any files.
        If the --force flag is present, it will automatically delete any
        files listed.
    """
    for item in old_dirs:
        if force:  # If --force was supplied, don't ask
            response = True
        elif force is False:  # Otherwise ask
            response = raw_input('Delete %s? (y/N) ' %(item))
            if response.lower() == 'y':
                response = True
            else:
                response = False

        if response is True:
            logging.warning('DELETING %s' %(item))
            if trash is not None:  # Use trash if present
                trash_location = trash + os.path.basename(item)
                os.rename(item, trash_location)
            else:
                remover(item)
            if os.listdir(os.path.dirname(item)) == []: # Delete empty dirs
                logging.warning('EMPTY DIRECTORY - DELETING %s'\
                                 %(os.path.dirname(item)))
                remover(os.path.dirname(item))


def remover(path):
    """ This function will delete any file or folder given"""
    try:
        os.remove(path)  # Delete the file
    except OSError:
        shutil.rmtree(path)  # Delete the tree


def declare_special_directories(config):
    """ Scans the config files (default .redwoodrc) and puts all directories
        that the program is supposed to ignore in a list.
        This function actually reads the logfile as a .csv
    """
    special_directories = []
    dir_listing_file = open(config['ignorefile'], mode='r')
    line = dir_listing_file.readline()
    while line != '':
        special_directories.append(line[:len(line) - 1])
        line = dir_listing_file.readline()
    logging.info('Ignoring %s' %(special_directories))
    return special_directories


def declare_time(dir_age):
    """Determine the maximum/minimum age of the files
       It does this through converting the specified
       age to days.
    """
    if dir_age.endswith('y'):
        age = float(dir_age[:len(dir_age) - 1]) * 365
    elif dir_age.endswith('mon'):
        age = float(dir_age[:len(dir_age) - 3]) * 30
    elif dir_age.endswith('w'):
        age = float(dir_age[:len(dir_age) - 1]) * 7
    elif dir_age.endswith('d'):
        age = float(dir_age[:len(dir_age) - 1])
    elif dir_age.endswith('h'):
        age = float(dir_age[:len(dir_age) - 1]) / 24
    elif dir_age.endswith('min'):
        age = (float(dir_age[:len(dir_age) - 3]) / 24) / 60
    elif dir_age.endswith('s'):
        age = ((float(dir_age[:len(dir_age) - 1]) / 24) / 60) / 60
    else:
        print 'INVALID AGE'
        age = 7
    return age


def dir_scan(special_directories, config):
    """ This function runs through the specified directory using os.walk()
        os.walk() generates a tuple that is then sorted
    """
    old_dirs = []
    for item in config['directory_list']:
        cwd     = config['directory_list'][item][0]['directory']
        mndepth = config['directory_list'][item][1]['mindepth']
        mxdepth = config['directory_list'][item][2]['maxdepth']
        age     = config['directory_list'][item][3]['age']
        reverse = config['directory_list'][item][4]['reverse']
        logging.info(cwd)
        files = subprocess.Popen('find %s -maxdepth %i -mindepth %i'
                                 %(cwd, mxdepth, mndepth),
                                 stdout=subprocess.PIPE,
                                 shell=True)
        file_list = files.communicate()[0].splitlines()
        for entry in file_list:
            flag = 2
            if config['empty']:
                try:
                    if os.listdir(entry) == []:
                        if config['and']:
                            flag -= 1
                        else:
                            logging.info('%s is empty' %(entry))
                            old_dirs.append(entry)
                except OSError:
                    pass
            age_tag = False
            logging.info('Checking %s' %(entry))
            ignore_flag = ignore_det(special_directories, entry)
            if ignore_flag:  # If we have to look at the file
                age_tag = file_scan(entry, declare_time(age), reverse)
            elif ignore_flag == False:  # If we ignore the file
                logging.info('Ignoring %s' %(entry))
            if age_tag:  # If the file is too old
                if config['and']:
                    flag -= 1
                else:
                    old_dirs.append(entry)
            if flag == 0:
                old_dirs.append(entry)
    return old_dirs


def ignore_det(special_directories, full_path):
    """ Determines if the current directory is to be ignored or not """
    ignore_flag = 1
    for field in special_directories:
        if full_path.startswith(field):
            ignore_flag *= 0
    if ignore_flag == 1:
        return True  # Return True if it is not ignored
    else:
        return False  # Return False if it's ignored


def file_scan(full_path, age, reverse):
    """ Individual file logic for the scan """
    try:
        flag = time_checker(full_path, age, reverse)
        if flag:  # If the file is fine
            return False
        else:
            if reverse:
                logging.info('----%s is new----' %(full_path))
            else:
                logging.info('----%s is old----' %(full_path))
            return True
    except OSError:
        logging.error('Unable to open %s, do you have permission?' %(full_path))
        return False


def time_checker(cfile, age, reverse):
    """ Determines if the file is too old or too new """
    now = time.time()  # Get current time
    timestamp = os.path.getmtime(cfile)  # Get last modified time
    if reverse:
        if (now - timestamp) < (age * 86400):  # Seconds in a day
            return False
        else:
            return True
    else:
        if (now - timestamp) > (age * 86400):
            return False
        else:
            return True


def get_args():
    """ Acquires command line input from user """
    global opts
    global args
    parser = optparse.OptionParser(usage = './%prog <options>')
    parser.add_option('-a', '--and', action='store_true',
                        default=False,
                        help='Flag only if both conditions are met?\
                                Note, this only applies if the -e flag\
                                is supplied as well.')
    parser.add_option('-c', '--clean', action='store_true',
                        default=False,
                        help='Clean logfile first?')
    parser.add_option('-d', '--directory', action='append',
                        default=None,
                        type='string',
                        help='Target Directory(s). If you wish\
                                to include multiple directories, seperate\
                                them using multiple -d arguments')
    parser.add_option('--delete', action='store_true',
                        default=False,
                        help='Delete flagged files?')
    parser.add_option('-e', '--empty', action='store_true',
                        default=False,
                        help='Flag empty directories as well?')
    parser.add_option('--force', action='store_true',
                        default=False,
                        help='Whether or not to ask for confirmation when\
                                deleting files. If this flag is included,\
                                it will NOT ask for confirmation.')
    parser.add_option('-l', '--logfile', action='store',
                        default='./',
                        type='string', help='Directory for the logfile')
    parser.add_option('-o', '--optionfile', action='store',
                        default='./',
                        type='string', help='Which config file to use')
    parser.add_option('-r', '--report', action='store',
                        default='./',
                        type='string', help='Directory for the report')
    parser.add_option('--reverse', action='store_true',
                        default=False,
                        help='Whether or not to pick files that are newer\
                                or older than the specified time. If this\
                                option is included, any files that are newer\
                                than the time set in .redwoodrc will be flagged\
                                or deleted, depending on other options.')
    parser.add_option('-t', '--trash', action='store',
                        default=None,
                        help='Location for trash. If this flag is present\
                        redwood will move old files to this directory\
                        instead of deleting them.')
    opts, args = parser.parse_args()
    if opts.a is True and opts.e is False:
        opts.a = False
    return opts


if __name__ == "__main__":
    sys.exit(main())
