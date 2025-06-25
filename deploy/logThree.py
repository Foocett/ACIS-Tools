from AcisCanTools import Parser
loggerThree = Parser(interface="can0", mode="logging", output_type="csv", output_path="/unattendLog", output_name="parsedLog_reduced_30_mins", reduced=False)
loggerThree.configure_smart_nox_output()
loggerThree.beginLogging()