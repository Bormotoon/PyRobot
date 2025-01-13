def center_window(gui):
    """
    Center the GUI window on the screen.

    :param gui: The GUI object containing the root window
    """
    gui.root.update_idletasks()  # Update "idle" tasks to get correct window dimensions
    width = gui.root.winfo_width()  # Get the current width of the window
    height = gui.root.winfo_height()  # Get the current height of the window
    # Calculate the x and y coordinates to center the window
    x = (gui.root.winfo_screenwidth() // 2) - (width // 2)
    y = (gui.root.winfo_screenheight() // 2) - (height // 2)
    # Set the geometry of the window to center it
    gui.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def setup_permanent_walls(gui):
    """
    Set up the permanent walls around the grid in the GUI.

    :param gui: The GUI object containing the grid dimensions and wall sets
    """
    for x in range(gui.width):
        # Add top boundary walls
        gui.permanent_walls.add(((x, 0), (x + 1, 0)))
        # Add bottom boundary walls
        gui.permanent_walls.add(((x, gui.height), (x + 1, gui.height)))
    for y in range(gui.height):
        # Add left boundary walls
        gui.permanent_walls.add(((0, y), (0, y + 1)))
        # Add right boundary walls
        gui.permanent_walls.add(((gui.width, y), (gui.width, y + 1)))