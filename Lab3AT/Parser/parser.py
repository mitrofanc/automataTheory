import ply.yacc as yacc
from Lexer.lexer import tokens

precedence = (
    ('right', 'ASSIGN'),
    ('left',  'MXTRUE', 'MXFALSE'),
    ('left',  'MXEQ', 'MXLT', 'MXGT', 'MXLTE', 'MXGTE'),
    ('left',  'AND'),
    ('left',  'PLUS', 'MINUS'),
    ('left',  'MULT', 'DIV'),
    ('right', 'NOT'),
    ('right', 'UMINUS')
)

def p_empty(p):
    """empty :"""
    pass

def p_literal(p):
    """
    literal : BOOL_LITERAL
            | OCT_INT
            | DEC_INT
            | HEX_INT
    """
    p[0] = ('literal', p[1])

def p_array_literal(p):
    """array_literal : LBRACKET array_elements_opt RBRACKET"""
    p[0] = ('array_literal', p[2])

def p_array_elements_opt(p):
    """array_elements_opt : array_elements_list
                            | empty"""
    p[0] = p[1] or []

def p_array_elements_list(p):
    """array_elements_list : expression
                            | array_elements_list COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_dimensions_opt(p):
    """dimensions_opt : LBRACKET dimensions_list RBRACKET
                        | empty"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_dimensions_list(p):
    """dimensions_list : expression
                       | dimensions_list COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_var_declaration(p):
    """var_declaration : VAR IDENTIFIER dimensions_opt ASSIGN expression"""
    p[0] = ('var_declaration', p[2], p[3], p[5])

def p_array_access(p):
    """array_access : IDENTIFIER LBRACKET indices_list RBRACKET"""
    p[0] = ('array_access', p[1], p[3])

def p_indices_list(p):
    """indices_list : expression
                    | indices_list COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_size_operator(p):
    """size_operator : SIZE LPAREN IDENTIFIER RPAREN"""
    p[0] = ('size_operator', p[3])

def p_type_conversion(p):
    """type_conversion : LOGITIZE IDENTIFIER
                        | DIGITIZE IDENTIFIER"""
    p[0] = ('type_conversion', p[1], p[2])

def p_size_change(p):
    """size_change : REDUCE IDENTIFIER dimensions_opt
                    | EXTEND IDENTIFIER dimensions_opt"""
    p[0] = ('size_change', p[1], p[2], p[3])

def p_assignment(p):
    """assignment : IDENTIFIER ASSIGN expression"""
    p[0] = ('assignment', p[1], p[3])

def p_elementwise_comparison_with_zero_post(p):
    """expression : ELEQ expression
                 | ELLT expression
                 | ELGT expression
                 | ELLTE expression
                 | ELGTE expression"""
    p[0] = ('elementwise_comparison_zero', p[1], p[2])

def p_elementwise_comparison_with_zero_pre(p):
    """expression : ELEQ  LPAREN expression RPAREN
                  | ELLT  LPAREN expression RPAREN
                  | ELGT  LPAREN expression RPAREN
                  | ELLTE LPAREN expression RPAREN
                  | ELGTE LPAREN expression RPAREN"""
    p[0] = ('elementwise_comparison_zero', p[1], p[3])

def p_elementwise_comparison_two_args(p):
    """expression : ELEQ LPAREN expression RPAREN LPAREN expression RPAREN
                  | ELLT LPAREN expression RPAREN LPAREN expression RPAREN
                  | ELGT LPAREN expression RPAREN LPAREN expression RPAREN
                  | ELLTE LPAREN expression RPAREN LPAREN expression RPAREN
                  | ELGTE LPAREN expression RPAREN LPAREN expression RPAREN"""
    #                op           e1                  e2
    p[0] = ('elementwise_comparison_two', p[1], p[3], p[6])

def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[0] = ('uminus', p[2])

