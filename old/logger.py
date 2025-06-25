# logger.py
import can
import csv
import json
from time import time as t
from datetime import datetime
from warnings import warn
import os

class logger: 
    """
    A class to log CAN messages from a network specified interface using the socketcan bustype.\n
    This class supports both raw data logging and acting as a datastream object to be passes into other methods

    Attributes:
        interface (str): The CAN interface to log from (default: 'can0').
        mode (str): The logging mode, either 'stream' or 'logging' (default: 'stream').
        kwargs (dict): Additional keyword arguments, related for logging mode, more in constructor docstring.
    """
    def __init__(self, interface='can0', mode='logging', **kwargs):
        """
        Initializes the CANLogger with the specified interface and mode.\n
        Keyword Args: \n
            \toutput_type (str): The type of output, either 'csv' or 'json' (default: 'csv'). \n
            \toutput_location (str): The relative location to save the output file (default: current dir).\n
            \toutput_name (str): The name of the output file (default: can_log_{timestamp}).
        """
        acceptable_stream_aliases = [
            'stream', 'datastream', 'streaming', 's', 'strm', 'streem', 'strema', 'strem',
            'data-stream', 'data_stream', 'data strm', 'data', 'live', 'livestream', 'live-stream',
            'realtime', 'real-time', 'on-the-fly', 'onfly', 'on_the_fly', 'on the fly',
            'stremaing', 'streming', 'stremm', 'stremming', 'streeming', 'stremaing',
            'strema', 'strea', 'strem', 'stremm', 'streming', 'stremaing',
            'stram', 'strem', 'stremm', 'streming', 'stremaing',
            'sream', 'sreaming', 'sreamm', 'sreamming',
        ]
        acceptable_logged_aliases = [
            'logged', 'log', 'logging', 'l', 'loged', 'loggin', 'logg', 'loggng',
            'logfile', 'log-file', 'log_file', 'log file', 'save', 'saved', 'record', 'recorded',
            'rec', 'recrod', 'recroded', 'recoding', 'recod', 'recodring',
            'archived', 'archive', 'archiv', 'archiving', 'archve', 'archveing',
            'persist', 'persistent', 'persisted', 'persisting',
            'file', 'tofile', 'to_file', 'to-file', 'to file',
            'looged', 'looging', 'loog', 'loogin', 'looged',
        ]
        accepable_kwargs = [
            'output_type', 'output_location', 'output_name'
        ]
    
        # Parameters
        self.active = False
        # Collect arguments
        self.interface = interface
        self.output_type = kwargs.get('output_type', 'csv')
        self.output_name = kwargs.get('output_name', f"can_log_{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        self.output_location = kwargs.get('output_location', os.getcwd())
        # Mode normalization and validation
        if mode in acceptable_stream_aliases:
            self.mode = 'stream'
        elif mode in acceptable_logged_aliases:
            self.mode = 'logged'
        else:
            raise ValueError(f"Mode '{mode}' is not recognized. Use either 'stream' or 'logged'.")

        # Validate arguments
        for keyword in kwargs:
            if keyword not in accepable_kwargs:
                warn(f"Invalid keyword argument: {keyword}, ignoring. \nAcceptable arguments are: {', '.join(accepable_kwargs)}", UserWarning)

        if self.mode == 'stream':
            if len(kwargs) > 0:
                warn("Provided keyword arguments will be ignored in stream mode", UserWarning)
        if self.mode == 'logged':
            # Warn if the user did not provide these values (i.e., they are set to the default)
            if 'output_type' not in kwargs:
                warn(f"output_type not provided, defaulting to '{self.output_type}'.", UserWarning)
            if 'output_location' not in kwargs:
                warn(f"output_location not provided, defaulting to '{self.output_location}'.", UserWarning)
            if 'output_name' not in kwargs:
                warn(f"output_name not provided, defaulting to '{self.output_name}'.", UserWarning)
            if self.output_type not in ['csv', 'json']:
                raise ValueError("output_type must be either 'csv' or 'json'.")
            if not os.path.exists(self.output_location):
                warn(f"Output location '{self.output_location}' does not exist. Creating it.", UserWarning)
                os.makedirs(self.output_location)
        
        # Initialize CAN bus
        if self.mode == 'logged':
            self.output_file = os.path.join(self.output_location, f"{self.output_name}.{self.output_type}")
        # Init
        self.bus = can.Bus(channel=self.interface, interface='socketcan')

        if self.mode == 'logged':
            if self.output_type == 'csv':
                self._run_csv_logging()
            elif self.output_type == 'json':
                self._run_json_logging()
        elif self.mode == 'stream':
            pass

    def __del__(self):
        """
        Destructor to ensure any open file handles are closed when the object is deleted.
        """
        self.close()
        print("CANLogger instance deleted and resources cleaned up.")

    def beginLogging(self):
        """
        Start or resume logging. If already active, does nothing.
        """
        if self.mode != 'logged':
            warn("beginLogging() can only be called in 'logged' mode.", UserWarning)
            return
        if self.active:
            warn("Logging is already active.", UserWarning)
            return
        self.active = True
        if self.mode == 'logged':
            if self.output_type == 'csv':
                if not hasattr(self, '_csvfile'):
                    self._csvfile = open(self.output_file, mode='a', newline='')
                    self._csvwriter = csv.writer(self._csvfile)
                    if self._csvfile.tell() == 0:
                        self._csvwriter.writerow(['No.', 'Time', 'Snd/Rc', 'Dest', 'Src', 'Priority', 'PGN', 'Data'])
                self._run_csv_logging()
            elif self.output_type == 'json':
                if not hasattr(self, '_jsonfile'):
                    self._jsonfile = open(self.output_file, mode='a+')
                    self._jsonfile.seek(0, os.SEEK_END)
                    if self._jsonfile.tell() == 0:
                        self._jsonfile.write('[')
                    else:
                        self._jsonfile.seek(self._jsonfile.tell() - 1)
                        self._jsonfile.truncate()
                        self._jsonfile.write(',')
                self._run_json_logging()

    def pauseLogging(self):
        """
        Pause logging. Logging can be resumed later by calling begin().
        """
        if self.mode != 'logged':
            warn("pauseLogging() can only be called in 'logged' mode.", UserWarning)
            return
        if not self.active:
            warn("Logging is already paused.", UserWarning)
            return
        self.active = False

    def _run_csv_logging(self):
        msg_count = 0
        start_time = t()
        try:
            while self.active:
                msg = self.bus.recv(timeout=1)
                if msg:
                    msg_count += 1
                    rel_time = msg.timestamp - start_time
                    snd_rc = 'Receive'
                    if msg.is_extended_id:
                        priority, pgn, src, dest = self._parse_j1939_id(msg.arbitration_id)
                    else:
                        priority = pgn = src = dest = ''
                    self._csvwriter.writerow([
                        msg_count,
                        f"{rel_time:.3f}",
                        snd_rc,
                        dest,
                        src,
                        priority,
                        pgn,
                        msg.data.hex(' ').upper()
                    ])
        except KeyboardInterrupt:
            print("Logging stopped by user.")

    def _run_json_logging(self):
        msg_count = 0
        start_time = t()
        try:
            first = True
            while self.active:
                msg = self.bus.recv(timeout=1)
                if msg:
                    msg_count += 1
                    rel_time = msg.timestamp - start_time
                    snd_rc = 'Receive'
                    if msg.is_extended_id:
                        priority, pgn, src, dest = self._parse_j1939_id(msg.arbitration_id)
                    else:
                        priority = pgn = src = dest = ''
                    entry = json.dumps({
                        'No.': msg_count,
                        'Time': f"{rel_time:.3f}",
                        'Snd/Rc': snd_rc,
                        'Dest': dest,
                        'Src': src,
                        'Priority': priority,
                        'PGN': pgn,
                        'Data': msg.data.hex(' ').upper()
                    })
                    if not first:
                        self._jsonfile.write(',\n')
                    self._jsonfile.write(entry)
                    self._jsonfile.flush()
                    first = False
        except KeyboardInterrupt:
            print("Logging stopped by user.")

    def close(self):
        """
        Close any open file handles. Should be called when done logging.
        """
        if hasattr(self, '_csvfile'):
            self._csvfile.close()
            del self._csvfile
            del self._csvwriter
        if hasattr(self, '_jsonfile'):
            self._jsonfile.write(']')
            self._jsonfile.close()
            del self._jsonfile

    def read(self, timeout=1):
        """
        Read a CAN message from the bus. This is a wrapper for self.bus.recv().
        Args:
            timeout (float): Time in seconds to wait for a message. Default is 1 second.
        Returns:
            can.Message or None: The received CAN message, or None if timeout occurs.
        """
        if self.mode != 'stream':
            warn("read() can only be called in 'stream' mode.", UserWarning)
            return None
        return self.bus.recv(timeout=timeout)

    def _parse_j1939_id(self, arbitration_id):
        """
        Parse a 29-bit J1939 CAN identifier into its component fields.

        The J1939 protocol encodes several fields into a single 29-bit CAN identifier. To extract these fields,
        we use bitwise operations to shift to the start point then use a bitwise AND operation to mask the relevant bits.

        - Priority (3 bits): Bits 26-28.
        - PGN (Parameter Group Number, 18 bits): Bits 8-25.
        - Source Address (8 bits): Bits 0-7.
        - PDU Format (8 bits): Bits 16-23.
        - Destination Address (8 bits): For PDU1 format (PDU Format < 240), bits 8-15 are the destination address (shift right by 8, mask with 0xFF). For PDU2 format (PDU Format >= 240), destination is broadcast (255).

        Args:
            arbitration_id (int): The 29-bit CAN identifier.
        Returns:
            tuple: (priority, pgn, src, dest)
        """
        priority = (arbitration_id >> 26) & 0x7  # Extract bits 26-28 for priority
        pgn = (arbitration_id >> 8) & 0x3FFFF    # Extract bits 8-25 for PGN
        src = arbitration_id & 0xFF              # Extract bits 0-7 for source address
        pdu_format = (arbitration_id >> 16) & 0xFF  # Extract bits 16-23 for PDU format
        if pdu_format < 240:
            dest = (arbitration_id >> 8) & 0xFF  # Extract bits 8-15 for destination address
        else:
            dest = 255  # Broadcast or not applicable
        return priority, pgn, src, dest

if __name__ == "__main__":
    # Example usage
    #logger = logger(interface='can0', mode='logging', output_type='csv', output_location='./logs', output_name='can_log_test')
    stream = logger(interface='can0', mode='stream')
    print(f"CAN Logger initialized with interface: {stream.interface}, mode: {stream.mode}, output file: None (stream mode)")
    
    while True:
        msg = stream.read(timeout=1)
        if msg:
            print(f"Received message: {msg}")
        else:
            print("No message received within timeout period.")
    # You can now use logger.bus to receive messages and log them as needed.
    # This is just a setup example; actual logging functionality would be implemented in methods of the class.