package operationsTests;
import lab2at.lib.RegexLib;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ReverseTests {

    @Test
    void testMatchAndReverseMatchSimple() {
        String pattern = "abc";
        RegexLib lib = RegexLib.compile(pattern);
        RegexLib rev = lib.reverse();

        assertTrue(lib.match("abc"));
        assertFalse(lib.match("cba"));

        assertTrue(rev.match("cba"));
        assertFalse(rev.match("abc"));
    }

    @Test
    void testMatchAndReverseMatchWithGroups() {
        String pattern = "(<g1>a...)(<g2>b)c";
        RegexLib lib = RegexLib.compile(pattern);
        RegexLib rev = lib.reverse();

        String input = "aaabc";
        assertTrue(lib.match(input));
        var gr = lib.searchWithGroups(input);
        assertEquals("aaa", gr.group("g1"));
        assertEquals("b", gr.group("g2"));

        String reversedInput = new StringBuilder(input).reverse().toString();
        assertTrue(rev.match(reversedInput));
        var mrRev = rev.searchWithGroups(reversedInput);
        assertEquals("aaa", mrRev.group("g1"));
        assertEquals("b", mrRev.group("g2"));
    }

    @Test
    void testMatchAndReverseComplex() {
        String pattern = "abc?(<name1>lo|l)(t{3})%?%...<name1>";
        RegexLib lib = RegexLib.compile(pattern);
        RegexLib rev = lib.reverse();

        String input = "ablottt??lo";
        String reversedInput = new StringBuilder(input).reverse().toString();

        assertTrue(lib.match(input));
        assertFalse(lib.match(reversedInput));

        assertTrue(rev.match(reversedInput));
        assertFalse(rev.match(input));
    }

    @Test
    void testReverseWithKleeneStar() {
        RegexLib lib = RegexLib.compile("a(<g>b...)c");
        RegexLib rev = lib.reverse();

        assertTrue(lib.match("abbbc"));

        String revInput = new StringBuilder("abbbc").reverse().toString();
        assertTrue(rev.match(revInput));
        var gr = rev.searchWithGroups(revInput);
        assertEquals("bbb", gr.group("g"));
    }

    @Test
    void testReverseWithAlternation() {
        RegexLib lib = RegexLib.compile("(<g>a|b)c");
        RegexLib rev = lib.reverse();

        assertTrue(lib.match("ac"));
        assertTrue(lib.match("bc"));
        assertFalse(lib.match("cc"));

        String revInputA = "ca";
        String revInputB = "cb";

        assertTrue(rev.match(revInputA));
        assertTrue(rev.match(revInputB));
        assertFalse(rev.match(new StringBuilder("cc").reverse().toString()));

        var mrA = rev.searchWithGroups(revInputA);
        assertNotNull(mrA);
        assertEquals("a", mrA.group("g"));
    }
}
