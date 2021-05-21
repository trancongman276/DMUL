import enum


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    ID = 2
    STRING = 3

    # keyword
    FUNC = 101
    EFU = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ELSE = 108
    EIF = 109
    WHILE = 110
    DO = 111
    EWH = 112
    SWITCH = 113
    INCASE = 114
    OTHERCASE = 115
    SO = 116
    ESO = 117
    ESW = 118
    FOR = 119
    START = 120
    WITHIN = 121
    EXEC = 122
    EFO = 123
    LOOP = 124
    UNTIL = 125
    CONST = 126

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
    QSM = 216 # ?
    SEPARATOR = 217 # ,
