import zmq
import json
import threading

class BackupServer:
    def __init__(self, port, sub_port, heartbeat_port, persistence_file="server_backup_data.json"):
        self.context = zmq.Context()
        self.port = port  # Puerto para recibir solicitudes
        self.sub_port = sub_port  # Puerto para recibir sincronizaciones del servidor principal
        self.heartbeat_port = heartbeat_port  # Puerto para recibir heartbeats
        self.persistence_file = persistence_file

        # Sockets
        self.server_socket = self.context.socket(zmq.REP)  # Para manejar solicitudes
        self.server_socket.bind(f"tcp://localhost:{self.port}")
        self.sub_socket = self.context.socket(zmq.SUB)  # Para recibir sincronización de datos
        self.sub_socket.connect(f"tcp://localhost:{self.sub_port}")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Suscribirse a todos los mensajes
        self.heartbeat_socket = self.context.socket(zmq.PULL)  # Para recibir heartbeats del principal
        self.heartbeat_socket.bind(f"tcp://localhost:{self.heartbeat_port}")

        self.taxis = {}
        self.metrics = {"services_successful": 0, "services_rejected": 0}
        self.is_active = False
        self.load_data()

    def load_data(self):
        try:
            with open(self.persistence_file, "r") as file:
                data = json.load(file)
                self.taxis = data.get("taxis", {})
                self.metrics = data.get("metrics", {})
            print("Backup Server: Data loaded.")
        except FileNotFoundError:
            print("Backup Server: No persistence data. Starting fresh.")

    def save_data(self):
        with open(self.persistence_file, "w") as file:
            json.dump({"taxis": self.taxis, "metrics": self.metrics}, file)

    def monitor_heartbeat(self):
        while True:
            try:
                self.heartbeat_socket.recv_string(flags=zmq.NOBLOCK)
                print("Heartbeat received from primary server.")
                self.is_active = False
            except zmq.Again:
                print("Primary server heartbeat missed. Activating backup server.")
                self.is_active = True
            time.sleep(3)

    def sync_with_primary(self):
        """
        Sincroniza registros de taxis y otros datos importantes del servidor principal.
        """
        while True:
            try:
                message = self.sub_socket.recv_json(flags=zmq.NOBLOCK)
                if message["type"] == "register":  # Sincroniza el registro de taxis
                    taxi_id = message["id"]
                    position = message["position"]
                    self.taxis[taxi_id] = {"position": position, "status": "available"}
                    self.save_data()
                    print(f"Synced taxi {taxi_id} with position {position} from primary server.")
            except zmq.Again:
                pass
            time.sleep(0.5)

    def handle_requests(self):
        """
        Maneja las solicitudes de los usuarios solo si el servidor de respaldo está activo.
        """
        while True:
            if not self.is_active:
                continue  # Si no está activo, ignora las solicitudes
            message = self.server_socket.recv_pyobj()
            response = None
            if message["type"] == "request":
                response = self.assign_taxi(message["data"])
            self.server_socket.send_pyobj(response)

    def start(self):
        """
        Inicia el servidor de respaldo.
        """
        print(f"Backup Server running on port {self.port}.")
        threading.Thread(target=self.monitor_heartbeat).start()
        threading.Thread(target=self.sync_with_primary).start()
        self.handle_requests()

if __name__ == "__main__":
    backup_server = BackupServer(
        port=5556,
        sub_port=5559,  # Puerto donde escucha los datos del servidor principal
        heartbeat_port=5561  # Puerto donde recibe heartbeats
    )
    backup_server.start()
