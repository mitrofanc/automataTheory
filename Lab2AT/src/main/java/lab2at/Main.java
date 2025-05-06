package lab2at;

import lab2at.lexer.Lexer;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.util.GraphVizRenderer;

public class Main {
    public static void main(String[] args) throws Exception {
//        String pattern = "a|(<digit>0|1){3}?<digit>";
        String pattern = "a.........";
        Lexer lex = new Lexer(pattern);
        RegexParser parser = new RegexParser(lex.scan());
        Node tree = parser.parse();

        System.out.println(tree);

        GraphVizRenderer.render(tree, "ast.png");
    }
}
