

class Telemetry:
    def __init__(self, input_queue:mp.Queue, agregate_queue: mp.Queue, output_queue:mp.Queue) -> None:
        self.input = input_queue
        self.agregate = agregate_queue
        self.output = output_queue
        self.observers = []
        self.signal_received = False
    def get_data(self):
        return self.input.qsize(), self.agregate.qsize(), self.output.qsize()

    def notify(self):
        data=self.get_data()
        for observer in self.observers:
            observer.update(data)
    def poll(self,interval:int = 1):
        while True:
            if (self.signal_received):
                return
            time.sleep(interval)
            self.notify()


    def setup_sig_handler(self):

        def sig_handler(self):
            self.signal_received = True
            return

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)
