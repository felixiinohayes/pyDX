import numpy as np
from typing import List
from enum import Enum
from keywords import KW, TokenClass, NumberSubclass

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
    def __init__(self, token_class, subclass, value):
        self.token_class = token_class
        self.subclass = subclass
        self.value = value
    
    def __repr__(self):
        return f"Token({self.token_class}, {self.subclass}, {self.value})"
    

class FileReader:
    def __init__(self, filename):
        self.filename = filename
        self.current_line = 0
        self.t: Token = None
        self.token_generator = None
        self.kw_mapping = {kw.value: kw for kw in KW}
    
    def tokenize(self, file):
        for line in file:
            self.current_line += 1

            words = line.split()
            for word in words:
                if word.isdigit():
                    yield Token(TokenClass.NUMBER, NumberSubclass.INTEGER, int(word))
                elif word in self.kw_mapping:
                    yield Token(TokenClass.KEYWORD, None, self.kw_mapping[word])
                elif is_float(word):
                    yield Token(TokenClass.NUMBER, NumberSubclass.FLOAT, float(word))
                elif word[0] == '"' and word[-1] == '"':
                    yield Token(TokenClass.STRING, None, word)
                else:
                    raise ValueError("Token not recognised as number or keyword.")

    def parse_sarray(self, kind):
        origin = None
        deltas = None
        counts = 0


    def parse_object(self):
        objnum = None

        self.next_token()
        if self.t.token_class == TokenClass.NUMBER:
            objnum = self.t.value
        self.next_token()
        self.next_token()

        match self.t.value:
            case KW.GRIDPOSITIONS | KW.GRIDCONNECTIONS:
                self.parse_sarray(self.t.value)


    def next_token(self):
        try:
            self.t = next(self.token_generator)
            return self.t
        except StopIteration:
            self.t = None
            return None

    def parse(self):
        with open(self.filename, "r") as file:
            self.token_generator = self.tokenize(file)

            while True:
                self.next_token()

                if self.t is None:
                    break

                match self.t.value:
                    case KW.OBJECT:
                        self.parse_object()
                print(self.t)



                

def read_dx(filename: str) -> Field:
    reader = FileReader(filename)
    reader.parse()
    return Field() # insert parsed data as arguments

def main():
    field = read_dx("C10_TOP.dx")


if __name__ == "__main__":
    main()
