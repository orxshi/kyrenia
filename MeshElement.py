import Geometry as Geometry


class Face:
    def __init__(self, shape, point, parent_mesh, parent_cell, tag):
        self.tag = tag
        self.shape = shape
        self.parent_mesh = parent_mesh
        self.parent_cell = parent_cell
        self.point = point


class BoundaryFace(Face):
    def __init__(self, shape, point, wall, parent_mesh, tag, parent_cell=None):
        self.wall = wall
        for p in point:
            if p.parent_bface is not None:
                p.parent_bface.append(self)
        super(BoundaryFace, self).__init__(shape, point, parent_mesh, parent_cell, tag)


class InteriorFace(Face):
    def __init__(self, shape, point, parent_mesh, tag, parent_cell=None):
        for p in point:
            if p.parent_iface is not None:
                p.parent_iface.append(self)
        super(InteriorFace, self).__init__(shape, point, parent_mesh, parent_cell, tag)


class Cell:
    def __init__(self, shape, point, parent_mesh, tag):
        self.tag = tag
        self.parent_mesh = parent_mesh
        self.shape = shape
        self.point = point
        self.bface = list()
        self.iface = list()
        for p in point:
            if p.parent_cell is not None:
                p.parent_cell.append(self)


    def set_face_vertices(self):
        """
        Determine vertices of faces of the cell with GMSH convention.
        :return:
        """
        faces = list()  # list of faces which holds lists of vertices.
        if isinstance(self.shape, Geometry.Quad):
            face = list()
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
    def __init__(self, coor, parent_mesh, tag, parent_cell=None, parent_bface=None, parent_iface=None):
        self.tag = tag
        self.shape = Geometry.Point(coor)
        self.parent_mesh = parent_mesh
        self.parent_cell = parent_cell
        self.parent_bface = parent_bface
        self.parent_iface = parent_iface

