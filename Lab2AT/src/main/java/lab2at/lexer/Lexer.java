package lab2at.lexer;

import java.util.ArrayList;
import java.util.List;

public final class Lexer {
    private final String src;       // входная строка
    private final int n;            // её длина
    private int i = 0;              // текущий индекс
    private final List<Token> tokens = new ArrayList<>();

    public Lexer(String pattern) {
        this.src = pattern;
        this.n = pattern.length();
    }

    // Сканируем и составляем список токенов
    public List<Token> scan() {
        while (i < n) {
            char c = src.charAt(i);

            if (c == '.' && i + 2 < n && src.charAt(i+1) == '.' && src.charAt(i+2) == '.') {
                tokens.add(new Token(TokenType.KLEENE, null));
                i += 3;
                continue;
            }

            switch (c) {
                case '|' -> { tokens.add(new Token(TokenType.OR, null)); i++; }
                case '?' -> { tokens.add(new Token(TokenType.QUESTION, null)); i++; }
                case '(' -> { tokens.add(new Token(TokenType.LPAREN, null)); i++; }
                case ')' -> { tokens.add(new Token(TokenType.RPAREN, null)); i++; }
                case '{' -> {
                    int j = i + 1;
                    if (j >= n || !Character.isDigit(src.charAt(j)))
                        throw new IllegalArgumentException("Digit expected after '{'");

                    StringBuilder num = new StringBuilder();
                    while (j < n && Character.isDigit(src.charAt(j))) {
                        num.append(src.charAt(j));
                        j++;
                    }
                    if (j >= n || src.charAt(j) != '}')
                        throw new IllegalArgumentException("Missing '}' after repeat number");

                    tokens.add(new Token(TokenType.LBRACE, null));
                    tokens.add(new Token(TokenType.LITERAL, num.toString()));
                    tokens.add(new Token(TokenType.RBRACE, null));

                    i = j + 1;
                }
                case '}' -> { tokens.add(new Token(TokenType.RBRACE, null)); i++; }
                case '%' -> {
                    if (i + 2 >= n || src.charAt(i+2) != '%')
                        throw new IllegalArgumentException("Invalid using \"%\"");
                    tokens.add(new Token(TokenType.LITERAL, String.valueOf(src.charAt(i+1))));
                    i += 3;  // пропускаем %...%
                }
                case '<' -> { tokens.add(readGroupName()); } //
                default -> {
                    tokens.add(new Token(
                            TokenType.LITERAL,
                            String.valueOf(c)
                    ));
                    i++;
                }
            }
        }

        tokens.add(new Token(TokenType.EOF, null));
        return tokens;
    }

    // group_name или group_ref
    private Token readGroupName() {
        int j = i + 1;
        StringBuilder sb = new StringBuilder();

        // читаем имя до '>'
        while (j < n && Character.isLetterOrDigit(src.charAt(j))) {
            sb.append(src.charAt(j));
            j++;
        }
        if (j >= n || src.charAt(j) != '>')
            throw new IllegalArgumentException("Expect \"<\"");

        String name = sb.toString();
        i = j + 1;  // i после >

        // смотрим это было определение или ссылка
        boolean prevLparen = !tokens.isEmpty() && tokens.get(tokens.size()-1).type() == TokenType.LPAREN;
        TokenType type = prevLparen ? TokenType.GROUP_NAME : TokenType.GROUP_REF;
        return new Token(type, name);
    }
}
