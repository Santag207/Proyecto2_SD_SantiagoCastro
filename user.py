import zmq
import time
import threading

class User:
    def __init__(self, user_id, position, timeout):
        self.user_id = user_id
        self.position = position
        self.timeout = timeout
        self.active_broker = "tcp://localhost:5557"

        self.context = zmq.Context()
        self.req_socket = self.context.socket(zmq.REQ)
        self.notification_socket = self.context.socket(zmq.SUB)
        self.notification_socket.connect("tcp://localhost:5560")
        self.notification_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    def reconnect_broker(self, new_broker):
        attempts = 0
        while attempts < 3:  # Retry up to 3 times
            try:
                self.req_socket.disconnect(self.active_broker)
                self.active_broker = new_broker
                self.req_socket.connect(self.active_broker)
                print(f"Reconnected to broker: {self.active_broker}")
                break
            except zmq.ZMQError as e:
                print(f"Retrying connection: Attempt {attempts + 1}")
                attempts += 1
                time.sleep(1)


    def listen_notifications(self):
        while True:
            message = self.notification_socket.recv_json()
            self.reconnect_broker(f"tcp://127.0.0.1:{message['active_broker']}")

    def request_taxi(self):
        print(f"User {self.user_id} requesting taxi from position {self.position}.")
        start_time = time.time()
        self.req_socket.send_json({
            "type": "request",
            "id": self.user_id,
            "position": self.position
        })
        try:
            self.req_socket.setsockopt(zmq.RCVTIMEO, self.timeout * 1000)
            response = self.req_socket.recv_json()
            elapsed_time = time.time() - start_time

            if response["status"] == "success":
                print(f"User {self.user_id} assigned taxi {response['taxi_id']} in {elapsed_time:.2f}s.")
            else:
                print(f"User {self.user_id} request failed: {response['reason']}.")
        except zmq.error.Again:
            print(f"User {self.user_id} timed out after {self.timeout}s.")

    def start(self):
        self.req_socket.connect(self.active_broker)
        threading.Thread(target=self.listen_notifications).start()
        self.request_taxi()

if __name__ == "__main__":
    user = User(user_id=1, position=(5, 5), timeout=5)
    user.start()
