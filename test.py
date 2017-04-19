import sys
import unittest
import logging

"""Run tests

From https://stackoverflow.com/questions/1732438/how-do-i-run-all-python-unit-tests-in-a-directory
"""

# set up logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout)

testmodules = [
    'solver.test_geometry',
    'solver.test_graph',
    'solver.test_method',
    'solver.geometric.test_cluster',
    'solver.geometric.test_configuration',
    'solver.geometric.test_constraint'
    ]

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)
