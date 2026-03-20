import time
import multiprocessing as mp
class Telemetry:
    def __init__(self, input_queue:mp.Queue, agregate_queue: mp.Queue, output_queue:mp.Queue) -> None:
        self.input = input_queue
        self.agregate = agregate_queue
        self.output = output_queue
        self.observers = []
        self.stop_event = mp.Event()   
    def get_data(self):
        return self.input.qsize(), self.agregate.qsize(), self.output.qsize()

    def subscribe(self, observer):
        self.observers.append(observer)


    def quit(self):
        self.stop_event.set()
    def notify(self):
        data=self.get_data()
        for observer in self.observers:
            observer.update(data)
    def poll(self,interval:int = 1):
        try:
            while not self.stop_event.is_set():
                self.stop_event.wait(interval)   
                self.notify()
        except KeyboardInterrupt:
            pass


    def setup_sig_handler(self):

        def sig_handler(self):
            self.signal_received = True
            return

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)
