package lab2at.lib;

import lab2at.dfa.DFAOperations;
import lab2at.dfa.DFAState;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFARunner;
import lab2at.dfa.DFARunner.PrefixMatch;
import lombok.Getter;

import java.util.*;

@Getter
public final class RegexLib {
    private final DFARunner runner;
    private final int mainDFAId;
    private final List<String> groupNames; // группы
    private final Map<String, Integer> nameToDfaId;
    private final List<List<DFAState>> allDFA;
    private final Map<String, Node> groupDefs;
    private Node mainRoot;

    private RegexLib(DFARunner runner,
                     int mainDFAId,
                     List<String> groupNames,
                     Map<String, Integer> nameToDfaId,
                     List<List<DFAState>> allDFA,
                     Map<String, Node> groupDefs,
                     Node mainRoot) {
        this.runner = runner;
        this.mainDFAId = mainDFAId;
        this.groupNames = List.copyOf(groupNames);
        this.nameToDfaId = Map.copyOf(nameToDfaId);
        this.allDFA = List.copyOf(allDFA);
        this.groupDefs = Map.copyOf(groupDefs);
        this.mainRoot = mainRoot;
    }

    private RegexLib(DFARunner runner,
                     int mainDFAId,
                     List<String> groupNames,
                     Map<String, Integer> nameToDfaId,
                     List<List<DFAState>> allDFA,
                     Map<String, Node> groupDefs) {
        this.runner = runner;
        this.mainDFAId = mainDFAId;
        this.groupNames = List.copyOf(groupNames);
        this.nameToDfaId = Map.copyOf(nameToDfaId);
        this.allDFA = List.copyOf(allDFA);
        this.groupDefs = Map.copyOf(groupDefs);
        this.mainRoot = null;
    }

    public static RegexLib compile(String pattern) {
        Lexer lexer = new Lexer(pattern);
        List<Token> tokens = lexer.scan();

        RegexParser parser = new RegexParser(tokens);
        Node ast = parser.parse();

        Map<String, Node> groupDefs = new HashMap<>(parser.getGroupDefs()); // делаем изменяемую копию

        List<String> names = new ArrayList<>(groupDefs.keySet());

        DFACompiler compiler = new DFACompiler(groupDefs);
        int mainId = compiler.compile(ast);
        List<List<DFAState>> allDFA = compiler.getAll();
        DFARunner runner = new DFARunner(allDFA);

        return new RegexLib(runner, mainId, names, compiler.getNameToDfa(), allDFA, groupDefs, ast);
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
                    int[] subStr = prefixMatch.namedGroupSubs.get(dfaId);
                    String sub = (subStr == null || subStr[1] < 0) ? null : str.substring(subStr[0], subStr[1]);
                    map.put(grName, sub);
                }
                return new MatchResult(map);
            }
        }
        return null;
    }

    public RegexLib reverse() {
        Map<String, Node> revGroupDefs = new HashMap<>();
        for (var e : groupDefs.entrySet()) {
            revGroupDefs.put(e.getKey(), DFAOperations.reverse(e.getValue()));
        }

        mainRoot = DFAOperations.reverse(mainRoot);
//        Node mainRoot = revGroupDefs.get("mainAST");
//        revGroupDefs.remove("mainAST");
        // не нужно удалять "mainAST" — компилятор справится с этим

        DFACompiler compiler = new DFACompiler(revGroupDefs);
        int mainId = compiler.compile(mainRoot);

        List<List<DFAState>> allDFA = compiler.getAll();
        DFARunner runner = new DFARunner(allDFA);

        List<String> names = new ArrayList<>(revGroupDefs.keySet());

        return new RegexLib(runner, mainId, names, compiler.getNameToDfa(), allDFA, revGroupDefs, mainRoot);
    }

    public RegexLib intersect(RegexLib other) {
        List<DFAState> dfa1 = this.allDFA.get(this.mainDFAId);
        List<DFAState> dfa2 = other.allDFA.get(other.mainDFAId);

        List<DFAState> intersected = DFAOperations.intersect(dfa1, dfa2);

        List<List<DFAState>> newAll = new ArrayList<>(this.allDFA);
        newAll.add(intersected);
        int newMainId = newAll.size() - 1;

        return new RegexLib(new DFARunner(newAll), newMainId, this.groupNames, this.nameToDfaId, newAll, this.groupDefs);
    }
}
