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
    def __init__(self, token_class, subclass=None, value=None):
        self.token_class = token_class
        self.subclass = subclass
        self.value = value
    
    def __repr__(self):
        return f"Token({self.token_class}, {self.subclass}, {self.value})"
    

class FileReader:
    def __init__(self, filename):
        with open(filename, "r") as file:
            self.lines = file.readlines()[:50]
        self.current_line = 0
        self.kw_mapping = {kw.value: kw for kw in KW}

    def read_next_line(self):
        line = self.lines[self.current_line].strip()
        self.current_line += 1
        return line

    def tokenize(self, line):
        tokens = []
        words = line.split()
        for word in words:
            if word.isdigit():
                tokens.append(Token(TokenClass.NUMBER, NumberSubclass.INTEGER, int(word)))
            elif word in self.kw_mapping:
                tokens.append(Token(TokenClass.KEYWORD, None, self.kw_mapping[word]))
            elif is_float(word):
                tokens.append(Token(TokenClass.NUMBER, NumberSubclass.FLOAT, float(word)))
            elif word[0] == '"' and word[-1] == '"':
                tokens.append(Token(TokenClass.STRING, None, word))
            else:
                raise ValueError("Token not recognised as number or keyword.")
            print(tokens[-1])

    def parse(self):
        while self.current_line < len(self.lines):
            line = self.read_next_line()
            if line:
                tokens = self.tokenize(line)
                

def read_dx(filename: str) -> Field:
    reader = FileReader(filename)
    reader.parse()
    return Field() # insert parsed data as arguments

def main():
    field = read_dx("C10_TOP.dx")


if __name__ == "__main__":
    main()
