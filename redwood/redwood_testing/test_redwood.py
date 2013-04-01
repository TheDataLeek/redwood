#!/usr/bin/env python

import unittest
import redwood as mod
import os
import shutil

class AgeCheckTester(unittest.TestCase):

    def setUp(self):
        try:
            os.mkdir('./testdir')
            open('./testdir/testone', mode='w')
            open('./testdir/testtwo', mode='w')
            os.mkdir('./testdir/testdirtwo')
            open('./testdir/testdirtwo/one', mode='w')
            open('./testdir/testdirtwo/two', mode='w')
        except OSError:
            pass
        os.utime('./testdir', (1215121330, 1215121330))
        os.utime('./testdir/testone', (1215121330, 1215121330))
        os.utime('./testdir/testdirtwo', (1215121330, 1215121330))
        os.utime('./testdir/testdirtwo/one', (1215121330, 1215121330))
        self.file_list = ['./testdir/testone',
                          './testdir/testtwo',
                          './testdir/testdirtwo/one',
                          './testdir/testdirtwo/two']


    def testdeclaretime(self):
        assert mod.declare_time(['001min']) == (1.0 / 24) / 60
        assert mod.declare_time(['010mon']) == 10 * 30
        assert mod.declare_time(['100y']) == 365 * 100
        assert mod.declare_time(['999s']) == 0.0115625
        assert mod.declare_time(['99w']) == 693
        assert mod.declare_time(['302h']) == 302 / 24.0
        assert mod.declare_time(['32d']) == 32


    def testignore_det(self):
        assert mod.ignore_det([['/home/sherlock/test'],['/home/sherlock/projects'],['/home/sherlock/Downloads']],'/home/sherlock') == True
        assert mod.ignore_det([['/home/sherlock/test'],['/home/sherlock/projects'],['/home/sherlock/Downloads']],'/home/sherlock/Downloads') == False
        assert mod.ignore_det([['/home/sherlock/test'],['/home/sherlock/projects'],['/home/sherlock/Downloads']],'/home/sherlock/projects') == False
        assert mod.ignore_det([['/home/sherlock/test'],['/home/sherlock/projects'],['/home/sherlock/Downloads']],'/home/sherlock/test') == False
        assert mod.ignore_det([['/home/sherlock/test'],['/home/sherlock/projects'],['/home/sherlock/Downloads']],'/home/sherlock/perl') == True

    def testfilescan(self):
        assert mod.file_scan('./testdir/testone', 2, False) == True
        assert mod.file_scan('./testdir/testtwo', 2, False) == False
        assert mod.file_scan('./testdir/testdirtwo/one', 2, False) == True
        assert mod.file_scan('./testdir/testdirtwo/two', 2, False) == False

        assert mod.file_scan('./testdir/testone', 2, True) == False
        assert mod.file_scan('./testdir/testtwo', 2, True) == True
        assert mod.file_scan('./testdir/testdirtwo/one', 2, True) == False
        assert mod.file_scan('./testdir/testdirtwo/two', 2, True) == True


    def testtimecheck(self):
        assert mod.file_scan('./testdir/testone', 2, False) == True
        assert mod.file_scan('./testdir/testtwo', 2, False) == False
        assert mod.file_scan('./testdir/testdirtwo/one', 2, False) == True
        assert mod.file_scan('./testdir/testdirtwo/two', 2, False) == False

        assert mod.file_scan('./testdir/testone', 2, True) == False
        assert mod.file_scan('./testdir/testtwo', 2, True) == True
        assert mod.file_scan('./testdir/testdirtwo/one', 2, True) == False
        assert mod.file_scan('./testdir/testdirtwo/two', 2, True) == True


    def testpath_check(self):
        assert mod.path_checker('/home/', '.vimrc') == '/home/.vimrc'
        assert mod.path_checker('/home', '/.vimrc') == '/home/.vimrc'
        assert mod.path_checker('/home', '/test/.vimrc') == '/home/test/.vimrc'
        assert mod.path_checker('/home', '/test//.vimrc') == '/home/test/.vimrc'


    def tearDown(self):
        shutil.rmtree('./testdir')


if __name__ == "__main__":
    unittest.main()
