"""Clusters are generalised constraints on sets of points in
:math:`\mathbb{R}^2`. Cluster types are :class:`Rigid`, :class:`Hedgehog` and
:class:`Balloon`."""

import abc
import logging
from scipy.special import binom
from .relation import Distance, Angle

class Cluster(object, metaclass=abc.ABCMeta):
    """A set of points, satisfying some constaint"""

    pretty_name = "Cluster"

    def __init__(self, vars):
        """Create a new cluster

        Specified variables should be hashable.

        :param vars: cluster variables
        :type vars: list
        """

        # cluster variables
        self.vars = set(vars)

        # default overconstrained flag
        self.overconstrained = False

    def __str__(self):
        # create character string to represent whether the cluster is
        # overconstrained
        ovr_const = ""

        if self.overconstrained:
            ovr_const += "!"

        # create string variable list
        var_str = ", ".join([str(var) for var in self.var_list()])

        return "{}{}#{}({})".format(ovr_const, self.pretty_name, id(self), var_str)

    def var_list(self):
        """Variable list for the cluster

        :returns: the cluster's variables
        :rtype: list
        """

        return list(self.vars)

    def intersection(self, other):
        """Get the intersection between this cluster and the specified cluster

        :param other: other cluster
        :type other: :class:`Cluster`
        :returns: new cluster with intersection of input clusters' variables
        :rtype: :class:`Cluster`
        :raises TypeError: if cluster types are unknown
        """

        # intersection of points between this cluster and the other
        shared = self.vars & other.vars

        if len(shared) < 2:
            # not possible to merge
            logging.getLogger("cluster").debug("No intersection between {0} and"
            " {1}: less than 2 shared points".format(self, other))

            return None

        # return appropriate intersection
        if isinstance(other, Rigid):
            return self.intersect_rigid(shared, other)
        elif isinstance(other, Hedgehog):
            return self.intersect_hedgehog(shared, other)
        elif isinstance(other, Balloon):
            return self.intersect_balloon(shared, other)

        # if all fails
        raise TypeError("Intersection of unknown cluster types")

    @abc.abstractmethod
    def intersect_rigid(self, shared, rigid):
        pass

    @abc.abstractmethod
    def intersect_hedgehog(self, shared, hedgehog):
        pass

    @abc.abstractmethod
    def intersect_balloon(self, shared, balloon):
        pass

    def over_constraints(self, other):
        """Returns the overconstraints (duplicate distances and angles) between
        this cluster and another

        Cluster pairs can be made up of :class:`~Rigid`, :class:`~Hedgehog` or
        :class`~Balloon`
        """

        # union between distances and angles in common
        return common_distances(self, other) | common_angles(self, other)

    @abc.abstractmethod
    def common_distances(self, other):
        pass

    def common_angles(self, other):
        """Determine set of angles shared by this cluster and the other"""
        if isinstance(other, Rigid):
            return self.common_angles_rigid(other)
        elif isinstance(other, Hedgehog):
            return self.common_angles_hedgehog(other)
        elif isinstance(other, Balloon):
            return self.common_angles_balloon(other)

        # if all fails
        raise TypeError("Unknown other cluster type")

    @abc.abstractmethod
    def common_angles_rigid(self, rigid):
        pass

    @abc.abstractmethod
    def common_angles_hedgehog(self, hedgehog):
        pass

    @abc.abstractmethod
    def common_angles_balloon(self, balloon):
        pass

    def n_constraints(self):
        """Number of constraints on this cluster"""
        return self.n_distances() + self.n_angles()

    @abc.abstractmethod
    def n_distances(self):
        pass

    @abc.abstractmethod
    def n_angles(self):
        pass

