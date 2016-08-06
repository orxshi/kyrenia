import Geometry as Geometry


class Mesh:
    def __init__(self, file_name):
        self.point = list()  # list of points.
        self.cell = list()  # list of cells.
        self.bface = list()  # list of boundary faces.
        self.iface = list()  # list of interior faces.
        self.read_gmsh(file_name)
        self.topology_connectivity()

    def read_gmsh(self, file_name):
        """
        Read mesh from a file generated by GMSH. Call in __init__.

        :param filename: name of file to read grid from. it comes from __init__. (default=None)
        :type filename: str
        :rtype: None
        """
        with open(file_name, 'r') as f:
            # read number of points
            for line in f:
                if '$Nodes' in line:
                    np = int(next(f))
                    break
            # read points
            for _ in range(np):
                a = []  # dummy list
                for token in next(f).split():  # split coordinates.
                    a.append(float(token))
                self.point.append(Point(a[1:], self))  # ignoring first char.
            # read number of elements
            for line in f:
                if '$Elements' in line:
                    ne = int(next(f))
                    break
            # read elements
            for i in range(ne):
                a = list()  # dummy list
                # a[0] refers to tag.
                # a[1] refers to geometric shape.
                # a[2] refers to number of tags.
                # according to number of tags:
                # a[3] refers to physical tag.
                # a[4] refers to geometric tag.
                # a[5] refers to number of partitions.
                # according to number of partitions:
                # a[...] refers to partitions.
                # the rest refers to vertices.
                for token in next(f).split():
                    a.append(int(token))
                if a[1] == 15:  # point
                    pass
                elif a[1] == 1:  # line
                    # read last two entries.
                    point = list()
                    point.append(self.point[a[-2] - 1])  # -1 because GMSH has base 1.
                    point.append(self.point[a[-1] - 1])  # -1 because GMSH has base 1.
                    wall = False  # so adjust physical number accordingly when creating GMSH file.
                    if a[3] == 1:
                        wall = True
                    self.bface.append(BoundaryFace(Geometry.Line([shape for shape in point]), point, wall, self))
                elif a[1] == 3:  # quad
                    # read last four entries.
                    point = list()
                    point.append(self.point[a[-4] - 1])  # -1 because GMSH has base 1.
                    point.append(self.point[a[-3] - 1])  # -1 because GMSH has base 1.
                    point.append(self.point[a[-2] - 1])  # -1 because GMSH has base 1.
                    point.append(self.point[a[-1] - 1])  # -1 because GMSH has base 1.
                    self.cell.append(Cell(Geometry.Quad([shape for shape in point]), point, self))

    def print_vtk(self, file_name):
        """
        Write mesh to a file in vtk format.

        :param file_name: name of file to write.
        :return: vtk file
        """

        f = open(file_name, 'w')

        f.write('# vtk DataFile Version 3.0\n')
        f.write('All in VTK format\n')
        f.write('ASCII\n')
        f.write('DATASET UNSTRUCTURED_GRID\n')
        f.write('POINTS %i float\n' % len(self.point))

        # write points
        for p in self.point:
            for i in p.shape.coor:
                f.write('%s ' % i)
            f.write('\n')

        # write cell list size
        celllistsize = 0
        for i in self.cell:
            celllistsize += i.shape.n_vertex + 1
        f.write('CELLS %i %i\n' % (len(self.cell), celllistsize))

        # write cell vertices
        for i in self.cell:
            f.write('%s ' % i.shape.n_vertex)
            for v in i.point:
                f.write('%s ' % self.point.index(v))
            f.write('\n')

        # write cell types
        f.write('CELL_TYPES %i\n' % len(self.cell))
        for cell in self.cell:
            if isinstance(cell.shape, Geometry.Quad):  # check if cell shape is quad.
                f.write('%i\n' % 9)

    def topology_connectivity(self):
        """
        Establish cell-to-cell, face-to-cell connectivity of mesh. Create interior faces.
        :return:
        """
        # loop through cells.
        for cell in self.cell:
            faces = cell.set_face_vertices()
            # loop through points of faces.
            # note that 'faces' is not assigned to the cell yet.
            for face in faces:
                if face[0].parent_bface:  # needed to use continue statement.
                    # loop though bfaces that the first face vertex belongs to.
                    for parent_bface in face[0].parent_bface:  # face[0] is the first face vertex.
                        # count number of parent bfaces other points of the face belongs to.
                        sig = 0
                        for point in face[1:]:  # do not consider the first face point.
                            if parent_bface in point.parent_bface:
                                sig += 1
                        if sig == len(face) - 1:  # '-1' because we start from the second vertex to count matches.
                            cell.bface.append(parent_bface)
                            parent_bface.parent_cell.append(cell)
                            break  # looping though bfaces of the first face vertex.
                    continue  # with the next face as we are done with the current one.

                # loop through parent cells of the face vertex.
                for parent_cell in face[0].parent_cell:
                    # make sure that parent cell is not the current cell.
                    if parent_cell != cell:
                        # check if this parent cell is already processed.
                        if parent_cell not in cell.nei:
                            sig = 0
                            for point in face[1:]:  # do not consider the first face point.
                                sig += point.parent_cell.count(parent_cell)
                            if sig == len(face) - 1:  # '-1' because we start from the second vertex to count matches.
                                cell.nei.append(parent_cell)
                                parent_cell.nei.append(cell)
                                if isinstance(cell.shape, Geometry.Quad):
                                    shape = Geometry.Line
                                self.iface.append(InteriorFace(shape, face, self))
                                cell.iface.append(self.iface[-1])
                                parent_cell.iface.append(self.iface[-1])
                                break  # looping though parent cells of the first face vertex.


