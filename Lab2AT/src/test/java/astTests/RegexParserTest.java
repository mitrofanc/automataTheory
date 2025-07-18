package astTests;

import lab2at.ast.*;
import lab2at.lexer.Lexer;
import lab2at.parser.RegexParser;
import org.junit.jupiter.api.Test;
import util.TestUtil;

import static org.junit.jupiter.api.Assertions.assertThrows;

class RegexParserTest {

    private static Node init(String pattern) {
        return new RegexParser(new Lexer(pattern).scan()).parse();
    }

    @Test
    void literalConcat() {
        Node expected = new Node(NodeType.CONCAT,
                new Node(NodeType.LITERAL, "a"),
                new Node(NodeType.LITERAL, "b"));
        Node actual = init("ab");

        TestUtil.renderTree(actual, "concat_ab");
        AstAssert.assertAstEquals(expected, actual);
    }

    @Test
    void alterVsConcatPrecedence() {
        Node concat = new Node(NodeType.CONCAT,
                new Node(NodeType.LITERAL, "b"),
                new Node(NodeType.LITERAL, "c"));
        Node expected = new Node(NodeType.OR,
                new Node(NodeType.LITERAL, "a"),
                concat);

        Node actual = init("a|bc");

        TestUtil.renderTree(actual, "or_and");
        AstAssert.assertAstEquals(expected, actual);
    }

    @Test
    void kleeneOptional() {
        Node expected = new Node(NodeType.OPTIONAL,
                new Node(NodeType.KLEENE,
                        new Node(NodeType.LITERAL, "a"), null),
                null);

        Node actual = init("a...?");
        TestUtil.renderTree(actual, "kleene_optional");
        AstAssert.assertAstEquals(expected, actual);
    }

    @Test
    void escapeBraces() {
        Node expected = new Node(NodeType.LITERAL, "{");
        Node actual = init("%{%");
        TestUtil.renderTree(actual, "escape_brace");
        AstAssert.assertAstEquals(expected, actual);
    }

    @Test
    void nestedParentheses() {
        Node expected = new Node(NodeType.LITERAL, "a");
        Node actual = init("(((a)))");
        TestUtil.renderTree(actual, "nested_paren");
        AstAssert.assertAstEquals(expected, actual);
    }

    @Test
    void repeatWithNoNumber() {
        assertThrows(IllegalArgumentException.class, () -> init("a{b}"));
    }

    @Test
    void repeatMissingClosingBrace() {
        assertThrows(IllegalArgumentException.class, () -> init("a{3"));
    }

    @Test
    void emptyNamedGroupShouldFail() {
        assertThrows(IllegalStateException.class, () -> init("(<digit>)"));
    }
}
