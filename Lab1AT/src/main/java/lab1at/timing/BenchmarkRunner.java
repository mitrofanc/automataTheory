package lab1at.timing;

import lab1at.generator.CorrectStringGenerator;
import lab1at.generator.IncorrectStringGenerator;
import lab1at.recognizer.Recognizer;
import lab1at.recognizer.RecognizerFactory;

public class BenchmarkRunner {
    public static void main(String[] args) {
        String[] parserTypes = {"regex", "flex", "smc"};

        for (String parserType : parserTypes) {
            Recognizer recognizer = RecognizerFactory.createRecognizer(parserType);
            TimingService timingService = new TimingService(new CorrectStringGenerator());
            String outputFile = "timing_results_correct_" + parserType + ".csv";
            System.out.println("Тест для корректных строк, парсер: " + parserType);
            timingService.runTimingTests(recognizer, outputFile);
        }

        for (String parserType : parserTypes) {
            Recognizer recognizer = RecognizerFactory.createRecognizer(parserType);
            TimingService timingService = new TimingService(new IncorrectStringGenerator());
            String outputFile = "timing_results_incorrect_" + parserType + ".csv";
            System.out.println("Тест для некорректных строк, парсер: " + parserType);
            timingService.runTimingTests(recognizer, outputFile);
        }

        GraphBuilder.buildGraph("Время распознавания (корректные строки)", "timing_results_correct");
        GraphBuilder.buildGraph("Время распознавания (некорректные строки)", "timing_results_incorrect");
    }
}
