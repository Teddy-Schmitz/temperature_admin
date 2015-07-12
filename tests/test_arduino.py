import pytest


@pytest.mark.json_data('{ "Bad data": asdfa')
def test_arduino_bad_data(arduino):
    with pytest.raises(ValueError):
        arduino.turn_off()


@pytest.mark.json_data('{ "Good data": "asdfa"}')
def test_arduino_good_data(arduino):
    arduino.turn_on()


@pytest.mark.json_data('{"temperature": 23.43}')
def test_arduino_good_temperature(arduino):
    temp = arduino.check_temps()

    assert temp is not None
    assert temp == 23.43


@pytest.mark.json_data('{"humidity": 23.43}')
def test_arduino_bad_temperature(arduino):
    with pytest.raises(KeyError):
        arduino.check_temps()


@pytest.mark.json_data('{"humidity": 34.43}')
def test_arduino_good_humidity(arduino):
    h = arduino.check_humidity()

    assert h is not None
    assert h == 34.43


@pytest.mark.json_data('{"temperature": 34.43}')
def test_arduino_bad_humidity(arduino):
    with pytest.raises(KeyError):
        arduino.check_humidity()
