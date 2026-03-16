import heapq
from collections import deque
from .hash_function import validate_signature
import json
import multiprocessing as mp

class Core:
    def __init__(self, input_queue: mp.Queue, aggregator_queue: mp.Queue, config)-> None:
        self.input_queue = input_queue
        self.output_queue = aggregator_queue
        self.config = config
        return
    def process(self):
        queue = self.input_queue
        while True:
            packet = queue.get() 
            if (not packet):
                self.output_queue.put(packet)
                return
            isPacketValid = self._validate(packet)
            if (isPacketValid):
                self.output_queue.put(packet)
            else:
                print("Invalid Packet Recieved")
        return
    def _validate(self,packet):
        key = self.config['stateless_tasks']['secret_key']
        iterations = self.config['stateless_tasks']['iterations']

        hash_val = packet.get('security_hash')
        raw_val = packet.get("metric_value")
        return validate_signature(hash_val,raw_val,key,iterations)

class Agregator:
    def __init__(self, queue: mp.Queue, output_queue: mp.Queue, maxLen: int) -> None:
        self.queue = queue
        self.expected_id = 0
        self.pq = []
        self.deque = deque(maxlen=maxLen)
        self.output = output_queue
        return
    # TODO: expected id 
    def agregate(self):
        while True:
            received_packet = self.queue.get()
            if (not received_packet):
                return
            while received_packet and received_packet["_id"] == self.expected_id:
                avg = self._generate_output(received_packet)
                self.output.put(avg)
                self.expected_id +=1
                received_packet = None
                if self.pq:
                    received_packet = heapq.heappop(self.pq)
            if (received_packet):
                heapq.heappush(self.pq,received_packet)
        return
    def _generate_output(self,packet):
        self.deque.append(float(packet['metric_value']))
        running_avg = sum(self.deque)/len(self.deque)
        return running_avg


#
# OUTPUT
# if __name__ == "__main__":
#     packet = {
#         "_id": 0,
#         "entity_name": "Sensor_Alpha",
#         "time_period": "1773037634",
#         "metric_value": "23.81",
#         "security_hash": "6fffc630960e0661f40d2c57ee51271a55f024161d76f574da49674bd1a3af88",
#     }
#     input_queue = mp.Queue()
#     input_queue.put(packet)
#     input_queue.put(None)
#
#     output_queue = mp.Queue()
#     config = json.loads(json_string)
#     core = Core(input_queue, output_queue,config)
#     core.process()
#     final_out = mp.Queue()
#     a = Agregator(output_queue,final_out,50) 
#     a.agregate()
#     print("HERE")
#     get_result = final_out.get()
#     print(get_result)

