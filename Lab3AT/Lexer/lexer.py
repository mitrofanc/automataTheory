import ply.lex as lex

tokens = [
    # Логические литералы
    'TRUE',
    'FALSE',

    # Целочисленные литералы в 3 форматах
    'OCT_INT',
    'DEC_INT',
    'HEX_INT',

    # Переменные VAR
    'VAR',
    'IDENTIFIER',

    # Размерности в квадратных скобках и запятые
    'LBRACKET', 'RBRACKET', 'COMMA',

    # Операторы
    'ASSIGN',

    # Арифметические операторы
    'PLUS', 'MINUS', 'MULT', 'DIV',

    # Логические операторы
    'NOT', 'AND', 'MXTRUE', 'MXFALSE',

    # Операторы сравнения
    'MXEQ', 'MXLT', 'MXGT', 'MXLTE', 'MXGTE',
    'ELEQ', 'ELLT', 'ELGT', 'ELLTE', 'ELGTE',

    # Операторы управления роботом и язык
    'MOVE', 'ROTATE', 'LEFT', 'RIGHT',
    'FOR', 'BOUNDARY', 'STEP',
    'SWITCH',
    'TASK', 'DO', 'GET', 'RESULT', 'FINDEXIT',
    'PLEASE', 'THANKS',

    # Новые ключевые слова/операторы из задания
    'SIZE',
    'LOGITIZE',
    'DIGITIZE',
    'REDUCE',
    'EXTEND',
    'ENVIRONMENT',

    # Скобки
    'LPAREN', 'RPAREN',
]

# Регулярные выражения для простых символов
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_ignore = ' \t\r'

reserved_map = {
    'VAR': 'VAR',
    'TRUE': 'TRUE',
    'FALSE': 'FALSE',
    'NOT': 'NOT',
    'AND': 'AND',
    'MXTRUE': 'MXTRUE',
    'MXFALSE': 'MXFALSE',

    'MXEQ': 'MXEQ',
    'MXLT': 'MXLT',
    'MXGT': 'MXGT',
    'MXLTE': 'MXLTE',
    'MXGTE': 'MXGTE',

    'ELEQ': 'ELEQ',
    'ELLT': 'ELLT',
    'ELGT': 'ELGT',
    'ELLTE': 'ELLTE',
    'ELGTE': 'ELGTE',

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
    'FINDEXIT': 'FINDEXIT',
    'PLEASE': 'PLEASE',
    'THANKS': 'THANKS',

    'SIZE': 'SIZE',
    'LOGITIZE': 'LOGITIZE',
    'DIGITIZE': 'DIGITIZE',
    'REDUCE': 'REDUCE',
    'EXTEND': 'EXTEND',
    'ENVIRONMENT': 'ENVIRONMENT',
}

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved_map.get(t.value.upper(), 'IDENTIFIER')
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
    t.value = int(t.value, 10)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