class Rigid(Cluster):
    """Represents a set of points that form a rigid body"""

    pretty_name = "Rigid"

    def __init__(self, *args, **kwargs):
        """Creates a new rigid cluster"""

        # call parent
        super(Rigid, self).__init__(*args, **kwargs)

    def intersect_rigid(self, shared, rigid):
        # intersection is also a rigid
        return Rigid(shared)

    def intersect_hedgehog(self, shared, hedgehog):
        # shared variables except the hedgehog's central variable
        x_vars = set(shared) - set([hedgehog.c_var])

        if hedgehog.c_var in self.vars and len(x_vars) >= 2:
            # hedgehog's central variable is in this rigid, and there are at
            # least two extra variables to form a constraint with
            return Hedgehog(hedgehog.c_var, x_vars)

        return None

    def intersect_balloon(self, shared, balloon):
        # call balloon's intersect method with reversed arguments
        return balloon.intersect_rigid(shared, self)

    def common_distances(self, other):
        """Determine set of distances shared by this cluster and the other"""

        # empty set of common distances
        common_distances = set()

        if not isinstance(other, Rigid):
            # other constraint is not rigid, so it doesn't have distances
            return common_distances

        # shared variables between this rigid and the other
        shared = list(set(self.vars) & set(other.vars))

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i):
                # get variables
                v1 = shared[i]
                v2 = shared[j]

                # add distance to set (duplicates will be avoided due to hash
                # values for each distance)
                common_distances.add(Distance(v1, v2))

        return common_distances

    def common_angles_rigid(self, rigid):
        # list of duplicate angles
        shared = list(set(self.vars) & set(rigid.vars))

        # empty set of common angles
        common_angles = set()

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i+1, len(shared)):
                # loop over third variable
                for k in range(j+1, len(shared)):
                    # get variables
                    v1 = shared[i]
                    v2 = shared[j]
                    v3 = shared[k]

                    # add combinations of angles to set (duplicates will be
                    # avoided due to hash values for each angle)
                    common_angles.add(Angle(v1, v2, v3))
                    common_angles.add(Angle(v2, v3, v1))
                    common_angles.add(Angle(v3, v1, v2))

        return common_angles

    def common_angles_hedgehog(self, hedgehog):
        # list of duplicate angles
        shared = list(set(self.vars) & set(hedgehog.x_vars))

        # empty set of common angles
        common_angles = set()

        if hedgehog.c_var not in self.vars:
            # hedgehog's central variable is not part of this rigid, so there
            # are no overconstrained angles to add
            return common_angles

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i+1, len(shared)):
                # get variables
                v1 = shared[i]
                v2 = shared[j]

                # create angles with the hedgehog's central point
                common_angles.add(Angle(v1, hedgehog.c_var, v2))

        return common_angles

    def common_angles_balloon(self, balloon):
        # list of duplicate angles
        shared = list(set(self.vars) & set(balloon.vars))

        # empty set of common angles
        common_angles = set()

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i+1, len(shared)):
                # loop over third variable
                for k in range(j+1, len(shared)):
                    # get variables
                    v1 = shared[i]
                    v2 = shared[j]
                    v3 = shared[k]

                    # add combinations of angles to set (duplicates will be
                    # avoided due to hash values for each angle)
                    common_angles.add(Angle(v1, v2, v3))
                    common_angles.add(Angle(v2, v3, v1))
                    common_angles.add(Angle(v3, v1, v2))

        return common_angles

    def n_distances(self):
        return int(binom(len(self.vars), 2))

    def n_angles(self):
        return int(binom(len(self.vars), 3) * 3)

