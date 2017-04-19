from unittest import TestCase
from .constraint import ConstraintGraph, PlusConstraint, FunctionConstraint, \
NotClockwiseConstraint, NotCounterClockwiseConstraint, NotObtuseConstraint, \
NotAcuteConstraint
from ..geometry import Vector, is_clockwise

class TestConstraints(TestCase):
    def setUp(self):
        self.problem = ConstraintGraph()

        self.problem.add_variable('a')
        self.problem.add_variable('b')
        self.problem.add_variable('d')
        self.problem.add_variable('f')
        self.problem.add_variable('g')

        # create plus constraints
        self.plus1 = PlusConstraint('a', 'b', 'c')
        self.plus2 = PlusConstraint('c', 'd', 'e')
        self.plus3 = PlusConstraint('e', 'f', 'g')

        self.problem.add_constraint(self.plus1)
        self.problem.add_constraint(self.plus2)
        self.problem.add_constraint(self.plus3)

    def test_variables(self):
        # all variables including implictly defined ones should be there
        self.assertIn('a', self.plus1.variables())
        self.assertIn('b', self.plus1.variables())
        self.assertIn('c', self.plus1.variables())
        self.assertIn('c', self.plus2.variables())
        self.assertIn('d', self.plus2.variables())
        self.assertIn('e', self.plus2.variables())
        self.assertIn('e', self.plus3.variables())
        self.assertIn('f', self.plus3.variables())
        self.assertIn('g', self.plus3.variables())

    def test_get_constraints_on(self):
        # all of the variables should have plus as a constraint
        self.assertIn(self.plus1, self.problem.get_constraints_on('a'))
        self.assertIn(self.plus1, self.problem.get_constraints_on('b'))
        self.assertIn(self.plus1, self.problem.get_constraints_on('c'))
        self.assertIn(self.plus2, self.problem.get_constraints_on('c'))
        self.assertIn(self.plus2, self.problem.get_constraints_on('d'))
        self.assertIn(self.plus2, self.problem.get_constraints_on('e'))
        self.assertIn(self.plus3, self.problem.get_constraints_on('e'))
        self.assertIn(self.plus3, self.problem.get_constraints_on('f'))
        self.assertIn(self.plus3, self.problem.get_constraints_on('g'))

    def test_get_constraints_on_all(self):
        # a and b only have plus1
        self.assertEqual(self.problem.get_constraints_on_all(['a', 'b']), \
        [self.plus1])

        # adding c shouldn't change the fact
        self.assertEqual(self.problem.get_constraints_on_all(['a', 'b', 'c']), \
        [self.plus1])

    def test_get_constraints_on_any(self):
        # c has two constraints, so we should see them
        # use sets to avoid differences in order
        self.assertEqual(set(self.problem.get_constraints_on_any(['a', 'b', \
        'c'])), set([self.plus1, self.plus2]))

        # e too
        self.assertEqual(set(self.problem.get_constraints_on_any(['a', 'b', \
        'c', 'd', 'e', 'f', 'g'])), set([self.plus1, self.plus2, self.plus3]))

class TestFunctionConstraint(TestCase):
    def setUp(self):
        # function constraint to check if a triangle is clockwise
        self.constraint = FunctionConstraint(is_clockwise, \
        ['a', 'b', 'c'])

    def test_function(self):
        # clockwise should be true
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 1), \
        'b': Vector(1, 0), 'c': Vector(0, -1)}))

        # counter clockwise should be false
        self.assertFalse(self.constraint.satisfied({'a': Vector(0, -1), \
        'b': Vector(1, 0), 'c': Vector(0, 1)}))

class TestNotClockwiseConstraint(TestCase):
    def setUp(self):
        self.constraint = NotClockwiseConstraint('a', 'b', 'c')

    def test_notclockwise(self):
        # counter clockwise should be true
        self.assertTrue(self.constraint.satisfied({'a': Vector(1, 0), \
        'b': Vector(0, 1), 'c': Vector(0, -1)}))

        # clockwise should be false
        self.assertFalse(self.constraint.satisfied({'a': Vector(1, 0), \
        'b': Vector(0, -1), 'c': Vector(0, 1)}))

        # edge case: 3 points on top of each other
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(0, 0), 'c': Vector(0, 0)}))

class TestNotCounterClockwiseConstraint(TestCase):
    def setUp(self):
        self.constraint = NotCounterClockwiseConstraint('a', 'b', 'c')

    def test_notcounterclockwise(self):
        # clockwise should be true
        self.assertTrue(self.constraint.satisfied({'a': Vector(1, 0), \
        'b': Vector(0, -1), 'c': Vector(0, 1)}))

        # counter clockwise should be false
        self.assertFalse(self.constraint.satisfied({'a': Vector(1, 0), \
        'b': Vector(0, 1), 'c': Vector(0, -1)}))

        # edge case: 3 points on top of each other
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(0, 0), 'c': Vector(0, 0)}))

class TestNotObtuseConstraint(TestCase):
    def setUp(self):
        self.constraint = NotObtuseConstraint('a', 'b', 'c')

    def test_notobtuse(self):
        # obtuse should be true
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(1, 0), 'c': Vector(0, 1)}))

        # acute should be false
        self.assertFalse(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(1, 0), 'c': Vector(2, 1)}))

        # edge case: 90 degrees
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(1, 0), 'c': Vector(1, 1)}))

class TestNotAcuteConstraint(TestCase):
    def setUp(self):
        self.constraint = NotAcuteConstraint('a', 'b', 'c')

    def test_notacute(self):
        # acute should be true
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(1, 0), 'c': Vector(2, 1)}))

        # obtuse should be true
        self.assertFalse(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(1, 0), 'c': Vector(0, 1)}))

        # edge case: 90 degrees
        self.assertTrue(self.constraint.satisfied({'a': Vector(0, 0), \
        'b': Vector(1, 0), 'c': Vector(1, 1)}))
