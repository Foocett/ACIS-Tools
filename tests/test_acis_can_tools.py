import pytest
from unittest.mock import patch, MagicMock
import sys
import types

# Import the module under test
import AcisCanTools

# --- Parser class tests ---
def test_parser_init_defaults():
    # Patch can.Bus to avoid hardware dependency
    with patch('AcisCanTools.can.Bus'):
        parser = AcisCanTools.Parser()
        assert parser.parse_type == 'smart_nox'
        assert parser.reduced_output is False
        assert parser.configured_for == []
        assert parser.mode in ['logged', 'stream']

def test_parser_invalid_parse_type():
    with patch('AcisCanTools.can.Bus'):
        with pytest.raises(ValueError):
            AcisCanTools.Parser(parse_type='invalid_type')

def test_parser_reduced_output_type_error():
    with patch('AcisCanTools.can.Bus'):
        with pytest.raises(TypeError):
            AcisCanTools.Parser(reduced_output='not_bool')

def test_configure_smart_nox_output_flags():
    with patch('AcisCanTools.can.Bus'):
        parser = AcisCanTools.Parser()
        parser.configure_smart_nox_output(nox_raw=False, o2_raw=True, status=False, heater=True, error_nox=False, error_o2=True)
        assert parser.nox_raw is False
        assert parser.o2_raw is True
        assert parser.status is False
        assert parser.heater is True
        assert parser.error_nox is False
        assert parser.error_o2 is True

def test_smart_nox_decode_all_true():
    with patch('AcisCanTools.can.Bus'):
        parser = AcisCanTools.Parser()
        parser.configure_smart_nox_output(nox_raw=True, o2_raw=True, status=True, heater=True, error_nox=True, error_o2=True)
        data = bytes([1,2,3,4,5,6,7,8])
        result = parser._smart_nox_decode(data)
        assert result == (513, 1027, 5, 6, 7, 8)

def test_smart_nox_decode_some_false():
    with patch('AcisCanTools.can.Bus'):
        parser = AcisCanTools.Parser()
        parser.configure_smart_nox_output(nox_raw=False, o2_raw=True, status=False, heater=True, error_nox=False, error_o2=True)
        data = bytes([1,2,3,4,5,6,7,8])
        result = parser._smart_nox_decode(data)
        assert result == (0, 1027, 0, 6, 0, 8)

# --- utils.static_decode tests ---
def test_static_decode_valid():
    data = bytes([1,2,3,4,5,6,7,8])
    result = AcisCanTools.utils.static_decode(data=data, device='smart_nox')
    assert result == (513, 1027, 5, 6, 7, 8)

def test_static_decode_invalid_device():
    data = bytes([1,2,3,4,5,6,7,8])
    with pytest.raises(ValueError):
        AcisCanTools.utils.static_decode(data=data, device='unknown')

def test_static_decode_no_data():
    with pytest.raises(ValueError):
        AcisCanTools.utils.static_decode(data=None, device='smart_nox')

# --- utils.get_can_interface tests ---
def test_get_can_interface_returns_interface():
    fake_output = '3: can0: <NOARP,UP,LOWER_UP,ECHO> mtu 16\n4: vcan0: <NOARP,DOWN> mtu 16\n'
    with patch('AcisCanTools.subprocess.check_output', return_value=fake_output):
        iface = AcisCanTools.utils.get_can_interface(verbose=False)
        assert iface == 'can0'

def test_get_can_interface_no_interfaces():
    with patch('AcisCanTools.subprocess.check_output', return_value=''):
        iface = AcisCanTools.utils.get_can_interface(verbose=False)
        assert iface == ''

def test_get_can_interface_exception():
    with patch('AcisCanTools.subprocess.check_output', side_effect=Exception('fail')):
        iface = AcisCanTools.utils.get_can_interface(verbose=False)
        assert iface == ''

# --- utils.check_can_status tests ---
def test_check_can_status_up():
    fake_output = '3: can0: <NOARP,UP,LOWER_UP,ECHO> mtu 16\n4: vcan0: <NOARP,DOWN> mtu 16\n'
    with patch('AcisCanTools.subprocess.check_output', return_value=fake_output):
        status = AcisCanTools.utils.check_can_status()
        assert status == 'UP'

def test_check_can_status_down():
    fake_output = '3: can0: <NOARP,DOWN> mtu 16\n'
    with patch('AcisCanTools.subprocess.check_output', return_value=fake_output):
        status = AcisCanTools.utils.check_can_status()
        assert status == 'DOWN'

def test_check_can_status_none():
    with patch('AcisCanTools.subprocess.check_output', return_value=''):
        status = AcisCanTools.utils.check_can_status()
        assert status is None

def test_check_can_status_exception():
    with patch('AcisCanTools.subprocess.check_output', side_effect=Exception('fail')):
        status = AcisCanTools.utils.check_can_status()
        assert status is None
