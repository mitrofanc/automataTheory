package lab1at.timing;

import lab1at.generator.StringGenerator;
import lab1at.recognizer.Recognizer;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class TimingService {
    private final StringGenerator stringGenerator;

    public TimingService(StringGenerator stringGenerator) {
        this.stringGenerator = stringGenerator;
    }

    public void runTimingTests(Recognizer recognizer, String outputFileName) {
        int numRows = 1000;
        int nameLength = 8;
        List<String> results = new ArrayList<>();
        results.add("Params,Time(ns)");

        for (int paramCount = 1; paramCount <= 1000; paramCount += 100) {
            List<String> lines = new ArrayList<>();

            for (int i = 0; i < numRows; i++) {
                String generatedString = stringGenerator.generateString(nameLength, paramCount);
                lines.add(generatedString);
            }
            long startTime = System.nanoTime();
            for (String line : lines) {
                recognizer.recognize(line);
            }
            long endTime = System.nanoTime();
            long duration = (endTime - startTime)/1000;
            results.add(paramCount + "," + duration);
        }

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFileName))) {
            for (String line : results) {
                writer.write(line);
                writer.newLine();
            }
            System.out.println("Результаты таймирования сохранены в " + outputFileName);
        } catch (IOException e) {
            System.out.println("Ошибка записи результатов таймирования: " + e.getMessage());
        }
    }
}
