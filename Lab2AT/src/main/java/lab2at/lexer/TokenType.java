package lab2at.lexer;

public enum TokenType {
    LITERAL,      // любой символ (включая экранированный %x%)
    OR,           // |
    QUESTION,     // ?
    LBRACE,       // {
    RBRACE,       // }
    LPAREN,       // (
    RPAREN,       // )
    KLEENE,     // ...  (Клини)
    GROUP_NAME,   // <name>
    GROUP_REF,    // <name> — ссылка на группу
    EOF
}

