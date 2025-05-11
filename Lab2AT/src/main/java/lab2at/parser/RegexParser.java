package lab2at.parser;

import lab2at.ast.*;
import lab2at.lexer.*;

import java.util.Iterator;
import java.util.List;

public final class RegexParser {
    private final List<Token> tokens;
    private Iterator<Token> it;
    private Token look;  // текущий токен

    public RegexParser(List<Token> tokens) {
        this.tokens = tokens;
    }

    // Функция для парсинга токенов, возвращает корень
    public Node parse() {
        it = tokens.iterator();
        look = it.next();
        Node result = parseExpr();
        expect(TokenType.EOF);
        return result;
    }

    // 1) OR (минимальный приоритет)
    private Node parseExpr() {
        Node left = parseConcat();
        // пока встречаем |, строим OR
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
        // пока следующий токен способен начать primary, делаем конкатенацию
        while (canStartAtom(look.type())) {
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
        if (look.type() != TokenType.LITERAL || !look.text().chars().allMatch(Character::isDigit)) {
            throw new IllegalArgumentException("Expected number after '{'");
        }
        int k = Integer.parseInt(look.text());
        look = it.next();
        expect(TokenType.RBRACE);

        if (k < 0) {
            throw new IllegalArgumentException("Negative repeat not allowed");
        } else if (k == 0) {
            return new Node(NodeType.NULL_REPEAT, null, null, null);
        } else if (k == 1) {
            return base;
        } else {
            // разворачиваем r{n}
            Node result = copyBranch(base);
            for (int i = 1; i < k; i++) {
                result = new Node(NodeType.CONCAT, result, copyBranch(base));
            }
            return result;
        }
    }

    // 4) Атомарные символы
    private Node parseAtoms() {
        switch (look.type()) {
            // (
            case LPAREN -> {
                look = it.next();  // съели (
                Token nameTok = null;
                if (look.type() == TokenType.GROUP_NAME) {
                    // определение именованной группы
                    nameTok = look;
                    look = it.next();
                }
                Node inner = parseExpr();
                expect(TokenType.RPAREN);
                if (nameTok != null) {
                    // (<name> r)
                    return new Node(NodeType.GROUP_DEF, nameTok.text(), inner, null);
                }
                // обычные скобки возвращают вложенное выражение
                return inner;
            }
            // <name> — ссылка
            case GROUP_REF -> {
                String name = look.text();
                look = it.next();
                return new Node(NodeType.GROUP_REF, name, null, null);
            }
            // одиночный символ
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
        if (look.type() != t) {
            throw new IllegalArgumentException("Unexpected token type: " + look);
        }
        if (t != TokenType.EOF) {
            look = it.next();
        }
    }

    // Проверяем, можно ли продолжать строить CONCAT
    private boolean canStartAtom(TokenType t) {
        return t == TokenType.LITERAL || t == TokenType.GROUP_REF || t == TokenType.LPAREN;
    }

    private Node copyBranch(Node n) {
        if (n == null) return null;
        Node left  = copyBranch(n.left);
        Node right = copyBranch(n.right);
        Node copy  = new Node(n.type, n.text, left, right);
        copy.repeatCount = n.repeatCount;
        return copy;
    }
}
