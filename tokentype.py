import enum


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    ID = 2
    STRING = 3

    # keyword
    LABEL = 101
    PRINT = 102
    INPUT = 103
    LET = 104
    IF = 105
    THEN = 106
    ELSE = 107
    EF = 108
    WHILE = 109
    DO = 110
    EW = 112
    GOTO = 113

    # OPERATOR
    EQ = 201  # =
    MINUS = 202  # -
    PLUS = 203  # +
    STAR = 204  # *
    SLASH = 205  # /
    EQEQ = 206  # ==
    NOTEQ = 207  # !=
    GEQ = 208  # >=
    LEQ = 209  # <=
    LT = 210  # <
    GT = 211  # >
    PEQ = 212 # +=
    MEQ = 213 # -=
    OBRACKET = 214 # (
    CBRACKET = 215 # )
