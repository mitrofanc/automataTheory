package dfaTests;

import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFARunner;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class DFATests {

    private boolean matches(String pattern, String input) {
        Lexer lexer = new Lexer(pattern);
        List<Token> tokens = lexer.scan();

        RegexParser parser = new RegexParser(tokens);
        Node ast = parser.parse();

        Map<String, Node> defs = parser.getGroupDefs();
        DFACompiler compiler = new DFACompiler(defs);
        int mainId = compiler.compile(ast);

        DFARunner runner = new DFARunner(compiler.getAll());
        return runner.matches(input, mainId);
    }

    @Test
    void testLiteralExact() {
        assertTrue(matches("hello", "hello"));
        assertFalse(matches("hello", "hell"));
        assertFalse(matches("hello", "hello!"));
    }

    @Test
    void testOptionalOperator() {
        assertTrue(matches("a?b", "b"));
        assertTrue(matches("a?b", "ab"));
        assertFalse(matches("a?b", "aab"));
    }

    @Test
    void testKleeneOperator() {
        assertTrue(matches("a...", ""));
        assertTrue(matches("a...", "a"));
        assertTrue(matches("a...", "aaaa"));
        assertFalse(matches("a...", "b"));
    }

    @Test
    void testAlternationAndConcat() {
        assertTrue(matches("a|bc", "a"));
        assertTrue(matches("a|bc", "bc"));
        assertFalse(matches("a|bc", "ab"));
        assertFalse(matches("a|bc", ""));
    }

    @Test
    void testGroupCallSimple() {
        String pat = "(<g>a|b)c<g>";
        assertTrue(matches(pat, "aca"));
        assertTrue(matches(pat, "bcb"));
        assertFalse(matches(pat, "acc"));
        assertFalse(matches(pat, "cbc"));
    }

    @Test
    void testRepeatNamedGroup() {
        String pat = "(<d>0|1){3}?<d>";
        assertTrue(matches(pat, "0000"));
        assertTrue(matches(pat, "1010"));
        assertTrue(matches(pat, "1111"));
        assertFalse(matches(pat, "000"));
        assertFalse(matches(pat, "00000"));
    }
}
