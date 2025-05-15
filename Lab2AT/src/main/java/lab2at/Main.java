package lab2at;

import lab2at.dfa.DFARunner;
import lab2at.lexer.Lexer;
import lab2at.lexer.Token;
import lab2at.lib.RegexLib;
import lab2at.parser.RegexParser;
import lab2at.ast.Node;
import lab2at.dfa.DFACompiler;
import lab2at.dfa.DFAState;
import lab2at.util.GraphVizRenderer;

import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) {
        RegexLib re = RegexLib.compile("abc?(<name1>lo|l)(t{3})%?%...<name1>");
        System.out.println( re.match("ablottt?lo") );   // true
        System.out.println( re.match("abctttlo") );     // false
    }

}
