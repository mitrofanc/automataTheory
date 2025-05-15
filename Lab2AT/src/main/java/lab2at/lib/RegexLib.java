package lab2at.lib;

import lab2at.ast.Node;
import lab2at.dfa.*;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lombok.Getter;

import java.util.List;
import java.util.Map;

public final class RegexLib {
    @Getter
    private final String pattern;
    @Getter
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
        int mainDFAId = compiler.compile(ast);
        List<List<DFAState>> allDFA = compiler.getAll();

        return new RegexLib(pattern, allDFA, mainDFAId);
    }

    public boolean match(String input) {
        return runner.matches(input, mainDFAId);
    }
}
