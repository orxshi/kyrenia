import sympy.geometry as symgeo

class AABB:
    """
    Construct axis-aligned bounding box.
    """
    def __init__(self, point, dim, r_min=None, r_max=None):
        """
        Construct AABB with given points.
        :param point: list of list of coordinates. example: [[1.5, 2.7], [4.1, 6.7], [7.5, 7.2]]
        """
        # initialize variables.
        # r_min[0]: x_min
        # r_min[1]: y_min
        # r_max[0]: x_max
        # r_max[1]: y_max

        if dim < 1 or dim > 3:
            raise ValueError('invalid dimension')

        self.dim = dim

        if r_min is not None and r_max is not None:
            self.r_min = r_min
            self.r_max = r_max
            for _ in dim:
                self.r.append(self.r_min[_])
                self.r.append(self.r_max[_])
        else:
            self.r = list()
            self.r_min = list()
            self.r_max = list()

            for _ in dim:
                self.r_min.append(1e6)
                self.r_max.append(-1e6)

            # loop through points to update variables.
            if point:
                for p in point:
                    for _ in dim:
                        self.r_min[_] = min(self.r_min[_], p[_])
                        self.r_max[_] = max(self.r_max[_], p[_])
                for _ in dim:
                    self.r.append(self.r_min[_])
                    self.r.append(self.r_max[_])

            else:
                raise ValueError('point is empty')

    def overlap(self, other):
        """
        Evaluate overlap of two AABBs.
        :param other:
        :return: False if no overlap.
                 True by default.
                 Error if dimensions do not match.
        """
        if self.dim != other.dim:
            return ValueError('dimensions do not match.')
        for d in self.dim:
            if self.r_min[d] > other.r_max[d]:  # self's left (bottom) edge is to the right (above) of other's right (top) edge.
                return False
            if self.r_max[d] < other.r_min[d]:  # self's right (top) edge is to the left (below) of other's left (bottom) edge.
                return False
        return True


class ADT:
    def __init__(self, dim, point):
        """
        :param dim:
        :param point: list of elements which holds list of points which holds list of coordinates. elements could be
        of any geometric shape.
        example: [[[1.5, 2.7], [4.1, 6.7], [7.5, 7.2]], [[1.5, 2.7], [4.1, 6.7], [7.5, 7.2]]]
        """
        self.dim = dim
        self.n_var = 2 * dim
        self.root = None

    def build(self, point):
        if self.root is None:
            root_aabb = AABB(point, self.dim)  # construct AABB of whole region.
            self.root = self.Node(level=0, key=None, adt_point=self.ADTPoint(point[0]), aabb=root_aabb)

            # insert the rest of the points to the tree.
            for p in point:
                child_dim = self.root.level % self.n_var
                self.insert(node=self.root, adt_point=self.ADTPoint(p), node_dim=child_dim)

    def insert(self, node, adt_point, node_dim):
        """
        Insert adt_point into one of the descendants of the node.
        :param node:
        :param adt_point:
        :param node_dim: one of the dimensions.
        :return: nothing.
        """
        # set level of the children.
        child_level = node.level + 1
        # the dimension at the children level.
        child_dim = child_level % self.n_var
        # the key for children.
        key = 0.5 * (adt_point.aabb.r_min[child_dim] + adt_point.aabb.r_max[child_dim])
        # set level of the grandchildren.
        grand_child_level = child_level + 1
        # the dimension at grandchildren level.
        grand_child_dim = grand_child_level % self.n_var

        if adt_point.aabb.r[node_dim] < node.key:
            if node.left is None:
                # set AABB of the region the child node represents.
                # set r_min
                r_min = node.aabb.r_min
                # set r_max
                r_max = list()
                for dim in self.n_var:
                    if dim != node_dim:
                        r_max[dim] = node.aabb.r_max
                    else:
                        r_max[dim] = key
                # pass r_min and r_max to node AABB.
                node_aabb = AABB(r_min, r_max, self.dim)
                # construct child node. adt_point is assigned to this child.
                node.left = self.Node(level=child_level, key=key, adt_point=adt_point, aabb=node_aabb)
            else:
                # insert adt_point into one of the descendants of the left child.
                self.insert(node=node.left, adt_point=adt_point, node_dim=grand_child_dim)
        else:
            if node.right is None:
                # set AABB of the region the child node represents.
                # set r_min
                r_max = node.aabb.r_max
                # set r_max
                r_min = list()
                for dim in self.n_var:
                    if dim != node_dim:
                        r_min[dim] = node.aabb.r_min
                    else:
                        r_min[dim] = key
                # pass r_min and r_max to node AABB.
                node_aabb = AABB(r_min, r_max, self.dim)
                # construct child node. adt_point is assigned to this child.
                node.right = self.Node(level=child_level, key=key, adt_point=adt_point, aabb=node_aabb)
            else:
                # insert adt_point into one of the descendants of the right child.
                self.insert(node=node.right, adt_point=adt_point, node_dim=grand_child_dim)

    def search_children(self, node, adt_point):
        """
        Evaluate overlap of AABB of node's children' and of adt_point. Add overlapping children to search_stack.
        :param node:
        :param adt_point:
        :return:
        """
        if node.left is not None:
            # check whether AABB of child and of adt_point overlap.
            if adt_point.aabb.overlap(self.node.left.aabb):
                self.search_stack.append(node.left)

        if node.right is not None:
            # check whether AABB of child and of adt_point overlap.
            if adt_point.aabb.overlap(self.node.right.aabb):
                self.search_stack.append(node.right)

    def search(self, node, adt_point):
        # check whether AABB of root and of adt_point overlap.
        if adt_point.aabb.overlap(self.root.aabb):
            self.search_(self.root, adt_point)

    def search_(self, node, adt_point):
        # check whether AABB of node's adt_point and adt_point of interest overlap.
        if adt_point.aabboverlap(node.adt_point.aabb):
            # check true overlap.
            if node.adt_point.true_overlap(adt_point):
                return True, node.adt_point.tag
            else:
                # keep searching children.
                self.search_children(node, adt_point)
                self.search_(self.search_stack.pop())
                # pop() removes and at the same time return the last element of search_stack.

    class Node:
        def __init__(self, level, key, adt_point, aabb):
            self.key = key
            self.left = None
            self.right = None
            self.level = level
            self.adt_point = adt_point
            self.aabb = aabb  # aabb of the region which this node represents.

    class ADTPoint:
        def __init__(self, point, tag):
            self.point = point
            self.tag = tag
            self.aabb = AABB(point, self.dim)  # aabb of the element.

        def true_overlap(self, other):
            # convert list: [[1,2], [3,4], [5,6]] to tuple: [(1,2), (3,4), (5,6)]
            point_tuple_self = list()
            for p in self.point:
                point_tuple_self.append(tuple(p))

            point_tuple_other = list()
            for p in other.point:
                point_tuple_other.append(tuple(p))

            poly_self = symgeo.Polygon(point_tuple_self)
            poly_other = symgeo.Polygon(point_tuple_other)

            return poly_self.intersection(poly_other)




