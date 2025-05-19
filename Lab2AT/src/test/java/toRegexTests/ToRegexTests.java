package toRegexTests;

import lab2at.lib.RegexLib;
import lab2at.util.ToRegexI;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ToRegexTests {

    private boolean matches(String pattern, String input) {
        RegexLib lib1 = RegexLib.compile(pattern);

        var allDFA = lib1.getAllDFA();
        int mainId = lib1.getMainDFAId();

        Map<Integer, String> idToGroupName = new HashMap<>();
        for (var e : lib1.getNameToDfaId().entrySet()) {
            idToGroupName.put(e.getValue(), e.getKey());
        }

        String restored = ToRegexI.toRegex(allDFA.get(mainId), idToGroupName, lib1);
        System.out.println(pattern + " restored: " + restored);

        RegexLib lib2 = RegexLib.compile(restored);

        return lib1.match(input) && lib2.match(input);
    }

    @Test
    void testLiteralExact() {
        assertTrue(matches("aboba", "aboba"));
        assertFalse(matches("12kaf", "12|kaf"));
        assertFalse(matches("aboba", "abobaa"));
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
        String pat = "abc?(<name1>lo|l)(t{3})%?%...<name1>";
        assertTrue(matches(pat, "ablottt??lo"));
        assertTrue(matches(pat, "abclttt?l"));
        assertFalse(matches(pat, "acc"));
        assertFalse(matches(pat, "abclott?l"));
    }
}