def p_expression_binop(p):
    """expression : expression PLUS expression
                 | expression MINUS expression
                 | expression MULT expression
                 | expression DIV expression"""
    p[0] = ('binop', p[2], p[1], p[3])

def p_comparison_with_zero(p):
    """expression : expression MXEQ
                 | expression MXLT
                 | expression MXGT
                 | expression MXLTE
                 | expression MXGTE"""
    p[0] = ('comparison_zero', p[2], p[1])

# префиксный вариант: MXGT ( expr )
def p_comparison_with_zero_prefix(p):
    """expression : MXEQ  LPAREN expression RPAREN
                  | MXLT  LPAREN expression RPAREN
                  | MXGT  LPAREN expression RPAREN
                  | MXLTE LPAREN expression RPAREN
                  | MXGTE LPAREN expression RPAREN"""
    p[0] = ('comparison_zero', p[1], p[3])

def p_logical_and(p):
    """expression : expression AND expression"""
    p[0] = ('and', p[1], p[3])

def p_logical_not(p):
    """expression : NOT expression"""
    p[0] = ('not', p[2])

def p_mxtrue(p):
    """expression : MXTRUE expression"""
    p[0] = ('mxtrue', p[2])

def p_mxfalse(p):
    """expression : MXFALSE expression"""
    p[0] = ('mxfalse', p[2])

def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]

def p_expression_primary(p):
    """
    expression : literal
               | array_literal
               | array_access
               | size_operator
               | type_conversion
               | get_environment
               | get_function_result
               | IDENTIFIER
    """
    if isinstance(p[1], tuple) and p[1][0] == 'get_environment':
        p[0] = p[1]
    else:
        p[0] = ('expr', p[1])


start = 'program'

def p_program(p):
    """program : statements"""
    p[0] = p[1]

def p_block(p):
    "block : LPAREN statements RPAREN"
    p[0] = p[2]

def p_statements(p):
    """statements : statement
                  | statements statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_for_loop(p):
    """
    for_loop : FOR IDENTIFIER BOUNDARY expression STEP expression block
    """
    p[0] = ('for_loop', p[2], p[4], p[6], p[7])

def p_switch_statement(p):
    """switch_statement : SWITCH expression BOOL_LITERAL block else_clause_opt"""
    p[0] = ('switch', p[2], p[3], p[4], p[5])

def p_else_clause_opt(p):
    """else_clause_opt : BOOL_LITERAL block
                        | empty"""
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = None

def p_robot_move(p):
    """robot_move : MOVE"""
    p[0] = ('move',)

def p_robot_rotate_left(p):
    """robot_rotate : ROTATE LEFT"""
    p[0] = ('rotate_left',)

def p_robot_rotate_right(p):
    """robot_rotate : ROTATE RIGHT"""
    p[0] = ('rotate_right',)

def p_get_environment(p):
    """get_environment : GET ENVIRONMENT"""
    p[0] = ('get_environment',)

def p_task_function(p):
    """task_function : TASK IDENTIFIER LPAREN param_list RPAREN block"""
    p[0] = ('task_function', p[2], p[4], p[6])

def p_param_list(p):
    """param_list : IDENTIFIER
                    | param_list COMMA IDENTIFIER
                    | empty"""
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_statement_result(p):
    """statement : RESULT expression"""
    p[0] = ('result', p[2])

def p_function_call(p):
    """function_call : DO IDENTIFIER arg_list"""
    p[0] = ('function_call', p[2], p[3])

def p_arg_list(p):
    """arg_list : expression
                | arg_list expression
                | empty"""
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_get_function_result(p):
    """get_function_result : GET IDENTIFIER"""
    p[0] = ('get_function_result', p[2])

def p_statement(p):
    """statement : var_declaration
                | assignment
                | for_loop
                | block
                | expression
                | size_change
                | switch_statement
                | robot_move
                | robot_rotate
                | get_environment
                | task_function
                | function_call
                | get_function_result"""
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}, line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()
