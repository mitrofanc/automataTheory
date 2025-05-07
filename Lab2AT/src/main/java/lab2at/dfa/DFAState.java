package lab2at.dfa;

import java.util.BitSet;
import java.util.Map;

public record DFAState(BitSet set, boolean accept, Map<Character, Integer> trans) {}