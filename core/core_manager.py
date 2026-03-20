import multiprocessing as mp
from . import CoreLogic


class CoreManager:
    def __init__(self, input_queue, agregator_queue, workers, core_config):
        self.workers = workers
        self.input_queue = input_queue
        self.agg_queue = agregator_queue
        self.config = core_config
        self.processes_arr = []

    def initialize_multiprocessing(self):
        self.processes_arr = [self.generate_worker() for _ in range(self.workers)]

    def generate_worker(self):
        core = CoreLogic(self.input_queue, self.agg_queue, self.config)
        process=mp.Process(target=core.process)
        process.start()
        return process

    def shutdown_core(self):
        for worker in self.processes_arr:
            worker.join()