class Hedgehog(Cluster):
    """Represents a set of points (C, X1...XN) where all angles a(Xi, C, Xj) are
    known"""

    pretty_name = "Hedgehog"

    def __init__(self, c_var, x_vars):
        """Creates a new hedgehog cluster

        :param c_var: central variable
        :param x_vars: other variables
        :type c_var: object
        :type x_vars: list(object)
        :raises ValueError: if less than three variables are specified between \
        *c_var* and *x_vars*
        """

        x_vars = set(x_vars)

        # check there are enough other variables
        if len(x_vars) < 2:
            raise ValueError("Hedgehog must have at least three unique variables")

        # variables
        self.x_vars = x_vars
        self.c_var = c_var

        # call parent constructor with all variables
        super(Hedgehog, self).__init__(self.x_vars | set([self.c_var]))

    def var_list(self):
        """Gets list of variables associated with this hedgehog

        Overrides :class:`Cluster`.

        :returns: variables
        :rtype: list
        """

        # central value followed by other variables
        return [self.c_var] + list(self.x_vars)

    def intersect_rigid(self, shared, rigid):
        # call Rigid's intersect method with reversed arguments
        return rigid.intersect_hedgehog(shared, self)

    def intersect_hedgehog(self, shared, hedgehog):
        # shared variables except each hedgehog's central variables
        x_vars = self.x_vars & hedgehog.x_vars

        if self.c_var == hedgehog.c_var and len(x_vars) >= 2:
            # each hedgehog shares the same point, so merge them
            return Hedgehog(self.c_var, x_vars)

        # not possible to merge
        return None

    def intersect_balloon(self, shared, balloon):
        # shared variables except this hedgehog's central variable
        x_vars = set(shared) - set([self.c_var])

        if self.c_var in balloon.vars and len(x_vars) >= 2:
            # this hedgehog's central value is in the balloon, so make the
            # balloon's variables extra variables of this hedgehog
            return Hedgehog(self.c_var, x_vars)

        # not possible to merge
        return None

    def common_distances(self, other):
        # hedgehog has no distances
        return set()

    def common_angles_rigid(self, rigid):
        # call rigid's common angles method with reversed arguments
        return rigid.common_angles_hedgehog(self)

    def common_angles_hedgehog(self, hedgehog):
        # list of duplicate angles
        shared = list(set(self.x_vars) & set(hedgehog.x_vars))

        # empty set of common angles
        common_angles = set()

        if not self.c_var == hedgehog.c_var:
            # central values differ, so there are no overconstrained angles to
            # add
            return common_angles

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i):
                # get variables
                v1 = shared[i]
                v2 = shared[j]

                # add angle to overconstrained set
                common_angles.add(Angle(v1, self.c_var, v2))

        return common_angles

    def common_angles_balloon(self, balloon):
        # call balloon's common angles method with reversed arguments
        return balloon.common_angles_hedgehog(self)

    def n_distances(self):
        # no distances in a hedgehog
        return 0

    def n_angles(self):
        return int(binomial(len(self.x_vars), 2))

class Balloon(Cluster):
    """Represents a set of points that is invariant to rotation, translation and
    scaling"""

    pretty_name = "Balloon"

    def __init__(self, *args, **kwargs):
        """Create a new balloon

        :raises ValueError: if less than three variables are specified
        """

        # call parent
        super(Balloon, self).__init__(*args, **kwargs)

        # check there are enough variables for a balloon
        if len(self.vars) < 3:
            raise ValueError("Balloon must have at least three variables")

    def intersect_rigid(self, shared, rigid):
        if len(shared) < 3:
            # not possible to merge
            return None

        # intersection is a balloon
        return Balloon(shared)

    def intersect_hedgehog(self, shared, hedgehog):
        # call hedgehog's intersect method with reversed arguments
        return hedgehog.intersect_balloon(shared, self)

    def intersect_balloon(self, shared, balloon):
        # same as for rigid
        return self.intersect_rigid(shared, Rigid(balloon.var_list()))

    def common_distances(self, other):
        # balloon has no distances
        return set()

    def common_angles_rigid(self, rigid):
        # call rigid's common angles method with reversed arguments
        return rigid.common_angles_balloon(self)

    def common_angles_hedgehog(self, hedgehog):
        # list of duplicate angles
        shared = list(set(self.vars) & set(hedgehog.x_vars))

        # empty set of common angles
        common_angles = set()

        if hedgehog.c_var not in self.vars:
            # hedgehog's central value is not shared with this balloon, so there
            # are no overconstrained angles to add
            return common_angles

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i+1, len(shared)):
                # get variables
                v1 = shared[i]
                v2 = shared[j]

                # add angle to overconstrained set
                common_angles.add(Angle(v1, hedgehog.c_var, v2))

        return common_angles

    def common_angles_balloon(self, balloon):
        # list of duplicate angles
        shared = list(set(self.vars) & set(balloon.vars))

        # empty set of common angles
        common_angles = set()

        # loop over first variable
        for i in range(len(shared)):
            # loop over second variable
            for j in range(i+1, len(shared)):
                # loop over third variable
                for k in range(j+1, len(shared)):
                    # get variables
                    v1 = shared[i]
                    v2 = shared[j]
                    v3 = shared[k]

                    # add combinations of angles to set (duplicates will be
                    # avoided due to hash values for each angle)
                    common_angles.add(Angle(v1, v2, v3))
                    common_angles.add(Angle(v2, v3, v1))
                    common_angles.add(Angle(v3, v1, v2))

        return common_angles

    def n_distances(self):
        # no distances in a balloon
        return 0

    def n_angles(self):
        return int(binom(len(self.vars), 3) * 3)
