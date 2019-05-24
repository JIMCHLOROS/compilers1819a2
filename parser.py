import plex


class ParseError(Exception):
    pass


class myParser:
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

    def create_scanner(self, fp):
        self.SCANNER = plex.Scanner(self.LEXICON, fp)
        self.LA, self.TEXT = self.next_token()

    def next_token(self):
        return self.SCANNER.read()

    def match(self, token):
        if self.LA == token:
            self.LA, self.TEXT = self.next_token()
        else:
            raise ParseError("{} not the same as {}!".format(self.LA, token))

    def parse(self, fp):
        self.create_scanner(fp)
        self.stmt_list()

    def stmt_list(self):
        if self.LA in ("id", "print"):
            self.stmt()
            self.stmt_list()
        elif self.LA == None:
            return
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def stmt(self):
        if self.LA == "id":
            self.match("id")
            self.match("=")
            self.expr()
        elif self.LA == "print":
            self.match("print")
            self.expr()
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def expr(self):
        if self.LA in ("(", "id", "binary"):
            self.term()
            self.term_tail()
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def term_tail(self):
        if self.LA == "xor":
            self.match("xor")
            self.term()
            self.term_tail()
        elif self.LA in ("id", "print", ")", None):
            return
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def term(self):
        if self.LA in ("(", "id", "binary"):
            self.atom()
            self.atom_tail()
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def atom_tail(self):
        if self.LA == "or":
            self.match("or")
            self.atom()
            self.atom_tail()
        elif self.LA in ("xor", "id", "print", ")", None):
            return
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def atom(self):
        if self.LA in ("(", "id", "binary"):
            self.factor()
            self.factor_tail()
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def factor_tail(self):
        if self.LA == "and":
            self.match("and")
            self.factor()
            self.factor_tail()
        elif self.LA in ("xor", "or", "id", "print", ")", None):
            return
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))

    def factor(self):
        if self.LA == "(":
            self.match("(")
            self.expr()
            self.match(")")
        elif self.LA == "id":
            self.match("id")
        elif self.LA == "binary":
            self.match("binary")
        else:
            raise ParseError("{} was not what i was expecting!".format(self.LA))


parser = myParser()
with open("test.txt") as fp:
    parser.parse(fp)

"""
A -> ....By
    FOLLOW(B) <- FIRST(y)
A -> ....B
    FOLLOW(B) <- FOLLOW(A)
A -> ....By (<- y -> ε)
    FOLLOW(B) <- FOLLOW(A)
"""
