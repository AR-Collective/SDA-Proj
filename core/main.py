import heapq
from collections import deque

class Core:
    def __init__(self, input_queue: mp.Queue, aggregator_queue: mp.Queue)-> None:
        self.input_queue = input_queue
        self.output_queue = aggregator_queue
        return
    def process(self):
        queue = self.input_queue
        while True:
            packet = queue.get() 
        isPacketValid = _validate(packet)
        if (isPacketValid):
            processed = _process(packet)
            self.output_queue.put(processed)
        return

class Agregator:
    def __init__(self, queue: mp.Queue, output_queue: mp.Queue, maxLen: int) -> None:
        self.queue = queue
        self.expected_id = 0
        self.pq = []
        self.deque = deque(maxlen=maxLen)
        self.output = output_queue
        return
    def agregate(self):
        while True:
            received_packet = self.queue.get()
            # TODO: add poison pill
            while received_packet and received_packet.id == self.expected_id:
                _generate_output(received_packet)
                self.expected_id +=1
                received_packet = None
                if self.pq:
                    received_packet = heapq.heappop(self.pq)
            if (received_packet):
                heapq.heappush(self.pq,received_packet)
        return

