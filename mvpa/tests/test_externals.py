# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test externals checking"""

import unittest

from mvpa import cfg
from mvpa.base import externals
from mvpa.support import copy

class TestExternals(unittest.TestCase):

    def setUp(self):
        self.backup = []
        # paranoid check
        self.cfgstr = str(cfg)
        # clean up externals cfg for proper testing
        if cfg.has_section('externals'):
            self.backup = copy.deepcopy(cfg.items('externals'))
        cfg.remove_section('externals')


    def tearDown(self):
        if len(self.backup):
            # wipe existing one completely
            if cfg.has_section('externals'):
                cfg.remove_section('externals')
            cfg.add_section('externals')
            for o,v in self.backup:
                cfg.set('externals', o,v)
        # paranoid check
        # since order can't be guaranteed, lets check
        # each item after sorting
        self.failUnlessEqual(sorted(self.cfgstr.split('\n')),
                             sorted(str(cfg).split('\n')))


    def testExternals(self):
        self.failUnlessRaises(ValueError, externals.exists, 'BoGuS')


    def testExternalsNoDoubleInvocation(self):
        # no external should be checking twice (unless specified
        # explicitely)

        class Checker(object):
            """Helper class to increment count of actual checks"""
            def __init__(self): self.checked = 0
            def check(self): self.checked += 1

        checker = Checker()

        externals._KNOWN['checker'] = 'checker.check()'
        externals.__dict__['checker'] = checker
        externals.exists('checker')
        self.failUnlessEqual(checker.checked, 1)
        externals.exists('checker')
        self.failUnlessEqual(checker.checked, 1)
        externals.exists('checker', force=True)
        self.failUnlessEqual(checker.checked, 2)
        externals.exists('checker')
        self.failUnlessEqual(checker.checked, 2)

        # restore original externals
        externals.__dict__.pop('checker')
        externals._KNOWN.pop('checker')


    def testExternalsCorrect2ndInvocation(self):
        # always fails
        externals._KNOWN['checker2'] = 'raise ImportError'

        self.failUnless(not externals.exists('checker2'),
                        msg="Should be False on 1st invocation")

        self.failUnless(not externals.exists('checker2'),
                        msg="Should be False on 2nd invocation as well")

        externals._KNOWN.pop('checker2')



def suite():
    return unittest.makeSuite(TestExternals)


if __name__ == '__main__':
    import runner
