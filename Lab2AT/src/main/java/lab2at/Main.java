// src/main/java/lab2at/Main.java
package lab2at;

import lab2at.lib.RegexLib;
import lab2at.lib.MatchResult;

public class Main {
    public static void main(String[] args) {
        String pattern = "(<first>a...)(<second>b)c";
        String text    = "xxaaabcyy";

        RegexLib lib = RegexLib.compile(pattern);

        String full = "aaabc";
        System.out.printf("match(\"%s\") → %b%n", full, lib.match(full));

        // 2) Поиск
        String found = lib.search(text);
        System.out.printf("search(\"%s\") → %s%n", text,
                found != null ? "\"" + found + "\"" : "null");

        // 3) Поиск с группами
        MatchResult mr = lib.searchWithGroups(text);
        if (mr != null) {
            System.out.println("searchWithGroups → найдено:");
            System.out.printf("  first  = \"%s\"%n", mr.group("first"));
            System.out.printf("  second = \"%s\"%n", mr.group("second"));
        } else {
            System.out.println("searchWithGroups → ничего не найдено");
        }
    }
}
