from AcisCanTools import Parser

loggerTwo = Parser(interface="can0", mode="logging", output_type="csv", output_path="/unattendLog", output_name="parsedLog_reduced_30_mins", reduced=True)
loggerTwo.configure_smart_nox_output()
loggerTwo.beginLogging()