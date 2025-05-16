package searchTests;

import lab2at.lib.MatchResult;
import lab2at.lib.RegexLib;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class SearchTests {

    @Test
    void testSearchSimple() {
        RegexLib lib = RegexLib.compile("abc");
        assertEquals("abc", lib.search("zzzabczzz"));
    }

    @Test
    void testSearchWithGroupsSimple() {
        RegexLib lib = RegexLib.compile("(<first>a...)(<second>b)c");
        MatchResult mr = lib.searchWithGroups("xxaaabcyy");
        assertNotNull(mr);
        assertEquals("aaa", mr.group("first"));
        assertEquals("b", mr.group("second"));
    }

    @Test
    void testSearchWithGroupsOptional() {
        RegexLib lib = RegexLib.compile("(<first>a...)(<second>b)?c");
        MatchResult mr = lib.searchWithGroups("xxaaac");
        assertNotNull(mr);
        assertEquals("aaa", mr.group("first"));
        assertNull(mr.group("second"));

        mr = lib.searchWithGroups("xxaaabc");
        assertNotNull(mr);
        assertEquals("aaa", mr.group("first"));
        assertEquals("b", mr.group("second")); // группа сработала
    }

    @Test
    void testRepeatAndOptionalMixed() {
        RegexLib lib = RegexLib.compile("(<grp>a{2})?b");
        MatchResult mr1 = lib.searchWithGroups("b");
        assertNotNull(mr1);
        assertNull(mr1.group("grp"));

        MatchResult mr2 = lib.searchWithGroups("aab");
        assertNotNull(mr2);
        assertEquals("aa", mr2.group("grp"));
    }

    @Test
    void testMultipleNamedGroups() {
        RegexLib lib = RegexLib.compile("(<g1>a)(<g2>b)(<g3>c)");
        MatchResult mr = lib.searchWithGroups("xxabcxx");
        assertNotNull(mr);
        assertEquals("a", mr.group("g1"));
        assertEquals("b", mr.group("g2"));
        assertEquals("c", mr.group("g3"));
    }

    @Test
    void testLiteralEscapePercent() {
        RegexLib lib = RegexLib.compile("%?%");
        assertTrue(lib.match("?"));
        assertEquals("?", lib.search("abc?def"));
    }

    @Test
    void testRepeatZeroTimes() {
        RegexLib lib = RegexLib.compile("a{0}b");
        assertTrue(lib.match("b"));
        assertFalse(lib.match("ab"));
    }
}
