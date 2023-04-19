# Sensor Data Simulator

This program simulates a sensor producing events and sending them to a specified endpoint. The sensor generates events with random readings and event types, and these events are then consumed by a separate thread which sends them to the endpoint using HTTP POST requests.

## Installation

To install and manage dependencies for this project, we will use [Poetry](https://python-poetry.org/).

### Prerequisites

- Python 3.9 or higher
- Poetry (see the [official documentation](https://python-poetry.org/docs/#installation) for installation instructions)

### Installing Dependencies

1. Clone the repository:
- git clone https://github.com/amlluch/medtronic.git
- cd sensor-data-simulator

2. Install dependencies using Poetry:
- poetry install

## Running the Application

To run the application, first activate the virtual environment:
- python main.py

## Code Overview

The main components of the code are:

- `Event`: A dataclass representing an event, including its type and readings.
- `SensorMessage`: A dataclass representing a message sent by the sensor, including the sensor ID, event, and timestamp.
- `Sensor`: A class representing a sensor that generates random events.
- `send_state`: A function that sends sensor events from a queue to the specified endpoint.
- `sensor_producer`: A function that generates events and puts them into the queue.
- `main`: The main function that starts the producer and consumer threads and runs the application.

### Customizing the Application

You can customize the application by modifying the following variables:

- `URL`: Change this to the desired endpoint URL.
- `total_elements`: Change this in the `sensor_producer` function call inside `main` to control the number of events the sensor generates.
