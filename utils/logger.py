import logging
from pathlib import Path

def setup_logger(config):
    log_path = Path.home() / ".aifileorganizer" / "logs" / "app.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("AIFileOrganizer")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO if config['app'].get('debug', False) else logging.WARNING)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger