package lab1at.recognizer.flex;
%%
%class Lexer
%unicode
%standalone

%{
    private String funcName;

    public String getFuncName() {
        return funcName;
    }
%}

TYPE = (int|short|long)
NAME = [a-zA-Z][a-zA-Z0-9]{0,15}
LineTerminator = \r\n|\r|\n
WHITESPACE = ({LineTerminator}|[ \t\f])
OPENPAREN = "("
CLOSEPAREN = ")"
SEMICOLON = ";"
COMMA = ","

%state FUNCNAME
%state OPENPAREN
%state PARAMTYPE
%state PARAMNAME
%state NEXTPARAM
%state SEMICOLON
%state ERROR

%%
<YYINITIAL> {
    {WHITESPACE}*{TYPE}{WHITESPACE}+ {
        yybegin(FUNCNAME);

    }
    . {
        yybegin(ERROR);
    }
}

<FUNCNAME> {
    {NAME} {
        funcName = yytext();
        yybegin(OPENPAREN);
    }
    . {
        yybegin(ERROR);
    }
}

<OPENPAREN> {
    {WHITESPACE}*{OPENPAREN} {
        yybegin(PARAMTYPE);

    }
    . {
        yybegin(ERROR);
    }
}

<PARAMTYPE> {
    {WHITESPACE}*{TYPE}{WHITESPACE}+ {
        yybegin(PARAMNAME);

    }
    {CLOSEPAREN}{WHITESPACE}* {
        yybegin(SEMICOLON);
    }
    . {
        yybegin(ERROR);
    }
}

<PARAMNAME> {
    {NAME}{WHITESPACE}* {
        yybegin(NEXTPARAM);
    }
    . { 
        yybegin(ERROR);
    }
}

<NEXTPARAM> {
    {WHITESPACE}*{COMMA}{WHITESPACE}* {
        yybegin(PARAMTYPE);
    }
    {CLOSEPAREN}{WHITESPACE}* {
        yybegin(SEMICOLON);
    }
    . {
        yybegin(ERROR);
    }
}

<SEMICOLON> {
    {SEMICOLON}{WHITESPACE}* {
        return 0;
    }
    . {
        yybegin(ERROR);
    }
}

<ERROR> {
    . {
        return 1;
    }
}