class Face:
    def __init__(self, shape, point, parent_mesh):
        self.shape = shape  # the geometric shape of the face.
        self.parent_mesh = parent_mesh  # the mesh to which face belongs to.
        self.parent_cell = list()  # the cell to which face belongs to.
        self.point = point  # list of face vertices.

    def __eq__(self, other):
        return self.point == other.point


class BoundaryFace(Face):
    def __init__(self, shape, point, wall, parent_mesh):
        self.wall = wall  # boolean to indicate whether boundary face is a wall.
        # set this boundary face as parent of its vertices.
        for p in point:
            if p.parent_bface is not None:
                p.parent_bface.append(self)
        super(BoundaryFace, self).__init__(shape, point, parent_mesh)


class InteriorFace(Face):
    def __init__(self, shape, point, parent_mesh):
        # set this interior face as parent of its vertices.
        for p in point:
            if p.parent_iface is not None:
                p.parent_iface.append(self)
        super(InteriorFace, self).__init__(shape, point, parent_mesh)


class Cell:
    def __init__(self, shape, point, parent_mesh):
        self.parent_mesh = parent_mesh  # the mesh to which the cell belongs to.
        self.shape = shape  # geometric shape of the cell.
        self.point = point  # list of cell vertices.
        self.bface = list()  # list of cell boundary faces if any.
        self.iface = list()  # list of cell interior faces.
        self.nei = list()  # list of cell neighbors.
        # set this cell as parent of its vertices.
        for p in point:
            if p.parent_cell is not None:
                p.parent_cell.append(self)

    def __eq__(self, other):
        return self.point == other.point

    def set_face_vertices(self):
        """
        Determine vertices of cell faces with GMSH convention.
        Do not modify cell faces but returns a new list.
        :return:
        """
        faces = list()  # list of faces which holds lists of vertices.
        if isinstance(self.shape, Geometry.Quad):
            face = list()  # list of vertices.
            face.append(self.point[0])
            face.append(self.point[1])
            faces.append(face)

            face = list()
            face.append(self.point[1])
            face.append(self.point[2])

            face = list()
            face.append(self.point[2])
            face.append(self.point[3])

            face = list()
            face.append(self.point[3])
            face.append(self.point[0])

            return faces

        return None


class Point:
    def __init__(self, coor, parent_mesh):
        self.shape = Geometry.Point(coor)  # geometric shape.
        self.parent_mesh = parent_mesh  # the mesh to which point belongs to.
        self.parent_cell = list()  # the cell to which point belongs to.
        self.parent_bface = list()  # the boundary face to which point belongs to if any.
        self.parent_iface = list()  # the interior face to which point belongs to if any.

    def __eq__(self, other):
        return self.shape.coor == other.shape.coor















