import AcisCanTools
from AcisCanTools import utils as utl

test = AcisCanTools.Parser(interface=utl.get_can_interface(), mode="logging", parse_type="smart_nox")