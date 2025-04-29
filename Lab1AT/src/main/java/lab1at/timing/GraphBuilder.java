package lab1at.timing;

import org.knowm.xchart.BitmapEncoder;
import org.knowm.xchart.BitmapEncoder.BitmapFormat;
import org.knowm.xchart.XYChart;
import org.knowm.xchart.XYChartBuilder;
import org.knowm.xchart.SwingWrapper;
import org.knowm.xchart.style.Styler;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class GraphBuilder {

    public static void buildGraph(String graphTitle, String csvPrefix) {
        String[] parserTypes = {"regex", "flex", "smc"};
        XYChart chart = new XYChartBuilder()
                .width(800)
                .height(600)
                .title(graphTitle)
                .xAxisTitle("Количество параметров")
                .yAxisTitle("Время (ns)")
                .build();
        chart.getStyler().setLegendPosition(Styler.LegendPosition.InsideNE);

        for (String parser : parserTypes) {
            String csvFile = csvPrefix + "_" + parser + ".csv";
            List<Integer> paramCounts = new ArrayList<>();
            List<Long> times = new ArrayList<>();

            try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
                String line;
                boolean header = true;
                while ((line = br.readLine()) != null) {
                    if (header) {
                        header = false;
                        continue;
                    }
                    String[] parts = line.split(",");
                    paramCounts.add(Integer.parseInt(parts[0]));
                    times.add(Long.parseLong(parts[1]));
                }
            } catch (IOException e) {
                System.out.println("Ошибка чтения файла " + csvFile + ": " + e.getMessage());
                continue;
            }

            chart.addSeries(parser, paramCounts, times);
        }

        new SwingWrapper<>(chart).displayChart();

        try {
            String filename = csvPrefix + "_chart.png";
            BitmapEncoder.saveBitmap(chart, filename, BitmapFormat.PNG);
            System.out.println("График сохранён в файл " + filename);
        } catch (IOException e) {
            System.out.println("Ошибка сохранения графика: " + e.getMessage());
        }
    }
}
