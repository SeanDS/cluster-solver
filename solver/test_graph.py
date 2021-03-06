from unittest import TestCase
from .graph import Graph

class TestGraph(TestCase):
    def setUp(self):
        self.g = Graph()

        self.g.add_bi_edge('a', 'b')
        self.g.add_edge('a', 'c')
        self.g.add_edge('a', 'd')
        self.g.add_edge('b', 'c')
        self.g.add_bi_edge('b', 'd')
        self.g.add_bi_edge('c', 'd')

    def test_reverse(self):
        reverse_edges = self.g.reverse().edges()

        # test the reversed edges are in the reversed graph
        for edge in self.g.edges():
            self.assertTrue((edge[1], edge[0]) in reverse_edges)

    def test_subgraph(self):
        vertices = ['a', 'b', 'c']
        vertices_set = set(vertices)

        subgraph = self.g.subgraph(vertices)

        # check only subgraph vertices are in the new graph's edges
        for edge in subgraph.edges():
            self.assertFalse(len(set(edge).difference(vertices_set)) > 0)
