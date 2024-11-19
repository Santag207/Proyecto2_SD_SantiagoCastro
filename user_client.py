from confluent_kafka import Producer
from utils.common import read_config    
import threading
import time
import random
import json

def send_user_request(user_id, position, kafka_config):
    producer = Producer(kafka_config)

    # Create the user request payload
    user_request = {
        "user_id": user_id,
        "x": position[0],
        "y": position[1]
    }

    # Send the request to the 'user_requests' topic
    producer.produce("user_requests", key=str(user_id), value=json.dumps(user_request))
    producer.flush()
    print(f"User {user_id} sent request: {user_request}")

def simulate_multiple_users(num_users, kafka_config):
    threads = []

    for user_id in range(1, num_users + 1):
        # Generate a random position within a 10x10 grid
        position = (random.randint(0, 9), random.randint(0, 9))

        # Create a thread for each user to send requests
        thread = threading.Thread(target=send_user_request, args=(user_id, position, kafka_config))
        threads.append(thread)
        thread.start()

        time.sleep(0.5)  # Space out user requests

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":

    config = read_config()
    num_users = 10  # Number of users to simulate
    simulate_multiple_users(num_users, config)
