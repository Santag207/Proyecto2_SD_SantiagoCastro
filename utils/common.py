def read_config():
  # reads the client configuration from client.properties
  # and returns it as a key-value map
    try:
        config = {}
        with open("client.properties") as fh:
            for line in fh:
                line = line.strip()
                if len(line) != 0 and line[0] != "#":
                    parameter, value = line.strip().split('=', 1)
                    config[parameter] = value.strip()
        return config
    except FileNotFoundError:
        print("No se encontró el archivo client.properties")
