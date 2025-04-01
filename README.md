# Proyecto2_SD_SantiagoCastro

## Features

- **Distributed Concepts Implementation:** Experimentation with node communication, synchronization, and fault tolerance.
- **Modular Architecture:** Organized structure to facilitate testing and future extensions.
- **Educational Focus:** Development centered on the learning and deep understanding of distributed systems.
- **Detailed Documentation:** Guides and instructions to replicate and understand each component of the system.

## Technologies Used

- **Programming Language:** [Specify the programming language used, e.g., Python/Java/C++].
- **Frameworks and Libraries:** [List any frameworks or libraries used, if applicable].
- **Development Tools:** Git, [other relevant tools such as Docker or testing frameworks].

## Project Structure

```
Proyecto2_SD_SantiagoCastro
├── .git copy
├── __pycache__
├── utils
│   └── __init__.py  (if present, or other utility files)
├── client.properties
├── metrics.json
├── server.py
├── slave.py
├── taxi_client.py
├── taxi_positions.backup
├── taxi_positions.csv
└── user_client.py
```

#### Detailed Breakdown
- .git copy
A backup or duplicate of the Git repository folder. This may be used for archival purposes or as a reference for the original Git configuration.

- pycache
A directory created by Python to store compiled bytecode files (.pyc). These files speed up the loading of modules and are automatically generated.

- utils/
This folder is intended for utility modules that provide helper functions or common code used across the project.

- init.py (inside utils):
This file makes the directory a Python package. It may also include initialization code for the utility functions.

- client.properties
A configuration file for client settings. It likely contains properties such as server addresses, ports, or other client-specific configurations needed to run the client components of your project.

- metrics.json
A JSON file that stores metrics or logging data. This might be used for monitoring performance, tracking events, or collecting statistics from your distributed system.

- server.py
The main script for the server component of your project. This file likely handles incoming requests, manages connections, and coordinates tasks among different nodes in the system.

- slave.py
A script that defines the behavior of a slave node in your distributed system. This might include processing tasks received from the server, handling computation, or managing local resources.

- taxi_client.py
A client-side script dedicated to managing taxi-related operations. This could involve sending requests to the server, processing taxi-related data, or interacting with other system components to simulate taxi operations.

- taxi_positions.backup
A backup file that likely stores previous or temporary data regarding taxi positions. This file can be used to restore or verify historical data in case of discrepancies.

- taxi_positions.csv
A CSV file that contains structured data about taxi positions. It is used to store, update, or analyze the geographical or operational data of taxis within the system.

- user_client.py
A client script that manages user interactions. It may handle user input, send requests to the server, or provide feedback based on the operations performed by the system.

## Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/Santag207/Proyecto2_SD_SantiagoCastro.git
   ```
2. **Install Dependencies:**
Follow the specific instructions to install the necessary dependencies. For example, if using Python:
  
  ```
  cd Proyecto2_SD_SantiagoCastro
  pip install -r requirements.txt
  ```

(Adjust these steps according to the programming language and development environment you are using.)

## Usage
1. **Configure the Environment:**
Ensure you have set up the runtime environment (environment variables, network configuration, etc.) according to the project’s requirements.

2. **Run the Application:**
Use the following command to start the project:
  ```
  [execution command, e.g., python main.py]
  ```

3. **Testing and Validation:**
It is recommended to run the tests to verify the proper functioning of the system:
  ```
  [command to run tests, e.g., pytest]
  ```
