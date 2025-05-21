%{
#include <stdio.h>
#include <stdlib.h>

void yyerror(const char *s);
int yylex(void);
%}

%union {
    int ival;
    char* sval;
    // здесь можно добавить типы для AST-узлов
}

%token <ival> INT_LITERAL
%token <sval> IDENTIFIER
%token TRUE FALSE VAR SIZE REDUCE EXTEND MOVE ROTATE LEFT RIGHT FOR BOUNDARY STEP
%token ASSIGN SEMICOLON COMMA LPAREN RPAREN LBRACKET RBRACKET

%start program

%%

program:
    statements
;

statements:
    statements statement
    | statement
;

statement:
    var_declaration SEMICOLON
    | assignment SEMICOLON
    | move_command SEMICOLON
    | rotate_command SEMICOLON
    | for_loop
    // другие операторы
;

var_declaration:
    VAR IDENTIFIER dimensions_opt ASSIGN expression
;

dimensions_opt:
    /* пусто */
    | LBRACKET INT_LITERAL RBRACKET
    | LBRACKET INT_LITERAL COMMA INT_LITERAL RBRACKET
    // и т.д.
;

assignment:
    IDENTIFIER ASSIGN expression
;

move_command:
    MOVE
;

rotate_command:
    ROTATE LEFT
    | ROTATE RIGHT
;

for_loop:
    FOR IDENTIFIER BOUNDARY expression STEP expression statements
;

expression:
    INT_LITERAL
    | IDENTIFIER
    | expression PLUS expression
    | expression MINUS expression
    | expression MUL expression
    | expression DIV expression
    | LPAREN expression RPAREN
;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Error: %s\n", s);
}

int main(void) {
    return yyparse();
}
