import ply.lex as lex

reserved = {
    'TRUE':  'BOOL_LITERAL',
    'FALSE': 'BOOL_LITERAL',

    'MXTRUE':  'MXTRUE',
    'MXFALSE': 'MXFALSE',
    'MXEQ':  'MXEQ',
    'MXLT':  'MXLT',
    'MXGT':  'MXGT',
    'MXLTE': 'MXLTE',
    'MXGTE': 'MXGTE',
    'ELEQ':  'ELEQ',
    'ELLT':  'ELLT',
    'ELGT':  'ELGT',
    'ELLTE': 'ELLTE',
    'ELGTE': 'ELGTE',

    'AND':   'AND',
    'NOT':   'NOT',

    'VAR':  'VAR',
    'TASK': 'TASK',
    'FOR':  'FOR',
    'BOUNDARY': 'BOUNDARY',
    'STEP': 'STEP',
    'SWITCH': 'SWITCH',
    'RESULT': 'RESULT',
    'MOVE': 'MOVE',
    'ROTATE': 'ROTATE',
    'LEFT': 'LEFT',
    'RIGHT': 'RIGHT',
    'GET': 'GET',
    'ENVIRONMENT': 'ENVIRONMENT',
    'SIZE': 'SIZE',
    'LOGITIZE': 'LOGITIZE',
    'DIGITIZE': 'DIGITIZE',
    'REDUCE': 'REDUCE',
    'EXTEND': 'EXTEND',
    'DO': 'DO',
}

tokens = [
    'PLUS', 'MINUS', 'MULT', 'DIV',
    'ASSIGN',
    'LBRACKET', 'RBRACKET',
    'LPAREN', 'RPAREN',
    'COMMA',
    'OCT_INT', 'DEC_INT', 'HEX_INT',
    'IDENTIFIER',
] + list(set(reserved.values()))

t_PLUS      = r'\+'
t_MINUS     = r'-'
t_MULT      = r'\*'
t_DIV       = r'/'
t_ASSIGN    = r'='
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r','

def t_HEX_INT(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    return t

def t_OCT_INT(t):
    r'0[oO]?[0-7]+'
    t.value = int(t.value, 8)
    return t

def t_DEC_INT(t):
    r'(0|[1-9][0-9]*)'
    t.value = int(t.value, 10)
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    upper = t.value.upper()
    t.type = reserved.get(upper, 'IDENTIFIER')
    if t.type == 'BOOL_LITERAL':
        t.value = True if upper == 'TRUE' else False
    return t

def t_comment(t):
    r'//.*'
    pass

t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at line {t.lineno}")

lexer = lex.lex()
