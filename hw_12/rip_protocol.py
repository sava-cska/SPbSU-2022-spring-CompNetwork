import threading
import time
import queue
import json

io_mutex = threading.Lock()

class DistanceTable(object):
    def __init__(self, routers, ip_address):
        self.ip_address = ip_address
        self.next_router = {}
        self.distance = {}
        for router in routers:
            self.next_router[router] = ''
            self.distance[router] = len(routers) + 1 if ip_address != router else 0
    
    def add_edge(self, destination):
        self.next_router[destination] = destination
        self.distance[destination] = 1
    
    def update_from_neighbour(self, neighbour):
        changed = False
        for router in self.distance:
            if neighbour.distance[router] + 1 < self.distance[router]:
                self.distance[router] = neighbour.distance[router] + 1
                self.next_router[router] = neighbour.ip_address
                changed = True
        return changed
    
    def print_table(self):
        print('{:<20}{:<20}{:<20}'.format('Router IP', 'Next router', 'Distance'))
        for router in self.distance:
            dist = self.distance[router]
            distance = 'inf' if dist == len(self.distance) + 1 else dist
            print('{:<20}{:<20}{:<20}'.format(router, self.next_router[router], distance))
        print('---------------')

class Router(object):
    def __init__(self, routers, ip_address):
        self.mutex = threading.Lock()
        self.update_info_queue = queue.Queue()
        self.table = DistanceTable(routers, ip_address)
        self.neighbours = []
        self.final_state = False
        self.changed = True
        self.iterations = 0
    
    def add_edge(self, neighbour):
        self.neighbours.append(neighbour)
        self.table.add_edge(neighbour.table.ip_address)

    def send_info(self):
        step = 0
        while True:
            self.mutex.acquire()
        
            if not self.changed:
                self.iterations += 1
            else:
                self.iterations = 0
            if self.iterations == 3:
                self.final_state = True

            self.changed = False
            for neighbour in self.neighbours:
                neighbour.update_info_queue.put(self.table)
            
            step += 1
            io_mutex.acquire()
            print('Step {} of router {}'.format(step, self.table.ip_address))
            self.table.print_table()
            io_mutex.release()

            finish = self.final_state
            self.mutex.release()
            if finish:
                break

            time.sleep(3)

    def receive_info(self):
        while True:
            self.mutex.acquire()

            if not self.update_info_queue.empty():
                neighbour = self.update_info_queue.get()
                changed = self.table.update_from_neighbour(neighbour)
                if changed:
                    self.changed = True

            finish = self.final_state
            self.mutex.release()
            if finish:
                break

            time.sleep(0.2)
    
    def run(self):
        update_runner = threading.Thread(target=self.receive_info)
        update_runner.start()
        self.send_info()
        update_runner.join()

if __name__ == '__main__':
    with open('config.json', 'r') as file_network:
        network = json.load(file_network)
    
    graph = {}
    routers = []

    for router in network['routers']:
        routers.append(router)
        graph[router] = []
    
    for edge in network['connections']:
        graph[edge['router_1']].append(edge['router_2'])
        graph[edge['router_2']].append(edge['router_1'])

    ipToRouter = {}
    for router in routers:
        ipToRouter[router] = Router(routers, router)
    for router in routers:
        for neighbour in graph[router]:
            ipToRouter[router].add_edge(ipToRouter[neighbour])

    threads = []    
    for router in routers:
        thr = threading.Thread(target=ipToRouter[router].run)
        thr.start()
        threads.append(thr)

    for thr in threads:
        thr.join()
    
    for router in routers:
        print('Final state of router {}:'.format(router))
        ipToRouter[router].table.print_table()