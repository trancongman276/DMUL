from Token.tokentype import TokenType


class Token:
    def __init__(self, value, kind):
        self.value = value
        self.kind = kind

    @staticmethod
    def checktoken(tk):
        for kind in TokenType:
            if (kind.name == tk) and (100 <= kind.value < 200):
                return kind
        return None
