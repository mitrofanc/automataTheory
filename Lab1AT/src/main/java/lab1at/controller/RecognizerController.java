package lab1at.controller;

import lab1at.listener.InputData;
import lab1at.listener.InputListener;
import lab1at.listener.InputListenerFactory;
import lab1at.output.Output;
import lab1at.output.OutputFactory;
import lab1at.recognizer.Recognizer;
import lab1at.recognizer.RecognizerFactory;
import lab1at.report.Report;
import lab1at.report.ReportRenderer;
import lab1at.service.OverloadStatisticsService;

import java.util.List;

public class RecognizerController {

    public void run() {
        InputListener listener = InputListenerFactory.createListener();
        InputData inputData = listener.getInput();

        Recognizer recognizer = RecognizerFactory.createRecognizer(inputData.parserType());

        List<String> lines = inputData.lines();
        OverloadStatisticsService statsService = new OverloadStatisticsService();
        for (String line : lines) {
            statsService.processResult(recognizer.recognize(line));
        }

        Report report = new ReportRenderer(statsService.getOverloadCount());
        String reportContent = report.generateReport();

        Output output = OutputFactory.createOutput();
        output.display(reportContent);
    }
}
