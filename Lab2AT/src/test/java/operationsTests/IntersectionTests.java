package operationsTests;

import lab2at.lib.MatchResult;
import lab2at.lib.RegexLib;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class IntersectionTests {

    @Test
    void testDisjointLanguages() {
        // L1 = {"a"}, L2 = {"b"} → пересечение пусто
        RegexLib r1 = RegexLib.compile("a");
        RegexLib r2 = RegexLib.compile("b");
        RegexLib r = r1.intersect(r2);
        assertFalse(r.match("a"));
        assertFalse(r.match("b"));
    }

    @Test
    void testIdenticalLanguages() {
        // L1 = L2 = { "a", "b" }
        RegexLib r1 = RegexLib.compile("a|b");
        RegexLib r2 = RegexLib.compile("a|b");
        RegexLib r = r1.intersect(r2);
        assertTrue(r.match("a"));
        assertTrue(r.match("b"));
        assertFalse(r.match("c"));
    }

    @Test
    void testSubsetLanguage() {
        // a..., aa = aa
        RegexLib r1 = RegexLib.compile("a...");
        RegexLib r2 = RegexLib.compile("aa");
        RegexLib r = r1.intersect(r2);
        assertTrue(r.match("aa"));
        assertFalse(r.match("a"));
        assertFalse(r.match("aaa"));
    }

    @Test
    void testProperOverlap() {
        RegexLib r1 = RegexLib.compile("a...");
        RegexLib r2 = RegexLib.compile("a?b");
        RegexLib r = r1.intersect(r2);
        assertFalse(r.match("a"));
        assertFalse(r.match("aa"));
        assertFalse(r.match("aba"));
    }

    @Test
    void testIntersectionWithGroups() {
        RegexLib r1 = RegexLib.compile("(<g>aa...)b");
        RegexLib r2 = RegexLib.compile("aa?b");
        RegexLib r  = r1.intersect(r2);

        assertFalse(r.match("b"));
        assertFalse(r.match("aaab"));
    }
}
