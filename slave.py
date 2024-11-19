from concurrent.futures import ThreadPoolExecutor
import grpc
import taxi_service_pb2
import taxi_service_pb2_grpc
import threading

class BackupServiceServicer(taxi_service_pb2_grpc.BackupServiceServicer):
    def __init__(self):
        self.backup_data = []
        self._shutdown_event = threading.Event()

    def BackupData(self, request, context):
        if self._shutdown_event.is_set():
            context.abort(grpc.StatusCode.UNAVAILABLE, "Server shutting down")
        data = {
            'taxi_id': request.taxi_id,
            'x': request.x,
            'y': request.y,
            'user_id': request.user_id,
            'type': request.type
        }
        self.backup_data.append(data)
        print(f"Datos respaldados: {data}")
        return taxi_service_pb2.Ack(message="Datos respaldados")

    def stop(self):
        print("Deteniendo el servidor de respaldo...")
        self._shutdown_event.set()

def serve(port):
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    backup_servicer = BackupServiceServicer()
    taxi_service_pb2_grpc.add_BackupServiceServicer_to_server(backup_servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"Servidor de respaldo iniciado en el puerto {port}.")
    
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print(f"Servidor de respaldo en el puerto {port} apagándose...")
        backup_servicer.stop()
        server.stop(30)  # Esperar 30 segundos para que las operaciones en curso se completen
        print(f"Servidor de respaldo en el puerto {port} detenido.")

if __name__ == '__main__':
    serve(6001)  # Iniciar el servidor de respaldo en el puerto 6001
