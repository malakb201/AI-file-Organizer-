import sys
import os
from pathlib import Path
import tkinter as tk
from gui.main_window import MainWindow
from utils.config import load_config
from utils.logger import setup_logger
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root))

def main():
    # Initialize configuration
    config = load_config()
    
    # Setup logging
    logger = setup_logger(config)
    
    # Create and run the application
    root = tk.Tk()
    app = MainWindow(root, config, logger)
    root.mainloop()

if __name__ == "__main__":
    main()