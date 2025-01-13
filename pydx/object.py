from dataclasses import dataclass

# TODO: Figure out class hierarchies
class DXObject:
    def __init__(self, objectid):
        self.objectid = objectid
        self.attributes = {}

    def set_attribute(self, name, value):
        self.attributes[name] = value

@dataclass
class GroupMember:
    value: DXObject
    position: int


class Group(DXObject):
    def __init__(self, objectid):
        super().__init__(objectid)
        self.members = []
    

class Series(Group):
    def __init__(self, objectid):
        super().__init__(objectid)

    def add_member(self, value, position):
        self.members.append(GroupMember(value=value, position=position))



class Field(DXObject):
    def __init__(self, objectid):
        super().__init__(objectid)
        self.components = {}

    def add_component(self, name, value):
        self.components[name] = value

    def __repr__(self):
        return f"Field(components: {len(self.components)})"


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
