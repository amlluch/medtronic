import queue
import time
import uuid
from dataclasses import asdict
from unittest.mock import Mock, patch

import pytest

from src.errors import EventTypeError
from src.sensors_threads import Sensor, send_state
from src.sensors_threads import Event, SensorMessage, sensor_producer


def test_can_instantiate_event() -> None:
    # Given
    event = {"type": "nominal", "readings": [0, 1, 2]}

    # When
    event = Event(**event)

    # Then
    assert event.type == 'nominal'
    assert event.readings == [0, 1, 2]


def test_wrong_type_event_fails() -> None:
    # Given
    event = {"type": "non-existing-type", "readings": [0, 1, 2]}

    # Then
    with pytest.raises(EventTypeError):
        Event(**event)


def test_can_instantiate_sensor_message() -> None:
    # Given
    event = {"type": "nominal", "readings": [0, 1, 2]}
    sensor_message = {"id": str(uuid.uuid4()), "event": Event(**event), "timestamp": int(time.time())}

    # When
    sensor_message_object = SensorMessage(**sensor_message)

    # Then
    assert sensor_message_object.event.type == 'nominal'
    assert isinstance(sensor_message_object.id, str)


def test_can_serialise_sensor_message() -> None:
    # Given
    event = {"type": "nominal", "readings": [0, 1, 2]}
    sensor_message = {"id": str(uuid.uuid4()), "event": Event(**event), "timestamp": int(time.time())}
    sensor_message_object = SensorMessage(**sensor_message)

    # When
    serialised = asdict(sensor_message_object)

    # Then
    assert "event" in serialised
    assert "type" in serialised["event"]


def test_sensor_producer() -> None:
    # Given
    sensor = Sensor()

    sensor._event_type = Mock(return_value="nominal")

    sensor_queue = queue.Queue()
    total_elements = 5

    # When
    sensor_producer(sensor, sensor_queue, total_elements)

    # Then
    assert sensor_queue.qsize() == total_elements

    for _ in range(total_elements):
        sensor_state = sensor_queue.get()

        assert isinstance(sensor_state, SensorMessage)

        assert sensor_state.id == sensor.sensor_id
        assert isinstance(sensor_state.event, Event)
        assert sensor_state.event.type == "nominal"
        assert isinstance(sensor_state.event.readings, list)
        assert len(sensor_state.event.readings) == 3
        assert isinstance(sensor_state.timestamp, int)


def test_send_state():
    # Given
    sensor = Sensor()
    example_event = Event(type="nominal", readings=[1, 2, 3])
    sensor_state = SensorMessage(id=sensor.sensor_id, event=example_event, timestamp=1234567890)

    sensor_queue = queue.Queue()
    sensor_queue.put(sensor_state)

    mock_response = Mock()
    mock_response.status_code = 200

    # When
    with patch("requests.post", return_value=mock_response):
        from threading import Thread
        sender_thread = Thread(target=send_state, args=(sensor_queue,), daemon=True)
        sender_thread.start()

        sensor_queue.put(None)
        sender_thread.join()

    # Then
    assert sensor_queue.empty()
