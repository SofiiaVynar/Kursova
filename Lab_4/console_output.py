from output_strategy import OutputStrategy


class ConsoleOutput(OutputStrategy):
    def output(self, data: dict):
        print(data)
