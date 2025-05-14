package lab2at;

import lab2at.dfa.DFARunner;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFAState;
import lab2at.util.GraphVizRenderer;

import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        String pattern = "abc?(<name1>lo|l)(t{3})%?%...<name1>";
        String input = "ablottt?lo";

        Lexer lexer = new Lexer(pattern);
        List<Token> tokens = lexer.scan();
        RegexParser parser = new RegexParser(tokens);
        Node ast = parser.parse();
        System.out.println("AST: " + ast);

        Map<String,Node> defs = parser.getGroupDefs();
        DFACompiler compiler = new DFACompiler(defs);
        int mainDfaId = compiler.compile(ast);
        List<List<DFAState>> all = compiler.getAll();

        DFARunner runner = new DFARunner(all);
        boolean ok = runner.matches(input, mainDfaId);
        System.out.printf("Input \"%s\" matches? %s%n", input, ok);

        GraphVizRenderer.renderAst(ast, "out/ast.png");
        GraphVizRenderer.renderAllDfas(all, "out/dfa");
    }
}
