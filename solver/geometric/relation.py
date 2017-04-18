"""Relations are constraints between groups of points, such as the distance
between two points or the angle between three."""

import abc
import numpy as np

class PointRelation(object, metaclass=abc.ABCMeta):
    """Represents a relation between a set of points"""

    pretty_name = "Point Relation"

    def __init__(self, points):
        """Creates a new point relation

        :param points: list of points
        :type points: list
        """

        self.points = list(points)

    def __str__(self):
        # comma separated points
        points = ", ".join(self.points)

        return "{0}({1})".format(self.pretty_name, points)

    @abc.abstractmethod
    def __eq__(self, other):
        pass

    def __hash__(self):
        """Hash value of the relation

        This is required in order for relationships between the same points to
        be deduplicated in sets (e.g. :class:`cluster.Rigid.over_angles_rigid`).
        """

        return hash(frozenset(self.points))

class Distance(PointRelation):
    """Represents a defined distance between two points"""

    pretty_name = "Distance"

    def __init__(self, a, b):
        """Creates a new known distance

        The distance is defined between points *a* and *b*

        :param a: first point
        :param b: second point
        :type a: :class:`~.np.ndarray`
        :type b: :class:`~.np.ndarray`
        """

        # call parent constructor
        super(Distance, self).__init__([np.array(a), np.array(b)])

    def __eq__(self, other):
        if isinstance(other, Distance):
            # check points are the same
            return frozenset(self.points) == frozenset(other.points)

        # other object is not same type
        return False

class Angle(PointRelation):
    """Represents a defined angle between three points"""

    pretty_name = "Angle"

    def __init__(self, a, b, c):
        """Creates a new known angle

        The angle is defined at the *b* edge between *a* and *c*.

        :param a: first point
        :param b: second point
        :param c: third point
        :type a: :class:`~.np.ndarray`
        :type b: :class:`~.np.ndarray`
        :type c: :class:`~.np.ndarray`
        """

        # call parent constructor
        super(Angle, self).__init__([np.array(a), np.array(b), np.array(c)])

    def __eq__(self, other):
        if isinstance(other, Angle):
            # check the middle point is identical, and that the other points are
            # the included
            return self.points[1] == other.points[1] \
            and frozenset(self.points) == frozenset(other.points)

        # other object is not same type
        return False
