import ply.yacc as yacc
from Lexer.lexer import tokens

precedence = (
    ('right', 'ASSIGN'),
    ('left', 'MXTRUE', 'MXFALSE'),
    ('left', 'MXEQ', 'MXLT', 'MXGT', 'MXLTE', 'MXGTE'),
    ('left', 'ELEQ', 'ELLT', 'ELGT', 'ELLTE', 'ELGTE'),
    ('left', 'AND'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('right', 'NOT'),
)

def p_empty(p):
    'empty :'
    pass

def p_literal(p):
    '''
    literal : TRUE
            | FALSE
            | OCT_INT
            | DEC_INT
            | HEX_INT
    '''
    p[0] = ('literal', p[1])

def p_dimensions_opt(p):
    '''
    dimensions_opt : LBRACKET dimensions_list RBRACKET
                   | empty
    '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_dimensions_list(p):
    '''
    dimensions_list : expression
                    | dimensions_list COMMA expression
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_var_declaration(p):
    'var_declaration : VAR IDENTIFIER dimensions_opt ASSIGN literal'
    p[0] = ('var_declaration', p[2], p[3], p[5])

def p_array_access(p):
    'array_access : IDENTIFIER LBRACKET indices_list RBRACKET'
    p[0] = ('array_access', p[1], p[3])

def p_indices_list(p):
    '''
    indices_list : expression
                 | indices_list COMMA expression
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_size_operator(p):
    'size_operator : SIZE LPAREN IDENTIFIER RPAREN'
    p[0] = ('size_operator', p[3])

def p_type_conversion(p):
    '''
    type_conversion : LOGITIZE IDENTIFIER
                    | DIGITIZE IDENTIFIER
    '''
    p[0] = ('type_conversion', p[1], p[2])

def p_size_change(p):
    '''
    size_change : REDUCE IDENTIFIER dimensions_opt
                | EXTEND IDENTIFIER dimensions_opt
    '''
    p[0] = ('size_change', p[1], p[2], p[3])

def p_assignment(p):
    'assignment : IDENTIFIER ASSIGN expression'
    p[0] = ('assignment', p[1], p[3])

def p_arithmetic_expression_binop(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression MULT expression
               | expression DIV expression
    '''
    p[0] = ('binop', p[2], p[1], p[3])

def p_comparison_with_zero(p):
    '''
    expression : expression MXEQ
               | expression MXLT
               | expression MXGT
               | expression MXLTE
               | expression MXGTE
    '''
    p[0] = ('comparison_zero', p[2], p[1])

def p_elementwise_comparison_with_zero(p):
    '''
    expression : ELEQ expression
               | ELLT expression
               | ELGT expression
               | ELLTE expression
               | ELGTE expression
    '''
    p[0] = ('elementwise_comparison_zero', p[1], p[2])

def p_logical_not(p):
    'expression : NOT expression'
    p[0] = ('not', p[2])

def p_logical_and(p):
    'expression : expression AND expression'
    p[0] = ('and', p[1], p[3])

def p_mxtrue(p):
    'expression : MXTRUE expression'
    p[0] = ('mxtrue', p[2])

def p_mxfalse(p):
    'expression : MXFALSE expression'
    p[0] = ('mxfalse', p[2])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_literal(p):
    '''
    expression : literal
               | array_access
               | size_operator
               | type_conversion
               | IDENTIFIER
    '''
    p[0] = ('expression', p[1])

def p_block(p):
    '''
    block : statement_with_politeness
          | LPAREN statements RPAREN
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[2]

def p_statements(p):
    '''
    statements : statement_with_politeness
               | statements statement_with_politeness
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_for_loop(p):
    'for_loop : FOR IDENTIFIER BOUNDARY expression STEP IDENTIFIER block'
    p[0] = ('for_loop', p[2], p[4], p[6], p[7])

def p_switch_statement(p):
    '''
    switch_statement : SWITCH expression BOOL_LITERAL block else_clause_opt
    '''
    p[0] = ('switch', p[2], p[3], p[4], p[5])

def p_else_clause_opt(p):
    '''
    else_clause_opt : BOOL_LITERAL block
                    | empty
    '''
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = None

def p_robot_move(p):
    'robot_move : MOVE'
    p[0] = ('move',)

def p_robot_rotate_left(p):
    'robot_rotate : ROTATE LEFT'
    p[0] = ('rotate_left',)

def p_robot_rotate_right(p):
    'robot_rotate : ROTATE RIGHT'
    p[0] = ('rotate_right',)

def p_get_environment(p):
    'get_environment : GET ENVIRONMENT'
    p[0] = ('get_environment',)

def p_task_function(p):
    '''
    task_function : TASK IDENTIFIER param_list block RETURN_RESULT
    '''
    p[0] = ('task_function', p[2], p[3], p[4], p[5])

def p_param_list(p):
    '''
    param_list : IDENTIFIER
               | param_list COMMA IDENTIFIER
               | empty
    '''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_return_result(p):
    '''
    RETURN_RESULT : RESULT IDENTIFIER
    '''
    p[0] = ('return', p[2])

def p_function_call(p):
    '''
    function_call : DO IDENTIFIER arg_list
    '''
    p[0] = ('function_call', p[2], p[3])

def p_arg_list(p):
    '''
    arg_list : expression
             | arg_list COMMA expression
             | empty
    '''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_get_function_result(p):
    'get_function_result : GET IDENTIFIER'
    p[0] = ('get_function_result', p[2])

def p_statement_with_politeness(p):
    '''
    statement_with_politeness : optional_please statement optional_thanks
    '''
    p[0] = ('statement_politeness', p[1], p[2], p[3])

def p_optional_please(p):
    '''
    optional_please : PLEASE
                    | empty
    '''
    p[0] = p[1] if len(p) == 2 else None

def p_optional_thanks(p):
    '''
    optional_thanks : THANKS
                    | empty
    '''
    p[0] = p[1] if len(p) == 2 else None

def p_statement(p):
    '''
    statement : var_declaration
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
              | get_function_result
    '''
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type}, line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()
