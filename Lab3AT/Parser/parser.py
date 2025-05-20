import ply.yacc as yacc
from Lexer.lexer import tokens  # Импорт токенов из lexer.py

precedence = (
    ('right', 'ASSIGN'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
)

# Таблица символов, для хранения переменных и функций
symbol_table = {}

# ----- ПРОГРАММА -----

def p_program(p):
    'program : statements'
    p[0] = ('program', p[1])

def p_statements_multiple(p):
    'statements : statements statement'
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    'statements : statement'
    p[0] = [p[1]]

# ----- ПРЕДЛОЖЕНИЯ -----

def p_statement(p):
    '''statement : var_declaration
                 | assignment
                 | move_command
                 | rotate_command
                 | for_loop
                 | switch_statement
                 | function_definition
                 | function_call
                 | get_result
                 | group_statements
    '''
    p[0] = p[1]

# Группировка предложений в скобках
def p_group_statements(p):
    'group_statements : LPAREN statements RPAREN'
    p[0] = ('group', p[2])

# ----- ОБЪЯВЛЕНИЕ ПЕРЕМЕННОЙ -----

def p_var_declaration(p):
    'var_declaration : VAR IDENTIFIER dimensions_opt ASSIGN expression'
    p[0] = ('var_decl', p[2], p[3], p[5])

def p_dimensions_opt_empty(p):
    'dimensions_opt :'
    p[0] = []

def p_dimensions_opt_list(p):
    'dimensions_opt : LBRACKET dim_list RBRACKET'
    p[0] = p[2]

def p_dim_list_multiple(p):
    'dim_list : dim_list COMMA expression'
    p[0] = p[1] + [p[3]]

def p_dim_list_single(p):
    'dim_list : expression'
    p[0] = [p[1]]

# ----- ПРИСВАИВАНИЕ -----

def p_assignment(p):
    'assignment : IDENTIFIER ASSIGN expression'
    p[0] = ('assign', p[1], p[3])

# ----- УПРАВЛЕНИЕ РОБОТОМ -----

def p_move_command(p):
    'move_command : MOVE'
    p[0] = ('move',)

def p_rotate_command(p):
    '''rotate_command : ROTATE LEFT
                      | ROTATE RIGHT'''
    p[0] = ('rotate', p[2])

# ----- ЦИКЛ FOR -----

def p_for_loop(p):
    'for_loop : FOR IDENTIFIER BOUNDARY expression STEP expression statements'
    p[0] = ('for', p[2], p[4], p[6], p[7])

# ----- SWITCH -----

def p_switch_statement(p):
    '''switch_statement : SWITCH expression TRUE statements FALSE statements
                        | SWITCH expression TRUE statements'''
    if len(p) == 8:
        p[0] = ('switch', p[2], p[4], p[6])
    else:
        p[0] = ('switch', p[2], p[4], None)

# ----- ОПРЕДЕЛЕНИЕ ФУНКЦИИ TASK -----

def p_function_definition(p):
    'function_definition : TASK IDENTIFIER parameter_list statements'
    p[0] = ('task', p[2], p[3], p[4])

def p_parameter_list_empty(p):
    'parameter_list :'
    p[0] = []

def p_parameter_list_multiple(p):
    '''parameter_list : parameter_list IDENTIFIER
                      | IDENTIFIER'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

# ----- ВЫЗОВ ФУНКЦИИ DO -----

def p_function_call(p):
    'function_call : DO IDENTIFIER argument_list'
    p[0] = ('do', p[2], p[3])

def p_argument_list_empty(p):
    'argument_list :'
    p[0] = []

def p_argument_list_multiple(p):
    '''argument_list : argument_list expression
                     | expression'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

# ----- ПОЛУЧЕНИЕ РЕЗУЛЬТАТА GET -----

def p_get_result(p):
    'get_result : GET IDENTIFIER'
    p[0] = ('get', p[2])

# ----- ВЫРАЖЕНИЯ -----

# Арифметические и логические бинарные операции
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIV expression
                  | expression AND expression'''
    p[0] = ('binop', p[2], p[1], p[3])

# Унарный логический оператор NOT
def p_expression_not(p):
    'expression : NOT expression'
    p[0] = ('not', p[2])

# Скобки для группировки выражений
def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

# Литералы: целочисленные и логические
def p_expression_int(p):
    '''expression : DEC_INT
                  | OCT_INT
                  | HEX_INT'''
    p[0] = ('int', p[1])

def p_expression_bool(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = ('bool', True if p[1].upper() == 'TRUE' else False)

# Переменная
def p_expression_var(p):
    'expression : IDENTIFIER'
    p[0] = ('var', p[1])

# Операторы сравнения с нулём (MXEQ, MXLT, MXGT, MXLTE, MXGTE)
def p_expression_mxcomp(p):
    '''expression : MXEQ expression
                  | MXLT expression
                  | MXGT expression
                  | MXLTE expression
                  | MXGTE expression'''
    p[0] = ('mxcomp', p[1], p[2])

# Поэлементные операторы сравнения с нулём (ELEQ, ELLT, ELGT, ELLTE, ELGTE)
def p_expression_elecomp(p):
    '''expression : ELEQ expression
                  | ELLT expression
                  | ELGT expression
                  | ELLTE expression
                  | ELGTE expression'''
    p[0] = ('elecomp', p[1], p[2])

# Операторы преобразования типов
def p_expression_cast(p):
    '''expression : LOGITIZE IDENTIFIER
                  | DIGITIZE IDENTIFIER'''
    p[0] = ('cast', p[1], p[2])

# Операторы изменения размерности
def p_expression_resize(p):
    '''expression : REDUCE IDENTIFIER dimensions_opt
                  | EXTEND IDENTIFIER dimensions_opt'''
    p[0] = ('resize', p[1], p[2], p[3])

# Оператор определения размера SIZE
def p_expression_size(p):
    'expression : SIZE LPAREN IDENTIFIER RPAREN'
    p[0] = ('size', p[3])

# Оператор GET ENVIRONMENT
def p_expression_environment(p):
    'expression : GET ENVIRONMENT'
    p[0] = ('get_environment',)

# ----- Ошибка -----

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ({p.value}) at line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()
