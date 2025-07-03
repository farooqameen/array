import logging
from asgi_correlation_id.context import correlation_id

class CorrelationIdHandler(logging.StreamHandler):
    """
    Custom logging handler that appends a correlation ID to log records.

    This handler ensures that each log message includes a `correlation_id`, 
    which is useful for tracking and correlating logs across different parts 
    of the application or distributed systems. If no correlation ID is found 
    in the current context, it defaults to "N/A".

    Methods:
        emit(record): Overrides the base class method to add the `correlation_id` 
                      to the log record before emitting it.

    Example:
        logger.info("This is a log message.")
        Output: "12:34:56.789 [MainThread] INFO  my_logger [12345abc] - This is a log message"
    """
    def emit(self, record):
        """
        Overrides the base `emit` method to add a `correlation_id` to the log record.

        Ensures that each log record includes a `correlation_id`. If the `correlation_id` 
        is not present in the current context, it assigns a default value of "N/A".

        Args:
            record (logging.LogRecord): The log record to be emitted.

        Returns:
            None

        Example:
            A log message with the correlation ID included in the output:

            Input:
                logger.info("Processing request.")

            Output:
                "12:34:56.789 [MainThread] INFO  job-plus-service-ai [12345abc] - Processing request."
            
            If no correlation ID is set:
                "12:34:56.789 [MainThread] INFO  job-plus-service-ai [N/A] - Processing request."
        """
        if 'correlation_id' not in record.__dict__:
            record.correlation_id = correlation_id.get() or "N/A"
        super().emit(record)

logging.basicConfig(
    level="INFO",
    format="%(asctime)s.%(msecs)03d [%(threadName)s.%(filename)s.%(funcName)s] %(levelname)-5s %(name)s [%(correlation_id)s] - %(message)s",
    datefmt="%H:%M:%S",
    handlers=[CorrelationIdHandler()]
)

logger = logging.getLogger("cbb-chatbot-v2")