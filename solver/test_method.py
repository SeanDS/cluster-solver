from unittest import TestCase
from .method import MethodGraph, AddMethod, MultiVariable, SumProdMethod, \
MethodGraphCycleException, MethodGraphDetermineException

class TestMethods(TestCase):
    def setUp(self):
        self.mg = MethodGraph()

        # add some variables
        self.mg.add_variable('a', 3)
        self.mg.add_variable('b', 4)

        # add an add method
        self.mg.add_method(AddMethod('a', 'b', 'c'))

    def test_add_method(self):
        # default values
        self.assertEqual(self.mg.get('c'), 7)

        # overwrite a
        self.mg.set('a', 10)

        self.assertEqual(self.mg.get('c'), 14)

    def test_recursive_add(self):
        # a + c = d, i.e. a + (a + b) = d
        self.mg.add_method(AddMethod('a', 'c', 'd'))

        self.assertEqual(self.mg.get('d'), 10)

        # b + d = e, i.e. b + (a + (a + b)) = e
        self.mg.add_method(AddMethod('b', 'd', 'e'))

        self.assertEqual(self.mg.get('e'), 14)

    def test_exceptions(self):
        # recursive adds
        self.mg.add_method(AddMethod('a', 'c', 'd'))
        self.mg.add_method(AddMethod('b', 'd', 'e'))

        # can't create cycles, e.g. by setting a to the result of something that
        # depends on a
        with self.assertRaises(MethodGraphCycleException):
            self.mg.add_method(AddMethod('d', 'e', 'a'))

        # can't have variables determined by more than one method
        with self.assertRaises(MethodGraphDetermineException):
            self.mg.add_method(AddMethod('a','b','e'))

class TestSumProdMethod(TestCase):
    def setUp(self):
        # graph
        self.graph = MethodGraph()

        # multivariables
        self.x = MultiVariable('x')
        self.y = MultiVariable('y')
        self.z = MultiVariable('z')

    def test_sum_prod_method(self):
        self.graph.add_variable('a', 1)
        self.graph.add_variable('b', 2)

        self.graph.add_variable(self.x)

        # add sum product method
        self.graph.add_method(SumProdMethod('a', 'b', self.x))

        self.graph.add_variable('p', 3)
        self.graph.add_variable('q', 4)

        self.graph.add_variable(self.y)

        # add sum product method
        self.graph.add_method(SumProdMethod('p', 'q', self.y))

        self.graph.add_variable(self.z)

        # add sum product method
        self.graph.add_method(SumProdMethod(self.x, self.y, self.z))

        self.assertEqual(self.graph.get(self.z), \
        set([36, 21, 24, 9, 10, 14, 15]))
