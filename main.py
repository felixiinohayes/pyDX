import numpy as np
from typing import List
from enum import Enum
from keywords import KW, TokenClass, Type

def _is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def _is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

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


class DXObject:
    def __init__(self, objectid):
        self.objectid = objectid
        self.attributes = {}

    def add_attribute(self, attribute, target):
        self.attributes[attribute] = target


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


class Token:
    def __init__(self, token_class, type, value):
        self.token_class = token_class
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.token_class}, {self.type}, {self.value})"


class FileReader:
    def __init__(self, filename):
        self.filename = filename
        self.current_line = 0
        self.t = None
        self.token_generator = None
        self.kw_mapping = {kw.value: kw for kw in KW}

        self.currentid = None
        self.components = {}
        self.fields = {}
        self.series_members = {}
        self.series = None
        self.rank = None

    # Increments the current token
    def next_token(self):
        try:
            self.t = next(self.token_generator)
            return self.t
        except StopIteration:
            self.t = None
            return None

    def tokenize(self, file):
        in_string = False
        current_string = []

        for line in file:
            self.current_line += 1

            words = line.split()
            for word in words:
                if not in_string:
                    if is_int(word):
                        yield Token(TokenClass.NUMBER, Type.INTEGER, int(word))
                    elif is_float(word):
                        yield Token(TokenClass.NUMBER, Type.FLOAT, float(word))
                    elif word in self.kw_mapping:
                        yield Token(TokenClass.KEYWORD, None, self.kw_mapping[word])
                    elif word.startswith('"') and word.endswith('"'):
                        yield Token(TokenClass.STRING, None, word[1:-1])
                    elif word.startswith('"') and not word.endswith('"'):
                        in_string = True
                        current_string.append(word[1:])
                    else:
                        raise ValueError("Token not recognised as number or keyword.")
                else:
                    if word.endswith('"'):
                        in_string = False
                        current_string.append(word[:-1])
                        full_string = " ".join(current_string)
                        current_string = []
                        yield Token(TokenClass.STRING, None, full_string)
                    else:
                        current_string.append(word)

    def match_keyword(self, keyword) -> bool:
        return (self.t.token_class == TokenClass.KEYWORD) & (self.t.value == keyword)

    def match_int(self) -> bool:
        return (self.t.token_class == TokenClass.NUMBER) & (self.t.type == Type.INTEGER)

    def match_float(self) -> bool:
        return (self.t.token_class == TokenClass.NUMBER) & (self.t.type == Type.FLOAT)

    def match_string(self) -> bool:
        return self.t.token_class == TokenClass.STRING

    def parse_series(self):

        while True:
            self.next_token()
            if not self.match_keyword(KW.MEMBER):
                break

            member = []
            self.next_token()
            if self.match_int():
                member.append(self.t.value)
            else:
                raise ValueError("Series member id must be integer.")

            self.next_token()
            if not self.match_keyword(KW.VALUE):
                raise ValueError("Expected value keyword in series definition.")

            self.next_token()
            if self.match_int():
                member.append(self.t.value)
            else:
                raise ValueError("Series member id must be integer.")

            self.next_token()
            if not self.match_keyword(KW.POSITION):
                raise ValueError("Expected position keyword in series definition.")

            self.next_token()
            if self.match_int():
                member.append(self.t.value)
            else:
                raise ValueError("Series member id must be integer.")

            self.series_members[member[0]] = (self.fields[member[1]], member[2])
        self.series = Series(self.currentid, self.series_members)

    def parse_field(self):
        f = Field(self.currentid)
        name = ""
        while True:
            self.next_token()
            if not (self.match_keyword(KW.COMPONENT) or self.match_keyword(KW.ATTRIBUTE)):
                break

            self.next_token()
            if self.match_string:
                name = self.t.value
            else:
                raise ValueError("Component name must be string.")

            self.next_token()
            self.next_token()
            if self.match_int or self.match_string:
                if self.t.value in self.components:
                    f.add(self.components[self.t.value], name)
                else:
                    raise ValueError("Component value not in object list.")
            else:
                raise ValueError("Component value must be int or string.")
        self.fields[self.currentid] = f


    def parse_grid(self, kind):
        origin = []
        deltas = []
        counts = []
        rank = None

        self.next_token()
        self.match_keyword(KW.COUNTS)

        self.next_token()
        match kind:
            case KW.GRIDPOSITIONS:
                # Parse counts
                while True:
                    if self.match_int():
                        counts.append(self.t.value)
                        self.next_token()
                    else:
                        break

                rank = len(counts)
                self.rank = rank

                if not self.match_keyword(KW.ORIGIN):
                    raise ValueError(f"Line {self.current_line}: Expected keyword {KW.ORIGIN} but encountered other token.")

                self.next_token()
                # Parse the origin
                for i in range(rank):
                    if self.match_float():
                        origin.append(self.t.value)
                    else:
                        raise ValueError(f"Line {self.current_line}: Expected float but encountered other token.")
                    self.next_token()
                    
                # Parse the deltas (There will RANK number of deltas)
                for i in range(rank):
                    if self.match_keyword(KW.DELTA):
                        self.next_token()

                        deltatemp = []
                        for j in range(rank):
                            if self.match_float():
                                deltatemp.append(self.t.value)
                            else:
                                raise ValueError(f"Line {self.current_line}: Expected float but encountered other token.")
                            self.next_token()
                        deltas.append(deltatemp)
                    else:
                        raise ValueError(f"Line {self.current_line}: Expected keyword {KW.DELTA} but encountered other token.")
                self.components[self.currentid] = GridPositions(self.currentid, origin, deltas, counts)

            case KW.GRIDCONNECTIONS:
                # Parse counts
                for i in range(self.rank):
                    if self.match_int():
                        counts.append(self.t.value)
                    else:
                        raise ValueError("Non integer encountered in connection counts.")
                    self.next_token()

                self.components[self.currentid] = GridConnections(self.currentid, counts)
                pass

    def parse_array(self):
        dtype = Type.FLOAT
        rank = None
        shape = None
        items = None

        while True:
            self.next_token()

            match self.t.value:
                case KW.TYPE:
                    self.next_token()
                    match self.t.value:
                        case KW.INTEGER:
                            dtype = Type.INTEGER
                        case KW.FLOAT:
                            dtype = Type.FLOAT
                        case KW.DOUBLE:
                            dtype = Type.DOUBLE
                        case KW.COMPLEX:
                            dtype = Type.COMPLEX
                        case _:
                            raise ValueError("Incorrect type keyword encountered.")
                case KW.RANK:
                    self.next_token()
                    self.match_int()
                    rank = self.t.value
                case KW.SHAPE:
                    self.next_token()
                    self.match_int()
                    shape = self.t.value
                case KW.ITEM:
                    self.next_token()
                    self.match_int()
                    items = self.t.value
                case KW.DATA:
                    self.next_token()
                    match self.t.value:
                        case KW.FOLLOWS:
                            dim = (shape, items)
                            data = self.read_array(dim, dtype)
                            self.components[self.currentid] = Array(self.currentid, data)
                        case _: # todo: implement FILE, MODE, byteoffset cases
                            raise NotImplementedError("Follows keyword expected.")
                case KW.ATTRIBUTE:
                    self.next_token()
                    att_name = ""
                    if self.match_string():
                        att_name = self.t.value
                    else:
                        raise ValueError("Expected string after attribute keyword.")

                    self.next_token()
                    if not self.match_keyword(KW.STRING): raise ValueError("Expected string keyword.")

                    target = ""
                    self.next_token()
                    if self.match_string():
                        target = self.t.value
                    else:
                        raise ValueError("Expected string after attribute keyword.")
                    self.components[self.currentid].add_attribute(att_name, target)
                case _:
                    break

    def read_array(self, dim, dtype):
        total_elements = np.prod(dim)
        data_flat = np.zeros(total_elements, dtype=float)
        reading = True
        for i in range(total_elements):
            self.next_token()
            if self.t.type == dtype:
                data_flat[i] = self.t.value
            else:
                raise ValueError("Unexpected dtype found while parsing array.")
        data = np.reshape(data_flat, dim)
        return data

    def parse_object(self):
        self.next_token()

        if self.match_int() or self.t.token_class == TokenClass.STRING:
            self.currentid = self.t.value
        else:
            raise ValueError("Need to define object id as int or string.")

        self.next_token()
        if self.t.value == KW.CLASS: # Skips the (optional) class keyword
            self.next_token()

        match self.t.value:
            case KW.GRIDPOSITIONS | KW.GRIDCONNECTIONS:
                self.parse_grid(self.t.value)
            case KW.ARRAY:
                self.parse_array()
            case KW.FIELD:
                self.parse_field()
            case KW.SERIES:
                self.parse_series()
            case _:
                raise ValueError("Only array, gridpos, gridcon classes supported.")


    def parse(self):
        with open(self.filename, "r") as file:
            self.token_generator = self.tokenize(file) # Initialize token generator
            self.next_token()

            while True:
                # print("parse", self.t.value)
                if self.t is None or self.t.value == KW.END:
                    break

                match self.t.value:
                    case KW.OBJECT:
                        self.parse_object()

            if self.series:
                return self.series
            else:
                return self.fields


def read_dx(filename: str):
    reader = FileReader(filename)
    return reader.parse()

if __name__ == "__main__":
    data = read_dx("testfiles/test1dseries.dx")
