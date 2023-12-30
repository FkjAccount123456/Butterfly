from enum import Enum, unique


@unique
class TokenType(Enum):
    EOF = 0
    # Operators
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    MOD = 5
    EQ = 6
    NE = 7
    GT = 8
    LT = 9
    GE = 10
    LE = 11
    LSH = 12
    RSH = 13
    AND = 14
    OR = 15
    BITAND = 16
    BITOR = 17
    XOR = 18
    NOT = 19
    INV = 20
    # Other symbols
    LPAREN = 100
    RPAREN = 101
    LSQBR = 102
    RSQBR = 103
    BEGIN = 104
    END = 105
    COMMA = 106
    COLON = 107
    DOT = 108
    SEMICOLON = 109
    # Keywords
    K_IF = 200
    K_ELSE = 201
    K_WHILE = 202
    K_VAR = 203
    K_FUNC = 204
    K_RETURN = 205
    K_BREAK = 206
    K_CONTINUE = 207
    # Others
    IDENT = 300
    CONST = 301


op_map = {
    '+': TokenType.ADD,
    '-': TokenType.SUB,
    '*': TokenType.MUL,
    '/': TokenType.DIV,
    '%': TokenType.MOD,
    '==': TokenType.EQ,
    '!=': TokenType.NE,
    '>': TokenType.GT,
    '<': TokenType.LT,
    '>=': TokenType.GE,
    '<=': TokenType.LE,
    '<<': TokenType.LSH,
    '>>': TokenType.RSH,
    '&&': TokenType.AND,
    '||': TokenType.OR,
    '&': TokenType.BITAND,
    '|': TokenType.OR,
    '^': TokenType.XOR,
    '!': TokenType.NOT,
    '~': TokenType.INV,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '[': TokenType.LSQBR,
    ']': TokenType.RSQBR,
    '{': TokenType.BEGIN,
    '}': TokenType.END,
    ',': TokenType.COMMA,
    ':': TokenType.COLON,
    '.': TokenType.DOT,
    ';': TokenType.SEMICOLON,
}

keyword_map = {
    'if': TokenType.K_IF,
    'else': TokenType.K_ELSE,
    'while': TokenType.K_WHILE,
    'var': TokenType.K_VAR,
    'func': TokenType.K_FUNC,
    'return': TokenType.K_RETURN,
    'break': TokenType.K_BREAK,
    'continue': TokenType.K_CONTINUE,
}

prio_map = {
    TokenType.MUL: 100,
    TokenType.DIV: 100,
    TokenType.MOD: 100,
    TokenType.ADD: 99,
    TokenType.SUB: 99,
    TokenType.LSH: 98,
    TokenType.RSH: 98,
    TokenType.EQ: 97,
    TokenType.NE: 97,
    TokenType.GT: 96,
    TokenType.LT: 96,
    TokenType.GE: 96,
    TokenType.LE: 96,
    TokenType.BITAND: 95,
    TokenType.XOR: 94,
    TokenType.BITOR: 93,
    TokenType.AND: 92,
    TokenType.OR: 91,
}

escape_map = {
    'r': '\r',
    't': '\t',
    'a': '\a',
    'f': '\f',
    'v': '\v',
    'b': '\b',
    'n': '\n',
    '"': '"',
    '\'': '\'',
    '\\': '\\',
}
