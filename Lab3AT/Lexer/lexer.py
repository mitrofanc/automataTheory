import ply.lex as lex

tokens = [
    'TRUE', 'FALSE',
    'OCT_INT', 'DEC_INT', 'HEX_INT',
    'VAR', 'SIZE', 'LOGITIZE', 'DIGITIZE',
    'REDUCE', 'EXTEND',
    'MOVE', 'ROTATE', 'LEFT', 'RIGHT',
    'FOR', 'BOUNDARY', 'STEP',
    'SWITCH', 'TASK', 'DO', 'GET', 'RESULT',
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

reserved = {
    'TRUE': 'TRUE',
    'FALSE': 'FALSE',
    'VAR': 'VAR',
    'SIZE': 'SIZE',
    'LOGITIZE': 'LOGITIZE',
    'DIGITIZE': 'DIGITIZE',
    'REDUCE': 'REDUCE',
    'EXTEND': 'EXTEND',
    'MOVE': 'MOVE',
    'ROTATE': 'ROTATE',
    'LEFT': 'LEFT',
    'RIGHT': 'RIGHT',
    'FOR': 'FOR',
    'BOUNDARY': 'BOUNDARY',
    'STEP': 'STEP',
    'SWITCH': 'SWITCH',
    'TASK': 'TASK',
    'DO': 'DO',
    'GET': 'GET',
    'RESULT': 'RESULT',
    'PLEASE': 'PLEASE',
    'THANKS': 'THANKS',
    'ENVIRONMENT': 'ENVIRONMENT',
    'NOT': 'NOT',
    'AND': 'AND',
    'MXTRUE': 'MXTRUE',
    'MXFALSE': 'MXFALSE'
}

t_MXEQ = r'MXEQ'
t_MXLT = r'MXLT'
t_MXGT = r'MXGT'
t_MXLTE = r'MXLTE'
t_MXGTE = r'MXGTE'

t_ELEQ = r'ELEQ'
t_ELLT = r'ELLT'
t_ELGT = r'ELGT'
t_ELLTE = r'ELLTE'
t_ELGTE = r'ELGTE'

t_NOT = r'NOT'
t_AND = r'AND'
t_MXTRUE = r'MXTRUE'
t_MXFALSE = r'MXFALSE'

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_HEX_INT(t):
    r'0x[0-9a-fA-F]+'
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

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at line {t.lineno}")

lexer = lex.lex()
