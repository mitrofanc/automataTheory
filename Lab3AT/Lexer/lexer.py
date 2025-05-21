import ply.lex as lex

tokens = [
    'TRUE', 'FALSE',
    'OCT_INT', 'DEC_INT', 'HEX_INT',
    'VAR', 'SIZE', 'LOGITIZE', 'DIGITIZE',
    'REDUCE', 'EXTEND',
    'MOVE', 'ROTATE', 'LEFT', 'RIGHT',
    'FOR', 'BOUNDARY', 'STEP',
    'SWITCH', 'TASK', 'DO', 'GET', 'RESULT', 'FINDEXIT',
    'PLEASE', 'THANKS', 'ENVIRONMENT',
    'NOT', 'AND', 'MXTRUE', 'MXFALSE',
    'MXEQ', 'MXLT', 'MXGT', 'MXLTE', 'MXGTE',
    'ELEQ', 'ELLT', 'ELGT', 'ELLTE', 'ELGTE',
    'IDENTIFIER', 'ASSIGN', 'PLUS', 'MINUS', 'MULT', 'DIV',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA'
]

t_ASSIGN   = r'='
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_MULT     = r'\*'
t_DIV      = r'/'
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA    = r','

t_ignore = ' \t\r'

reserved = {k: k for k in tokens if k.isupper() and k not in ('OCT_INT', 'DEC_INT', 'HEX_INT', 'IDENTIFIER')}

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.upper(), 'IDENTIFIER')
    return t

def t_HEX_INT(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    return t

def t_OCT_INT(t):
    r'0[0-7]+'
    t.value = int(t.value, 8)
    return t

def t_DEC_INT(t):
    r'[1-9][0-9]*'
    t.value = int(t.value)
    return t

def t_ZERO(t):
    r'0'
    t.value = 0
    t.type = 'DEC_INT'
    return t

def t_TRUE(t):
    r'TRUE'
    t.value = True
    return t

def t_FALSE(t):
    r'FALSE'
    t.value = False
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at line {t.lineno}")

lexer = lex.lex()
