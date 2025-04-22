import logging

class WebLogHandler(logging.Handler):
    logs = []

    def emit(self, record):
        msg = self.format(record)
        WebLogHandler.logs.append(msg)
    
    @classmethod
    def get_logs(cls):
        return cls.logs

    @classmethod
    def clear_logs(cls):
        cls.logs.clear()
