import zmq
import threading
import time

class Broker:
    def __init__(self, port, heartbeat_port):
        self.context = zmq.Context()
        self.broker_socket = self.context.socket(zmq.ROUTER)
        self.broker_socket.bind(f"tcp://localhost:{port}")
        self.heartbeat_socket = self.context.socket(zmq.PUSH)
        self.heartbeat_socket.connect(f"tcp://localhost:{heartbeat_port}")
        self.message_buffer = []

    def send_heartbeat(self):
        while True:
            self.heartbeat_socket.send_string("heartbeat")
            time.sleep(2)

    def forward_messages(self):
        while True:
            try:
                message = self.broker_socket.recv_multipart()
                self.message_buffer.append(message)  # Almacena mensajes para sincronización
                self.broker_socket.send_multipart(message)
            except zmq.ZMQError as e:
                print(f"Broker error: {e}")

    def start(self):
        threading.Thread(target=self.send_heartbeat).start()
        self.forward_messages()

if __name__ == "__main__":
    broker = Broker(port=5557, heartbeat_port=5562)
    broker.start()
