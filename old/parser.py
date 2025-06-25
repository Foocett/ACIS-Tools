from logger import logger

class Parser:
    """
    
    """
    def __init__(self, datastream, **kwargs):
        if isinstance(datastream, logger):
            self.datastream = datastream
            if self.datastream.mode != "stream":
                raise ValueError("passed datastream object must be in 'stream' mode")
        else:
            raise TypeError("datastream must be an instance of CANLogger.logger")