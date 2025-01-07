from enum import Enum, auto

class KW(Enum):
    OBJECT = "object"
    CLASS = "class"
    END = "end"
    DATA = "data"
    COMPONENT = "component"
    DELTA = "delta"
    COUNTS = "counts"
    GRIDPOSITIONS = "gridpositions"
    GRIDCONNECTIONS = "gridconnections"
    TYPE = "type"
    FLOAT = "float"
    INTEGER = "integer"
    DOUBLE = "double"
    COMPLEX = "complex"
    RANK = "rank"
    SHAPE = "shape"
    ITEM = "item"
    FOLLOWS = "follows"
    ATTRIBUTE = "attribute"
    ORIGIN = "origin"
    STRING = "string"
    ARRAY = "array"
    FIELD = "field"
    VALUE = "value"
    SERIES = "series"
    MEMBER = "member"
    POSITION = "position"

class TokenClass(Enum):
    NUMBER = auto()
    KEYWORD = auto()
    STRING = auto()

class Type(Enum):
    INTEGER = auto()
    FLOAT = auto()
    DOUBLE = auto()
    COMPLEX = auto()
