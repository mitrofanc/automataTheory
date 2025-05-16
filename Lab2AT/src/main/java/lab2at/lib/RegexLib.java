package lab2at.lib;

import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFARunner;
import lab2at.dfa.DFAState;
import lombok.Getter;

import java.util.List;
import java.util.Map;

public final class RegexLib {
    @Getter
    private final String pattern;
    private final List<List<DFAState>> allDFA;
    private final int mainDFAId;
    private final DFARunner runner;

    private RegexLib(String pattern, List<List<DFAState>> allDFA, int mainDFAId) {
        this.pattern = pattern;
        this.allDFA = allDFA;
        this.mainDFAId = mainDFAId;
        this.runner = new DFARunner(allDFA);
    }

    public static RegexLib compile(String pattern) {
        Lexer lexer = new Lexer(pattern);
        List<Token> tokens = lexer.scan();

        RegexParser parser = new RegexParser(tokens);
        Node ast = parser.parse();
        Map<String, Node> groupDefs = parser.getGroupDefs();

        DFACompiler compiler = new DFACompiler(groupDefs);
        int mainId = compiler.compile(ast);
        List<List<DFAState>> all = compiler.getAll();

        return new RegexLib(pattern, all, mainId);
    }

    public boolean match(String input) {
        return runner.matches(input, mainDFAId);
    }

    public String search(String text) {
        for (int pos = 0; pos < text.length(); pos++) {
            int len = runner.matchPrefix(text, pos, mainDFAId);
            if (len >= 0) {
                return text.substring(pos, pos + len);
            }
        }
        return null;
    }

    public MatchResult searchWithGroups(String text) {
        for (int pos = 0; pos < text.length(); pos++) {
            int len = runner.matchPrefix(text, pos, mainDFAId);
            if (len >= 0) {
                return new MatchResult(pos, pos + len, text);
            }
        }
        return null;
    }

    public record MatchResult(int start, int end, String str) {
        @Override
        public String toString() {
            return str.substring(start, end);
        }
    }
}
