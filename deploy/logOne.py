from AcisCanTools import Logger
loggerOne = Logger(interface="can0", mode="logging", output_type="csv", output_path="/unattendLog", output_name="rawData_30_mins")
loggerOne.beginLogging()