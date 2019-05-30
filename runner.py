import plex


class ParseError(Exception):
    pass


class RunError(Exception):
    pass


class myRunner:

    def __init__(self):
        DIGIT = plex.Range("09")
        BINARY_DIGIT = plex.Range("01")
        LETTER = plex.Range('azAZ')
        BINARY_TOKEN = plex.Rep1(BINARY_DIGIT)
        IDENTIFIER_TOKEN_OPERATOR = LETTER + plex.Rep(LETTER | DIGIT)
        AND_TOKEN = plex.Str("and")
        OR_TOKEN = plex.Str("or")
        XOR_TOKEN = plex.Str("xor")
        EQUALITY_OPERATOR = plex.Str("=")
        OPEN_PARENTHESES = plex.Str("(")
        CLOSE_PARENTHESES = plex.Str(")")
        PRINT_TOKEN = plex.Str("print")
        SPACE = plex.Any(" \n\t")

        self.LEXICON = plex.Lexicon([(SPACE, plex.IGNORE),
                                     (BINARY_TOKEN, "binary"),
                                     (AND_TOKEN, "and"),
                                     (OR_TOKEN, "or"),
                                     (XOR_TOKEN, "xor"),
                                     (EQUALITY_OPERATOR, "="),
                                     (PRINT_TOKEN, "print"),
                                     (OPEN_PARENTHESES, "("),
                                     (CLOSE_PARENTHESES, ")"),
                                     (IDENTIFIER_TOKEN_OPERATOR, "id")])

        self.ST = {}

    def create_scanner(self, fp):
        self.SCANNER = plex.Scanner(self.LEXICON, fp)
        self.LA, self.TEXT = self.next_token()

    def next_token(self):
        return self.SCANNER.read()

    def match(self, TOKEN):
        if self.LA == TOKEN:
            self.LA, self.TEXT = self.next_token()
        else:
            raise ParseError("self.LA not the same as token!")

    def run(self, fp):
        self.create_scanner(fp)
        self.stmt_list()

    def stmt_list(self):
        if self.LA in ("id", "print"):
            self.stmt()
            self.stmt_list()
        elif self.LA == None:
            return
        else:
            raise ParseError("Didnt get 'id' or 'print' token!")

    def stmt(self):
        if self.LA == "id":
            varname = self.TEXT
            self.match("id")
            self.match("=")
            self.ST[varname] = self.expr()
        elif self.LA == "print":
            self.match("print")
            print('{:b}'.format(self.expr()))
        else:
            raise ParseError("Didnt get what i was expecting!")

    def expr(self):
        if self.LA in ("(", "id", "binary"):
            t = self.term()
            while self.LA == "xor":
                self.match("xor")
                t2 = self.term()
                t ^= t2
            if self.LA in ("id", "print", ")", None):
                return t
            raise ParseError("Didn't get what i was expecting!")
        else:
            raise ParseError("Didnt get what i was expecting!")

    def term(self):
        if self.LA in ("(", "id", "binary"):
            f = self.atom()
            while self.LA == "or":
                self.match("or")
                f2 = self.atom()
                f |= f2
            if self.LA in ("xor", "id", "print", ")", None):
                return f
            raise ParseError("Didnt get what i was expecting!")
        else:
            raise ParseError("Didnt get what i was expecting!")

    def atom(self):
        if self.LA in ("(", "id", "binary"):
            f = self.factor()
            while self.LA == "and":
                self.match("and")
                f2 = self.factor()
                f += f2
            if self.LA in ("xor", "or", "id", "print", ")", None):
                return f
            raise ParseError("Didnt get what i was expecting!")
        else:
            raise ParseError("Didnt get what i was expecting!")

    def factor(self):
        if self.LA == "(":
            self.match("(")
            e = self.expr()
            self.match(")")
            return e
        elif self.LA == "id":
            varname = self.TEXT
            self.match("id")
            if varname in self.ST:
                return self.ST[varname]
            raise RunError("Didn't find the value in the Dictionary.")
        elif self.LA == "binary":
            value = int(self.TEXT, 2)
            self.match("binary")
            return value
        else:
            raise ParseError("Didnt get what i was expecting!")


runner = myRunner()
with open("testRunner.txt") as fp:
    runner.run(fp)