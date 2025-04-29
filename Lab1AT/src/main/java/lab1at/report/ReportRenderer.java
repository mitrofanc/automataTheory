package lab1at.report;

import java.util.Map;

public class ReportRenderer implements Report {
    private final Map<String, Integer> statistics;

    public ReportRenderer(Map<String, Integer> statistics) {
        this.statistics = statistics;
    }

    @Override
    public String generateReport() {
        StringBuilder sb = new StringBuilder();
        sb.append("Overloaded functions report:\n");
        statistics.forEach((name, count) ->
                sb.append(name).append(" -> ").append(count).append("\n")
        );
        // todo add timing results
        return sb.toString();
    }
}
