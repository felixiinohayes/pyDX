import numpy as np
from typing import List
from enum import Enum
from keywords import KW, TokenClass, Type

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        print(string)
        return False

class Field:
    def __init__(self):
        self.positions = None
        self.connections = None
        self.data = None


class Token:
    def __init__(self, token_class, type, value):
        self.token_class = token_class
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.token_class}, {self.subclass}, {self.value})"
    

class FileReader:
    def __init__(self, filename):
        self.filename = filename
        self.current_line = 0
        self.t = None
        self.token_generator = None
        self.kw_mapping = {kw.value: kw for kw in KW}
    

    # Increments the current token
    def next_token(self):
        try:
            self.t = next(self.token_generator)
            return self.t
        except StopIteration:
            self.t = None
            return None

    def tokenize(self, file):
        for line in file:
            self.current_line += 1

            words = line.split()
            for word in words:
                if word.isdigit():
                    yield Token(TokenClass.NUMBER, Type.INTEGER, int(word))
                elif word in self.kw_mapping:
                    yield Token(TokenClass.KEYWORD, None, self.kw_mapping[word])
                elif is_float(word):
                    yield Token(TokenClass.NUMBER, Type.FLOAT, float(word))
                elif word[0] == '"' and word[-1] == '"':
                    yield Token(TokenClass.STRING, None, word)
                else:
                    raise ValueError("Token not recognised as number or keyword.")

    def match_keyword(self, keyword):
        if (self.t.token_class == TokenClass.KEYWORD) & (self.t.value == keyword):
            return True
        else:
            raise ValueError(f"Line {self.current_line}: Expected keyword {keyword} but encountered other token.")

    def match_int(self):
        if (self.t.token_class == TokenClass.NUMBER) & (self.t.type == Type.INTEGER):
            return 
        else:
            raise ValueError(f"Line {self.current_line}: Expected integer but encountered other token.")

    def match_float(self):
        if (self.t.token_class == TokenClass.NUMBER) & (self.t.type == Type.FLOAT):
            return
        else:
            raise ValueError(f"Line {self.current_line}: Expected float but encountered other token.")

    def parse_sarray(self, kind):
        origin = []
        deltas = []
        counts = []
        rank = None

        self.next_token()
        self.match_keyword(KW.COUNTS)
        self.next_token()
        
        # Parse counts
        try:
            while True:
                self.match_int()
                counts.append(self.t.value)
                self.next_token()
        except ValueError:
            pass

        rank = len(counts)

        match kind:
            case KW.GRIDPOSITIONS:
                self.match_keyword(KW.ORIGIN)
                self.next_token()

                # Parse the origin
                for i in range(rank):
                    self.match_float()
                    origin.append(self.t.value)
                    self.next_token()

                # Parse the deltas (There will RANK number of deltas)
                for i in range(rank):
                    self.match_keyword(KW.DELTA)
                    self.next_token()
                    for j in range(rank):
                        self.match_float()
                        deltas.append(self.t.value)
                        self.next_token()
                
            case KW.GRIDCONNECTIONS:
                pass

    def parse_array(self):
        dtype = Type.FLOAT
        rank = None
        shape = None
        items = None

        done = False
        while not done:
            self.next_token()

            match self.t.value:
                case KW.TYPE:
                    self.next_token()
                    match self.t.value:
                        case KW.INTEGER:
                            type = Type.INTEGER
                        case KW.FLOAT:
                            type = Type.FLOAT
                        case KW.DOUBLE:
                            type = Type.DOUBLE
                        case KW.COMPLEX:
                            type = Type.COMPLEX
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
                            dim = tuple((items for _ in range(shape))) # Fix this to account for rank/shape/items
                            data = np.zeros(shape=dim, dtype=float)
                        case _: # todo: implement FILE, MODE, byteoffset cases
                            raise NotImplementedError("Follows keyword expected.")


    def parse_object(self):
        objnum = None

        self.next_token()

        self.match_int()
        objnum = self.t.value

        self.next_token()
        if self.t.value == KW.CLASS: # Skips the (optional) class keyword
            self.next_token()

        match self.t.value:
            case KW.GRIDPOSITIONS | KW.GRIDCONNECTIONS:
                self.parse_sarray(self.t.value)
            case KW.ARRAY:
                self.parse_array()


    def parse(self):
        with open(self.filename, "r") as file:
            self.token_generator = self.tokenize(file) # Initialize token generator

            i=0
            while i<10:
                # print(self.t)
                self.next_token()

                if self.t is None:
                    break

                match self.t.value:
                    case KW.OBJECT:
                        self.parse_object()
                i+=1


def read_dx(filename: str) -> Field:
    reader = FileReader(filename)
    reader.parse()
    return Field() # insert parsed data as arguments

def main():
    field = read_dx("C10_TOP.dx")


if __name__ == "__main__":
    main()