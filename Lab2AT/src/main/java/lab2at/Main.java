package lab2at;

import lab2at.lib.RegexLib;

public class Main {
    public static void main(String[] args) throws Exception {
        // Исходный паттерн "abc"
        RegexLib regex = RegexLib.compile("abc");
        System.out.println("match(\"abc\") = " + regex.match("abc")); // true
        System.out.println("match(\"abd\") = " + regex.match("abd")); // false

        // Инверсия: принимает все, что НЕ "abc"
        RegexLib inverted = regex.invert();
        System.out.println("invert match(\"abc\") = " + inverted.match("abc")); // false
        System.out.println("invert match(\"abd\") = " + inverted.match("abd")); // true
        System.out.println("invert match(\"\") = " + inverted.match(""));     // true (пустая строка не "abc")

        // Пересечение паттернов: a... и aa...
        RegexLib r1 = RegexLib.compile("a...");
        RegexLib r2 = RegexLib.compile("aa...");
        RegexLib intersected = r1.intersect(r2);

        System.out.println("intersect match(\"a\") = " + intersected.match("a"));     // false, т.к. r2 требует минимум 2 'a'
        System.out.println("intersect match(\"aa\") = " + intersected.match("aa"));   // true
        System.out.println("intersect match(\"aaa\") = " + intersected.match("aaa")); // true

        // Проверка search с инверсией
        String text = "zzzabczzz";
        System.out.println("search in inverted: " + inverted.search(text)); // найдёт первое несовпадение, т.е. "zzz" или т.п.
    }
}
