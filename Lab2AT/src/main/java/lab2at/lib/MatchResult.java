package lab2at.lib;

import java.util.*;

public final class MatchResult implements Iterable<String> {
    private final Map<String, String> namedGroups;

    public MatchResult(Map<String, String> namedGroups) {
        this.namedGroups = Collections.unmodifiableMap(new LinkedHashMap<>(namedGroups));
    }

    public String group(String name) {
        if (!namedGroups.containsKey(name))
            throw new IllegalArgumentException("No such group: " + name);
        return namedGroups.get(name);
    }

    @Override
    public Iterator<String> iterator() {
        return namedGroups.values().iterator();
    }
}