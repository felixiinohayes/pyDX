class DXObject:
    def __init__(self, objectid):
        self.objectid = objectid
        self.attributes = {}

    def add_attribute(self, attribute, target):
        self.attributes[attribute] = target


class Series(DXObject):
    def __init__(self, objectid, members):
        super().__init__(objectid)
        self.members = members


class Field(DXObject):
    def __init__(self, objectid):
        super().__init__(objectid)
        self.components = {}

    def add(self, component, name):
        self.components[name] = component


class GridPositions(DXObject):
    def __init__(self, objectid, origin, deltas, counts):
        super().__init__(objectid)
        self.origin = origin
        self.deltas = deltas
        self.counts = counts


class GridConnections(DXObject):
    def __init__(self, objectid, counts):
        super().__init__(objectid)
        self.counts = counts


class Array(DXObject):
    def __init__(self, objectid, data):
        super().__init__(objectid)
        self.data = data
