import numpy as np
from typing import List
from enum import Enum
from keywords import KW, TokenClass, Type

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


class Field:
    def __init__(self):
        self.components = {}

    def add(self, component, name):
        self.components[name] = component


class GridPositions:
    def __init__(self, objectid, origin, deltas, counts):
        self.objectid = objectid
        self.origin = origin
        self.deltas = deltas
        self.counts = counts


class GridConnections:
    def __init__(self, objectid, counts):
        self.objectid = objectid
        self.counts = counts


class Array:
    def __init__(self, objectid, data):
        self.objectid = objectid
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
        self.objectids = []
        self.currentid = None
        self.components = {}
        self.fields = {}
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

    def parse_field(self):
        print("field")
        f = Field()
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
                            if not (i == rank - 1 and j == rank - 1): self.next_token()
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
                    if i < self.rank - 1: self.next_token()

                self.components[self.currentid] = GridConnections(self.currentid, counts)
                pass

    def parse_array(self):
        dtype = Type.FLOAT
        rank = None
        shape = None
        items = None
        print("array")

        done = False
        while not done:
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
                            break
                        case _: # todo: implement FILE, MODE, byteoffset cases
                            raise NotImplementedError("Follows keyword expected.")
                case KW.ATTRIBUTE:
                    # todo
                    pass
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
        print("object")
        self.next_token()

        if self.match_int() or self.t.token_class == TokenClass.STRING:
            self.objectids.append(self.t.value)
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
            case _:
                raise ValueError("Only array, gridpos, gridcon classes supported.")


    def parse(self):
        with open(self.filename, "r") as file:
            self.token_generator = self.tokenize(file) # Initialize token generator
            self.next_token()

            while True:
                # print("parse", self.t.value)
                if self.t is None:
                    break

                match self.t.value:
                    case KW.OBJECT:
                        self.parse_object()
                self.next_token()

            print(self.components)
            print(self.fields)
            # print(self.fields[''].components['data'].data)


def read_dx(filename: str) -> Field:
    reader = FileReader(filename)
    reader.parse()
    return Field() # insert parsed data as arguments

def main():
    field = read_dx("testfiles/test1d.dx")


if __name__ == "__main__":
    main()
