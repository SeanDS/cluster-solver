"""Provides a Configuration class representing a set of named points with
coordinates"""

import logging
from ..geometry import Scalar, Vector, Matrix, distance_2p, make_hcs, \
make_hcs_scaled, cs_transform_matrix

class Configuration(object):
    """A set of named points with coordinates.

    Immutable. Defines equality and a hash function.
    """

    def __init__(self, mapping):
        """Instantiate a configuration

        :param mapping: dictionary mapping between variables and points, e.g. \
        {v0: p0, v1: p1, v2: p2}, note that points are objects of class \
        :class:`Vector`
        """

        # dictionary mapping variable names to point values
        self.mapping = dict(mapping)

        # flag indicating an underconstrained merge (i.e. not a unique solution)
        self.underconstrained = False

        self.makehash()

    def copy(self):
        """Shallow copy of this configuration"""

        # new configuration
        new = Configuration(self.mapping)

        # copy underconstrained flag
        new.underconstrained = self.underconstrained

        return new

    def vars(self):
        """Iterator for this configuration's variable list"""
        return self.mapping.keys()

    def get(self, var):
        """Coordinates for the specified variable

        :param var: variable to get coordinates for
        """

        return self.mapping[var]

    def transform(self, t):
        """Creates a new configuration representing this one transformed by
        matrix t

        :param t: transformation matrix
        """

        # empty dict of new coordinates
        new_mapping = {}

        # loop over each coordinate in this configuration
        for v in self.mapping:
            # calculate the new homogeneous coordinate
            ph = (t * Matrix([[self.mapping[v].x, self.mapping[v].y, 1.0]]).transpose()).elements

            # create a vector for the new coordinates
            new_mapping[v] = Vector(ph[0][0] / ph[2][0], ph[1][0] / ph[2][0])

        # create and return a new configuration using the new coordinates
        return Configuration(new_mapping)

    def add(self, c):
        """Create a new configuration representing this one extended with all
        points in c not in this configuration"""

        # empty dict of new coordinates
        new_mapping = {}

        # FIXME: just deep copy the dict - loop not needed
        # loop over each coordinate in this configuration
        for v in self.mapping:
            # copy the coordinate into the new set
            new_mapping[v] = self.mapping[v]

        # loop over the coordinates in the other configuration
        for v in c.mapping:
            # copy any coordinates not present in this configuration
            if v not in new_mapping:
                new_mapping[v] = c.mapping[v]

        # create and return a new configuration using the new coordinates
        return Configuration(new_mapping)

    def select(self, variables):
        """Create a new configuration that is a subconfiguration of this
        one containing only the selected variables

        :param variables: variables to select from this configuration
        """

        # empty dict of new coordinates
        new_mapping = {}

        # FIXME: probably a smarter way to select the variables
        for v in variables:
            new_mapping[v] = self.mapping[v]

        # create and return a new configuration using the new coordinates
        return Configuration(new_mapping)

    def merge(self, other):
        """Creates a new configuration which is this one, plus another
        configuration transformed such that the common points overlap, where
        possible

        :param other: other configuration to transform and merge
        """

        logging.getLogger("configuration").debug("Merging %s with %s", self, other)

        # calculate the transform matrix and get the underconstrained status
        t, underconstrained = self.transformation_matrix(other)

        # add the transformed version of other configuration to this one
        merged_configuration = self.add(other.transform(t))

        return merged_configuration, underconstrained

    def transformation_matrix(self, other):
        """Calculates the transformation matrix required to overlap the provided
        configuration with this one, such that, where possible, common points
        overlap

        :param other: other configuration to calculate the transformation matrix \
        for
        """

        # get the variables shared between the two configurations
        shared = set(self.vars()) & set(other.vars())

        # work out whether the merged configuration will be underconstrained
        underconstrained = self.underconstrained or other.underconstrained

        # check if there are shared variables
        if len(shared) == 0:
            # by definition, this is underconstrained
            underconstrained = True

            # calculate homogeneous unit vectors for the two configurations
            # using the origin
            cs1 = make_hcs(Vector.origin(), Vector(1.0, 0.0))
            cs2 = make_hcs(Vector.origin(), Vector(1.0, 0.0))
        elif len(shared) == 1:
            # underconstrained if there is more than one variable in each
            # configuration
            if len(self.vars()) > 1 and len(other.vars()) > 1:
                underconstrained = True

            # get the only shared variable
            v1 = list(shared)[0]

            # get coordinates associated with the only shared variable in each
            # configuration
            p11 = self.mapping[v1]
            p21 = other.mapping[v1]

            # calculate homogenous unit vectors for the two configurations using
            # the only shared variable's coordinates in each case
            cs1 = make_hcs(p11, p11 + Vector(1.0, 0.0))
            cs2 = make_hcs(p21, p21 + Vector(1.0, 0.0))
        else:
            # get the first two shared variables
            v1 = list(shared)[0]
            v2 = list(shared)[1]

            # FIXME: the following code is duplicated for this and the other
            # configuration - turn into a function (this is also used in merge_scale)

            # get the coordinates associated with the first two shared variables
            # in this configuration
            p11 = self.mapping[v1]
            p12 = self.mapping[v2]

            # check if the coordinates overlap
            if Scalar.tol_zero((p12 - p11).length):
                # coordinates overlap, so the merge is underconstrained
                underconstrained = True

                # calculate the homogenous coordinate system for the first
                # configuration using only the first shared point
                cs1 = make_hcs(p11, p11 + Vector(1.0, 0.0))
            else:
                # coordinates are different, so calculate the homogenous
                # coordinate system for the first configuration using the
                # vectors of the first two shared coordinates
                cs1 = make_hcs(p11, p12)

            # get the coordinates associated with the first two shared variables
            # in the other configuration
            p21 = other.mapping[v1]
            p22 = other.mapping[v2]

            # check if the coordinates overlap
            if Scalar.tol_zero((p22 - p21).length):
                # coordinates overlap, so the merge is underconstrained
                underconstrained = True

                # calculate the homogenous coordinate system for the first
                # configuration using only the first shared point
                cs2 = make_hcs(p21, p21 + Vector(1.0, 0.0))
            else:
                # coordinates are different, so calculate the homogenous
                # coordinate system for the first configuration using the
                # vectors of the first two shared coordinates
                cs2 = make_hcs(p21, p22)

        # calculate the transformation matrix between the two homogenous
        # coordinate systems
        t = cs_transform_matrix(cs2, cs1)

        return t, underconstrained

    def __eq__(self, other):
        """Configuration equality operator

        Note that this does not just check if two configurations have variables
        with identical coordinates. Instead, two configurations are considered
        equal if they can be mapped on to one another by rotating one with
        respect to the other.
        """

        # FIXME: this contains code that is probably redundant - the hash value
        # will probably pick up a lot of the other checks

        if hash(self) != hash(other):
            # the hash value for configurations is based only on the variable
            # names, so if these differ then the configurations are definitely
            # different
            return False
        elif len(self.mapping) != len(other.mapping):
            # equal configurations would have the same number of variables
            return False
        else:
            # equal configurations would share the same variable names
            for var in self.mapping:
                if var not in other.mapping:
                    return False

            # determine the rotation-translation transformation to transform
            # the other configuration onto this one
            t, _ = self.transformation_matrix(other)

            # transform the other configuration
            other_t = other.transform(t)

            # test if the points map onto each
            for var in self.mapping:
                # calculate distance between the coordinates for the same
                # variable in each configuration
                d = distance_2p(other_t.get(var), self.get(var))

                # check if d is >0
                if not Scalar.tol_zero(d) and Scalar.tol_gt(d, 0):
                    return False

            # configurations are equal
            return True

    def makehash(self):
        """Calculate the hash that represents this configuration

        The hash is based only on variable names (not their coordinates)
        """

        self.hashvalue = hash(sum([hash(var) for var in self.mapping]))

    def __hash__(self):
        return self.hashvalue

    def __str__(self):
        return "Configuration({0})".format(self.mapping)

    def __repr__(self):
        return str(self)
