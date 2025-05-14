package lab2at.parser;

import lab2at.ast.*;
import lab2at.lexer.*;
import lombok.Getter;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public final class RegexParser {
    private final List<Token> tokens;
    private Iterator<Token> it;
    private Token look;  // текущий токен
    @Getter
    private final Map<String, Node> groupDefs = new HashMap<>(); // имя → тело группы

    public RegexParser(List<Token> tokens) {
        this.tokens = tokens;
    }

    // Функция для парсинга токенов, возвращает корень (дерево без GROUP_REF)
    public Node parse() {
        it = tokens.iterator();
        look = it.next();
        Node result = parseExpr();
        expect(TokenType.EOF);
        collectDefs(result); // составляем мапу группа->выражение
        return expandRefs(result);
    }

    // 1) OR (минимальный приоритет)
    private Node parseExpr() {
        Node left = parseConcat();
        while (look.type() == TokenType.OR) {
            look = it.next();
            Node right = parseConcat();
            left = new Node(NodeType.OR, left, right);
        }
        return left;
    }

    // 2) CONCAT
    private Node parseConcat() {
        Node left = parsePostfix();
        while (canStartConc(look.type())) {
            Node right = parsePostfix();
            left = new Node(NodeType.CONCAT, left, right);
        }
        return left;
    }

    // 3) Постфиксы (..., ?, {)
    private Node parsePostfix() {
        Node left = parseAtoms();
        boolean again = true;
        while (again) {
            switch (look.type()) {
                case KLEENE -> { // a...
                    look = it.next();
                    left = new Node(NodeType.KLEENE, left, null);
                }
                case QUESTION -> { // a?
                    look = it.next();
                    left = new Node(NodeType.OPTIONAL, left, null);
                }
                case LBRACE -> { // a{n}
                    left = parseRepeat(left);
                }
                default -> again = false;
            }
        }
        return left;
    }

    // Обработка повтора (a{n})
    private Node parseRepeat(Node base) {
        expect(TokenType.LBRACE);
        if (look.type() != TokenType.LITERAL || !look.text().chars().allMatch(Character::isDigit))
            throw new IllegalArgumentException("Expected number after '{'");
        int k = Integer.parseInt(look.text());
        look = it.next();
        expect(TokenType.RBRACE);
        if (k < 0)
            throw new IllegalArgumentException("Negative repeat not allowed");
        if (k == 0)
            return new Node(NodeType.NULL_REPEAT, null, null, null);
        if (k == 1)
            return base;
        Node res = copy(base);
        for (int i = 1; i < k; i++)
            res = new Node(NodeType.CONCAT, res, copy(base));
        return res;
    }

    // 4) Атомарные символы
    private Node parseAtoms() {
        switch (look.type()) {
            case LPAREN -> {
                look = it.next(); // '('
                Token nameTok = null;
                if (look.type() == TokenType.GROUP_NAME) {
                    nameTok = look;
                    look = it.next(); // имя группы
                }
                Node inner = parseExpr();
                expect(TokenType.RPAREN);

                if (nameTok != null) {
                    return new Node(NodeType.GROUP_DEF, nameTok.text(), inner, null);
                }
                return inner;
            }
            // <name> - ссылка
            case GROUP_REF -> {
                String name = look.text();
                look = it.next();
                return new Node(NodeType.GROUP_CALL, name, null, null);
            }

            case LITERAL -> {
                String lit = look.text();
                look = it.next();
                return new Node(NodeType.LITERAL, lit, null, null);
            }
            default -> throw new IllegalStateException("Unexpected token: " + look.type());
        }
    }

    // Проверка на соответствие токена типу t
    private void expect(TokenType t) {
        if (look.type() != t)
            throw new IllegalArgumentException("Unexpected token: " + look);
        if (t != TokenType.EOF)
            look = it.next();
    }

    // Проверяем, можно ли продолжать строить CONCAT
    private boolean canStartConc(TokenType t) {
        return t == TokenType.LITERAL || t == TokenType.GROUP_REF || t == TokenType.LPAREN;
    }

    private Node copy(Node n) {
        if (n == null) return null;
        Node left = copy(n.left);
        Node right = copy(n.right);
        Node ret = new Node(n.type, n.text, left, right);
        return ret;
    }

    // собираем определение групп в мапу
    private void collectDefs(Node n) {
        if (n == null) return;
        if (n.type == NodeType.GROUP_DEF)
            groupDefs.put(n.text, n.left);   // имя → тело
        collectDefs(n.left);
        collectDefs(n.right);
    }

    private Node expandRefs(Node n) {
        if (n == null) return null;
        if (n.type == NodeType.GROUP_DEF) {
            return new Node(NodeType.GROUP_CALL, n.text, null, null);
        } else {
            n.left  = expandRefs(n.left);
            n.right = expandRefs(n.right);
            return n;
        }
    }
}
