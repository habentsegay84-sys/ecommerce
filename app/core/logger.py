import logging

# Configure the application's root logger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Shared application logger.
logger = logging.getLogger("ecommerce")