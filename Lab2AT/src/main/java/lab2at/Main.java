package lab2at;

import lab2at.ast.NodeType;
import lab2at.dfa.DFABuilder;
import lab2at.dfa.DFAState;
import lab2at.dfa.TreeAnalyzer;
import lab2at.lexer.Lexer;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.util.GraphVizRenderer;

import java.util.List;

public class Main {
    public static void main(String[] args) throws Exception {
        String pattern = "(a|bc)*d";

        Lexer lex = new Lexer(pattern);
        Node  tree = new RegexParser(lex.scan()).parse();

        Node eof = new Node(NodeType.LITERAL, "#");
        tree = new Node(NodeType.CONCAT, tree, eof);

        TreeAnalyzer analyzer = new TreeAnalyzer();
        analyzer.analyze(tree);
        GraphVizRenderer.renderAst(tree, "ast.png");

        DFABuilder b = new DFABuilder(tree, analyzer.follow);
        List<DFAState> dfa = b.build();

        GraphVizRenderer.renderDfa(dfa, "dfa.png");
    }
}

