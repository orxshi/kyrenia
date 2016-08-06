class Shape:
    def __init__(self, n_vertex, point):
        self.n_vertex = n_vertex
        self.point = point


class Quad(Shape):
    def __init__(self, point):
        self.n_vertex = 4
        self.n_face = 4
        super(Quad, self).__init__(self.n_vertex, point=point)


class Point:
    def __init__(self, coor):
        self.coor = coor


class Line(Shape):
    def __init__(self, point):
        self.n_vertex = 2
        super(Line, self).__init__(self.n_vertex, point=point)