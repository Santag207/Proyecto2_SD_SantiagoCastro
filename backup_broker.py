import zmq
import threading
import time

class BackupBroker:
    def __init__(self, port, heartbeat_port):
        self.context = zmq.Context()
        self.broker_socket = self.context.socket(zmq.ROUTER)
        self.broker_socket.bind(f"tcp://localhost:{port}")
        self.heartbeat_socket = self.context.socket(zmq.PULL)
        self.heartbeat_socket.bind(f"tcp://localhost:{heartbeat_port}")
        self.is_active = False
        self.message_buffer = []

    def monitor_heartbeat(self):
        while True:
            try:
                self.heartbeat_socket.recv_string(flags=zmq.NOBLOCK)
                print("Heartbeat received from primary broker.")
                self.is_active = False
            except zmq.Again:
                print("Primary broker heartbeat missed. Activating backup broker.")
                self.is_active = True
            time.sleep(3)

    def forward_messages(self):
        while True:
            if not self.is_active:
                continue
            for message in self.message_buffer:
                self.broker_socket.send_multipart(message)
            self.message_buffer.clear()

            try:
                message = self.broker_socket.recv_multipart()
                print(f"Backup Broker received: {message}")
                self.broker_socket.send_multipart(message)
            except zmq.ZMQError as e:
                print(f"Backup Broker error: {e}")

    def start(self):
        threading.Thread(target=self.monitor_heartbeat).start()
        self.forward_messages()

if __name__ == "__main__":
    backup_broker = BackupBroker(port=5558, heartbeat_port=5562)
    backup_broker.start()
