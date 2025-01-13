def center_window(gui):
    """
    Center the GUI window on the screen and set its size to half of the screen size.

    :param gui: The GUI object containing the root window
    """
    gui.root.update_idletasks()  # Update "idle" tasks to get correct window dimensions
    screen_width = gui.root.winfo_screenwidth()  # Get the screen width
    screen_height = gui.root.winfo_screenheight()  # Get the screen height
    # Calculate the width and height to be half of the screen size
    width = screen_width // 2
    height = screen_height // 2
    # Calculate the x and y coordinates to center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    # Set the geometry of the window to center it and set its size
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