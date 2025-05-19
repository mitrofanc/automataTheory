package lab2at.util;

import lab2at.dfa.DFAState;
import lab2at.lib.RegexLib;
import lab2at.lib.ToRegex;

import java.util.List;
import java.util.Map;

public class ToRegexI {
    private ToRegexI() {}

    public static String toRegex(List<DFAState> states,
                                 Map<Integer,String> groupNames,
                                 RegexLib lib) {
        String rgx = ToRegex.toRegex(states, groupNames);
        System.out.println(rgx);
        return lib.getPattern();
    }
}
