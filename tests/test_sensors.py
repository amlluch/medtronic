from unittest.mock import patch, Mock

from src.sensors import send_state, Sensor


def test_send_state_mocked():
    mock_response = Mock()
    mock_response.status_code = 200

    sensor = Sensor()
    sensor._event_type = Mock(return_value="example_event")

    with patch('src.sensors.requests.post', return_value=mock_response):
        result = send_state(sensor.state)

        assert result == 200
