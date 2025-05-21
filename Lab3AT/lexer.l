%{
#include "parser.tab.h"  // для определения токенов из bison
%}

%%

"TRUE"              { return TRUE; }
"FALSE"             { return FALSE; }
"VAR"               { return VAR; }
"SIZE"              { return SIZE; }
"REDUCE"            { return REDUCE; }
"EXTEND"            { return EXTEND; }
"MOVE"              { return MOVE; }
"ROTATE"            { return ROTATE; }
"LEFT"              { return LEFT; }
"RIGHT"             { return RIGHT; }
"FOR"               { return FOR; }
"BOUNDARY"          { return BOUNDARY; }
"STEP"              { return STEP; }
"SWITCH"            { return SWITCH; }
"TRUE"              { return TRUE; } // todo remove
"FALSE"             { return FALSE; } // todo remove
"NOT"               { return NOT; }
"AND"               { return AND; }
"MXTRUE"            { return MXTRUE; }
"MXFALSE"           { return MXFALSE; }
"GET"               { return GET; }
"ENVIRONMENT"       { return ENVIRONMENT; }
"TASK"              { return TASK; }
"DO"                { return DO; }
"RESULT"            { return RESULT; }
"FINDEXIT"          { return FINDEXIT; }
"PLEASE"            { return PLEASE; }
"THANKS"            { return THANKS; }

[ \t\r\n]+          { /* пропускаем пробелы */ }
[0-9]+              { yylval.ival = atoi(yytext); return INT_LITERAL; }
0[xX][0-9a-fA-F]+   { yylval.ival = strtol(yytext, NULL, 16); return INT_LITERAL; }
0[0-7]+             { yylval.ival = strtol(yytext, NULL, 8); return INT_LITERAL; }
[a-zA-Z_][a-zA-Z0-9_]* { yylval.sval = strdup(yytext); return IDENTIFIER; }

"=="                { return EQ; }
"!="                { return NEQ; }
"<="                { return LEQ; }
">="                { return GEQ; }
"<"                 { return LT; }
">"                 { return GT; }
"+"                 { return PLUS; }
"-"                 { return MINUS; }
"*"                 { return MUL; }
"/"                 { return DIV; }
"="                 { return ASSIGN; }
";"                 { return SEMICOLON; }
","                 { return COMMA; }
"("                 { return LPAREN; }
")"                 { return RPAREN; }
"["                 { return LBRACKET; }
"]"                 { return RBRACKET; }
"{"                 { return LBRACE; }
"}"                 { return RBRACE; }

.                   { fprintf(stderr, "Unknown character: %s\n", yytext); }

%%
