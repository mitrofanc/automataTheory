package lab2at.lib;

import lab2at.dfa.DFAState;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFARunner;
import lab2at.dfa.DFARunner.PrefixMatch;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class RegexLib {
    private final DFARunner runner;
    private final int mainDFAId;
    private final List<String> groupNames; // группы
    private final Map<String, Integer> nameToDfaId;

    private RegexLib(DFARunner runner, int mainDFAId, List<String> groupNames, Map<String,Integer> nameToDfaId) {
        this.runner = runner;
        this.mainDFAId = mainDFAId;
        this.groupNames = List.copyOf(groupNames);
        this.nameToDfaId = Map.copyOf(nameToDfaId);
    }

    public static RegexLib compile(String pattern) {
        Lexer lexer = new Lexer(pattern);
        List<Token> tokens = lexer.scan();

        RegexParser parser = new RegexParser(tokens);
        Node ast = parser.parse();

        var groupDefs = parser.getGroupDefs();
        List<String> names = new ArrayList<>(groupDefs.keySet()); // имена всех групп

        DFACompiler compiler = new DFACompiler(groupDefs);
        int mainId = compiler.compile(ast);
        List<List<DFAState>> allDFA = compiler.getAll();
        DFARunner runner = new DFARunner(allDFA);

        return new RegexLib(runner, mainId, names, compiler.getNameToDfa());
    }

    public boolean match(String input) {
        PrefixMatch prefixMatch = runner.matchPrefix(input, 0, mainDFAId);
        return prefixMatch.length == input.length();
    }

    public String search(String text) {
        for (int i = 0; i < text.length(); i++) {
            PrefixMatch prefixMatch = runner.matchPrefix(text, i, mainDFAId);
            if (prefixMatch.length >= 0) {
                return text.substring(i, i + prefixMatch.length);
            }
        }
        return null;
    }

    public MatchResult searchWithGroups(String text) {
        for (int i = 0; i < text.length(); i++) {
            PrefixMatch prefixMatch = runner.matchPrefix(text, i, mainDFAId);
            if (prefixMatch.length >= 0) { // сохранение групп
                String str = text.substring(i, i + prefixMatch.length);
                Map<String, String> map = new LinkedHashMap<>();
                for (String grName : groupNames) {
                    int dfaId = nameToDfaId.get(grName);
                    int[] span = prefixMatch.namedGroupSubs.get(dfaId);
                    String sub = (span == null || span[1] < 0) ? null : str.substring(span[0], span[1]);
                    map.put(grName, sub);
                }
                return new MatchResult(map);
            }
        }
        return null;
    }
}
