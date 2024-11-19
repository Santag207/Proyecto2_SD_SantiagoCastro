import zmq
import threading
import json
import time

class CentralServer:
    def __init__(self, port, pub_port, backup_heartbeat_port, persistence_file="server_data.json"):
        self.context = zmq.Context()
        self.port = port
        self.pub_port = pub_port
        self.backup_heartbeat_port = backup_heartbeat_port
        self.persistence_file = persistence_file

        self.server_socket = self.context.socket(zmq.REP)
        self.server_socket.bind(f"tcp://localhost:{self.port}")
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(f"tcp://localhost:{self.pub_port}")
        self.heartbeat_socket = self.context.socket(zmq.PUSH)
        self.heartbeat_socket.connect(f"tcp://localhost:{self.backup_heartbeat_port}")

        self.taxis = {}
        self.metrics = {"services_successful": 0, "services_rejected": 0}
        self.load_data()

    def load_data(self):
        try:
            with open(self.persistence_file, "r") as file:
                data = json.load(file)
                self.taxis = data.get("taxis", {})
                self.metrics = data.get("metrics", {})
            print("Data loaded successfully.")
        except FileNotFoundError:
            print("No persistence data found. Starting fresh.")

    def save_data(self):
        with open(self.persistence_file, "w") as file:
            json.dump({"taxis": self.taxis, "metrics": self.metrics}, file)
        self.pub_socket.send_json({"action": "register", "data": self.taxis})

    def send_heartbeat(self):
        while True:
            self.heartbeat_socket.send_string("heartbeat")
            time.sleep(2)

    def start(self):
        print(f"Server running on port {self.port}.")
        threading.Thread(target=self.send_heartbeat).start()
        self.handle_requests()

    def handle_requests(self):
        while True:
            message = self.server_socket.recv_pyobj()
            response = None
            if message["type"] == "register":
                response = self.register_taxi(message["data"])
            elif message["type"] == "request":
                response = self.assign_taxi(message["data"])
            self.server_socket.send_pyobj(response)

    def register_taxi(self, data):
        taxi_id, position = data["id"], data["position"]
        self.taxis[taxi_id] = {"position": position, "status": "available"}
        self.save_data()
        return f"Taxi {taxi_id} registered successfully."

    def assign_taxi(self, data):
        user_position = data["position"]
        available_taxis = {k: v for k, v in self.taxis.items() if v["status"] == "available"}
        if not available_taxis:
            self.metrics["services_rejected"] += 1
            return {"status": "failed", "reason": "No taxis available"}

        nearest_taxi = min(
            available_taxis,
            key=lambda k: abs(user_position[0] - available_taxis[k]["position"][0]) +
                          abs(user_position[1] - available_taxis[k]["position"][1])
        )
        self.taxis[nearest_taxi]["status"] = "busy"
        self.metrics["services_successful"] += 1
        self.save_data()
        return {"status": "success", "taxi_id": nearest_taxi}

if __name__ == "__main__":
    server = CentralServer(port=5555, pub_port=5559, backup_heartbeat_port=5561)
    server.start()
