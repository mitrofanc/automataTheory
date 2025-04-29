package lab1at.service;

import lab1at.recognizer.RecognitionResult;
import lombok.Getter;

import java.util.HashMap;
import java.util.Map;

public class OverloadStatisticsService {

    private final Map<String, Integer> overloadCount = new HashMap<>();

    public Map<String, Integer> getOverloadCount () {
        return overloadCount;
    }

    public void processResult(RecognitionResult result) {
        if (result.recognized()) {
            String name = result.funcName();
            if (name != null) {
                overloadCount.merge(name, 1, Integer::sum);
            }
        }
    }

    public void printStatistics() {
        for (Map.Entry<String, Integer> entry : overloadCount.entrySet()) {
            System.out.println(entry.getKey() + " -> " + entry.getValue());
        }
    }
}
