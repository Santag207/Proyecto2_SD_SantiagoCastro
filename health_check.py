import zmq
import time
import threading

class HealthCheck:
    def __init__(self, primary_server, backup_server, primary_broker, backup_broker):
        self.context = zmq.Context()
        self.primary_server = primary_server
        self.backup_server = backup_server
        self.primary_broker = primary_broker
        self.backup_broker = backup_broker
        self.active_server = primary_server
        self.active_broker = primary_broker

        # Sockets to check servers and brokers
        self.server_socket = self.context.socket(zmq.REQ)
        self.server_socket.connect(f"tcp://localhost:{self.primary_server}")

        self.broker_socket = self.context.socket(zmq.REQ)
        self.broker_socket.connect(f"tcp://localhost:{self.primary_broker}")

        # PUB socket to notify clients
        self.notification_socket = self.context.socket(zmq.PUB)
        self.notification_socket.bind("tcp://localhost:5560")

    def monitor_servers(self):
        while True:
            try:
                self.server_socket.send_string("ping")
                response = self.server_socket.recv_string(flags=zmq.NOBLOCK)
                if response != "pong":
                    raise zmq.ZMQError
                print(f"Primary server {self.primary_server} is healthy.")
            except zmq.ZMQError:
                print(f"Primary server failed. Switching to backup server {self.backup_server}.")
                self.active_server = self.backup_server
                self.server_socket.disconnect(f"tcp://localhost:{self.primary_server}")
                self.server_socket.connect(f"tcp://localhost:{self.backup_server}")
                self.notify_clients()

            time.sleep(5)

    def monitor_servers(self):
        while True:
            fail_count = 0
            while fail_count < 3:  # Retry 3 times before declaring failure
                try:
                    self.server_socket.send_string("ping")
                    response = self.server_socket.recv_string(flags=zmq.NOBLOCK)
                    if response == "pong":
                        self.status["servers"][self.primary_server] = "active"
                        fail_count = 0
                        break
                except zmq.Again:
                    fail_count += 1
                    time.sleep(1)

            if fail_count >= 3:
                print("Primary server failed. Switching to backup server.")
                self.status["servers"][self.primary_server] = "inactive"
                self.status["servers"][self.backup_server] = "active"


    def notify_clients(self):
        self.notification_socket.send_json({
            "active_server": self.active_server,
            "active_broker": self.active_broker
        })
        print(f"Notified clients: Server {self.active_server}, Broker {self.active_broker}.")

    def start(self):
        threading.Thread(target=self.monitor_servers).start()
        threading.Thread(target=self.monitor_brokers).start()

if __name__ == "__main__":
    health_check = HealthCheck(
        primary_server=5555, backup_server=5556,
        primary_broker=5557, backup_broker=5558
    )
    health_check.start()
