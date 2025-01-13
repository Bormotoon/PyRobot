import tkinter as tk
from gui import RobotSimulatorGUI

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Initialize the RobotSimulatorGUI with the main window
    app = RobotSimulatorGUI(root)

    # Start the Tkinter event loop
    root.mainloop()