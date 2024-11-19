import zmq
import time
import random
import threading

class Taxi:
    def __init__(self, taxi_id, grid_size, start_pos, speed, max_services):
        self.taxi_id = taxi_id
        self.grid_size = grid_size
        self.position = start_pos
        self.speed = speed
        self.max_services = max_services
        self.active_broker = "tcp://localhost:5557"

        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.notification_socket = self.context.socket(zmq.SUB)
        self.notification_socket.connect("tcp://localhost:5560")
        self.notification_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    def reconnect_broker(self, new_broker):
        self.pub_socket.disconnect(self.active_broker)
        self.active_broker = new_broker
        self.pub_socket.connect(self.active_broker)
        print(f"Taxi {self.taxi_id} reconnected to broker: {self.active_broker}")

    def listen_notifications(self):
        while True:
            message = self.notification_socket.recv_json()
            self.reconnect_broker(f"tcp://localhost:{message['active_broker']}")

    def move(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        while self.max_services > 0:
            dx, dy = random.choice(directions)
            new_x = max(0, min(self.position[0] + dx, self.grid_size[0] - 1))
            new_y = max(0, min(self.position[1] + dy, self.grid_size[1] - 1))
            self.position = (new_x, new_y)

            self.pub_socket.send_json({
                "type": "update",
                "id": self.taxi_id,
                "position": self.position,
                "status": "available" if self.max_services > 0 else "done"
            })

            print(f"Taxi {self.taxi_id} moved to {self.position}.")
            time.sleep(self.speed)

        print(f"Taxi {self.taxi_id} has completed all services.")

    def start(self):
        self.pub_socket.connect(self.active_broker)
        threading.Thread(target=self.listen_notifications).start()
        self.move()

if __name__ == "__main__":
    taxi = Taxi(taxi_id=1, grid_size=(10, 10), start_pos=(0, 0), speed=1, max_services=3)
    taxi.start()
