from confluent_kafka import Producer
from utils.common import read_config
import time
import random
import json

def taxi_main(taxi_id, grid_size, kafka_config):
    producer = Producer(kafka_config)
    position = [random.randint(0, grid_size[0]-1), random.randint(0, grid_size[1]-1)]

    while True:
        # Move taxi randomly within the grid
        move = random.choice(['up', 'down', 'left', 'right'])
        if move == 'up' and position[1] < grid_size[1] - 1:
            position[1] += 1
        elif move == 'down' and position[1] > 0:
            position[1] -= 1
        elif move == 'left' and position[0] > 0:
            position[0] -= 1
        elif move == 'right' and position[0] < grid_size[0] - 1:
            position[0] += 1

        # Send position to Kafka topic
        taxi_position = {
            "taxi_id": taxi_id,
            "x": position[0],
            "y": position[1],
            "status": "available"
        }
        producer.produce("taxi_positions", key=str(taxi_id), value=json.dumps(taxi_position))

        print(f"Taxi {taxi_id} sent position: {taxi_position}")

        time.sleep(1)  # Simulate real-time updates

if __name__ == '__main__':
    taxi_id = 1
    grid_size = (10, 10)
    config = read_config()
    taxi_main(taxi_id, grid_size, config)