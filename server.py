from confluent_kafka import Consumer, Producer
from utils.common import read_config
import json
import os
import csv
import time

# Utility Functions for File Persistence

def save_to_csv(file_name, data, headers=None):
    file_exists = os.path.exists(file_name)
    with open(file_name, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists and headers:
            writer.writeheader()  # Write headers only once
        writer.writerow(data)

def save_to_json(file_name, data):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            json.dump([], file)

    with open(file_name, 'r+') as file:
        existing_data = json.load(file)
        existing_data.append(data)
        file.seek(0)
        json.dump(existing_data, file, indent=4)

def backup_system(file_name, data):
    backup_file = f"{file_name}.backup"
    save_to_json(backup_file, data)
    print(f"Backup saved to {backup_file}")

def log_metrics(event, start_time):
    elapsed_time = time.time() - start_time
    data = {
        "event": event,
        "timestamp": time.time(),
        "elapsed_time": elapsed_time
    }
    save_to_json("metrics.json", data)
    print(f"Metrics logged: {data}")

def calculate_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def simulate_service_time(taxi_id, start_position, end_position):
    distance = calculate_distance(*start_position, *end_position)
    service_time = distance * 0.5  # 0.5 seconds per unit distance
    print(f"Simulating service time for taxi {taxi_id}: {service_time} seconds")
    time.sleep(service_time)
    return service_time

# Server Logic

def find_nearest_taxi(user_x, user_y, active_taxis):
    min_distance = float('inf')
    nearest_taxi_id = None
    for taxi_id, (x, y) in active_taxis.items():
        distance = abs(user_x - x) + abs(user_y - y)
        if distance < min_distance:
            min_distance = distance
            nearest_taxi_id = taxi_id
    return nearest_taxi_id

def master_server(kafka_config):
    consumer = Consumer({
        **kafka_config,
        'group.id': 'master-consumer-group',
        'auto.offset.reset': 'earliest'
    })
    producer = Producer(kafka_config)

    consumer.subscribe(["taxi_positions", "user_requests"])

    active_taxis = {}  # Store active taxi positions

    try:
        while True:
            start_time = time.time()
            msg = consumer.poll(1.0)  # Wait up to 1 second for a message
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            topic = msg.topic()
            key = msg.key().decode('utf-8') if msg.key() else None
            try:
                value = json.loads(msg.value().decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"Malformed message received: {msg.value()}. Error: {e}")
                continue

            if topic == "taxi_positions":
                # Update active taxis
                try:
                    x, y = value['x'], value['y']
                    active_taxis[value['taxi_id']] = (x, y)

                    # Save position to file
                    save_to_csv("taxi_positions.csv", {
                        "taxi_id": value['taxi_id'],
                        "x": x,
                        "y": y,
                        "status": value.get('status', 'unknown')
                    }, headers=["taxi_id", "x", "y", "status"])
                    log_metrics("taxi_position_update", start_time)
                    print(f"Updated position for taxi {value['taxi_id']}: {active_taxis[value['taxi_id']]}")
                except KeyError as e:
                    print(f"Malformed taxi position message: {value}. Missing key: {e}")
                    backup_system("taxi_positions", value)

            elif topic == "user_requests":
                # Find nearest taxi for the user
                try:
                    nearest_taxi_id = find_nearest_taxi(value['x'], value['y'], active_taxis)

                    if nearest_taxi_id:
                        service_time = simulate_service_time(nearest_taxi_id, active_taxis[nearest_taxi_id], (value['x'], value['y']))
                        assignment = {
                            "user_id": value['user_id'],
                            "taxi_id": nearest_taxi_id,
                            "service_time": service_time
                        }
                        producer.produce("assignments", key=str(value['user_id']), value=json.dumps(assignment))
                        save_to_json("assignments.json", assignment)
                        log_metrics("taxi_assignment", start_time)
                        print(f"Assigned taxi {nearest_taxi_id} to user {value['user_id']}")
                    else:
                        print(f"No available taxis for user {value['user_id']}")
                except KeyError as e:
                    print(f"Malformed user request message: {value}. Missing key: {e}")

    except KeyboardInterrupt:
        print("Shutting down master server...")
    finally:
        consumer.close()

if __name__ == "__main__":
    kafka_config = read_config()
    master_server(kafka_config)
