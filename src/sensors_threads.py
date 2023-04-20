import threading
import time
import uuid
import random
from dataclasses import dataclass, asdict
from typing import List, Callable

import requests

from src.errors import EventTypeError
import queue


HEADERS = {"Content-Type": "application/json"}
URL = "https://en6msadu8lecg.x.pipedream.net/"


@dataclass
class Event:
    type: str
    readings: List[int]

    def __post_init__(self):
        if self.type not in ("nominal", "info", "warning", "error", "critical"):
            raise EventTypeError("Event type error")


@dataclass
class SensorMessage:
    id: str
    event: Event
    timestamp: int


class Sensor:
    def __init__(self):
        self.sensor_id = str(uuid.uuid4())
        print(f"Created sensor: {self.sensor_id}")

    def _event_type(self) -> str:
        event_types = ["nominal", "info", "warning", "error", "critical"]
        return random.choices(event_types, cum_weights=[60, 24, 10, 5, 1], k=1)[0]

    @property
    def state(self) -> SensorMessage:
        return SensorMessage(
            self.sensor_id,
            Event(
                self._event_type(), readings=[random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)]
            ),
            int(time.time()),
        )


def send_state(sensor_queue: queue.Queue) -> None:
    attempts = 0
    while True:
        with sensor_queue.mutex:
            reading = sensor_queue.queue[0] if not sensor_queue.empty() else None
        if reading is None:
            sensor_queue.get()
            break
        response = requests.post(URL, json=asdict(reading), headers=HEADERS)
        if response.status_code != 200:
            attempts += 1
            if attempts > 3:
                raise TimeoutError
        else:
            attempts = 0
            sensor_queue.get()

        time.sleep(0.5)


def sensor_producer(sensor: Sensor, sensor_queue: queue.Queue, total_elements: int) -> None:
    for i in range(total_elements):
        sensor_queue.put(sensor.state)
        time.sleep(random.uniform(0.1, 1.5))


def main() -> None:
    sensor_queue: queue.Queue = queue.Queue()
    sensor = Sensor()

    producer = threading.Thread(
        target=sensor_producer,
        args=(
            sensor,
            sensor_queue,
            5,
        ),
    )
    consumer = threading.Thread(target=send_state, args=(sensor_queue,))

    producer.start()
    consumer.start()

    producer.join()

    sensor_queue.put(None)
    consumer.join()


if __name__ == "__main__":
    main()
