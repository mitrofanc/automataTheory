package lab2at.dfa;

import java.util.BitSet;
import java.util.Map;

public record DFAState(
        BitSet positions,
        boolean accept,
        Map<Character, Integer> charTrans,
        Map<Integer, Integer> groupTrans
) {}
