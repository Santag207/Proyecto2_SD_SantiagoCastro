import zmq

def iniciar_broker():
    contexto = zmq.Context()

    # Socket SUB para recibir mensajes de los taxis
    subscripcion = contexto.socket(zmq.XSUB)
    subscripcion.bind("tcp://*:7005")  # Puerto actualizado

    # Socket PUB para enviar mensajes al servidor principal
    publicacion = contexto.socket(zmq.XPUB)
    publicacion.bind("tcp://*:7006")  # Puerto actualizado

    print("Broker en ejecución – esperando mensajes...")

    try:
        zmq.proxy(subscripcion, publicacion)
    except Exception as error:
        print(f"Error en el proxy del broker: {error}")
    finally:
        subscripcion.close()
        publicacion.close()
        contexto.term()

if __name__ == "__main__":
    iniciar_broker()
