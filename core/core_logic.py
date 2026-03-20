import heapq
from collections import deque
from .hash_function import validate_signature
import json
import multiprocessing as mp
from typing import Protocol
import time
import signal

class CoreLogic:
    def __init__(self, input_queue: mp.Queue, aggregator_queue: mp.Queue, config)-> None:
        self.input_queue = input_queue
        self.output_queue = aggregator_queue
        self.config = config
        return
    def process(self):
        queue = self.input_queue
        while True:
            packet = queue.get() 
            if packet is None:
                # Agle process ke liye EOF behj do
                queue.put(None)
                return

            isPacketValid = self._validate(packet)
            if (isPacketValid):
                packet["isValid"] = True
            else:
                # ye issliye taake bara package na jaaye, aur thora kaam optimize ho jaaye
                packet = {
                    "_id":packet["_id"],
                    "isValid": False
                }

            self.output_queue.put(packet)
        return
    def _validate(self,packet):
        key = self.config['stateless_tasks']['secret_key']
        iterations = self.config['stateless_tasks']['iterations']

        hash_val = packet.get('security_hash')
        raw_val = str(packet.get("metric_value"))
        return validate_signature(hash_val,raw_val,key,iterations)

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
            if received_packet is None:
                # POISON PILL
                self.output.put(None)
                return

            heapq.heappush(self.pq,(received_packet["_id"],received_packet))
            while self.pq and self.pq[0][0] == self.expected_id:
                _, packet_to_process = heapq.heappop(self.pq)
                avg = self._generate_output(packet_to_process)
                if avg is not None:
                    self.output.put(avg)
                self.expected_id +=1

    def _generate_output(self,packet):
        if (packet["isValid"]):
            self.deque.append(float(packet['metric_value']))
            running_avg = sum(self.deque)/len(self.deque)
            return running_avg


