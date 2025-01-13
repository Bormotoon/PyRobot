class RobotSimulatorBackend:
    def __init__(self, width, height, cell_size):
        """
        Initialize the backend for the robot simulator.

        :param width: Width of the grid
        :param height: Height of the grid
        :param cell_size: Size of each cell in the grid
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.robot_x = 0
        self.robot_y = 0
        self.walls = set()  # Set to store walls
        self.permanent_walls = set()  # Set to store permanent walls
        self.markers = {}  # Dictionary to store markers
        self.colored_cells = set()  # Set to store colored cells
        self.edit_mode = False  # Flag to indicate edit mode
        self.dragging_robot = False  # Flag to indicate if the robot is being dragged
        self.is_dragging = False  # New flag to track dragging state

        # Colors for different elements
        self.field_color = '#289628'
        self.grid_color = '#C8C80F'
        self.robot_color = '#FF4500'
        self.edit_field_color = '#6496FF'

        self.setup_permanent_walls()

    def setup_permanent_walls(self):
        """
        Set up the permanent walls around the grid.
        """
        self.permanent_walls.clear()
        for x in range(self.width):
            self.permanent_walls.add(((x, 0), (x + 1, 0)))  # Top boundary
            self.permanent_walls.add(((x, self.height), (x + 1, self.height)))  # Bottom boundary
        for y in range(self.height):
            self.permanent_walls.add(((0, y), (0, y + 1)))  # Left boundary
            self.permanent_walls.add(((self.width, y), (self.width, y + 1)))  # Right boundary

    def handle_canvas_click(self, event):
        """
        Handle click events on the canvas.

        :param event: The event object containing click information
        """
        if not self.edit_mode or self.is_dragging:
            return  # Do nothing if not in edit mode or if dragging robot

        # Calculate offsets to center the grid on the canvas
        offset_x = (event.widget.winfo_width() - self.width * self.cell_size) / 2
        offset_y = (event.widget.winfo_height() - self.height * self.cell_size) / 2

        # Adjust event coordinates based on offsets
        adjusted_x = event.x - offset_x
        adjusted_y = event.y - offset_y

        # Calculate grid coordinates
        grid_x = int(adjusted_x / self.cell_size)
        grid_y = int(adjusted_y / self.cell_size)

        # Define a margin for wall detection
        margin = 5

        # Determine if click is closer to vertical or horizontal line
        x_remainder = adjusted_x % self.cell_size
        y_remainder = adjusted_y % self.cell_size

        wall = None
        if x_remainder < margin or x_remainder > self.cell_size - margin or \
                y_remainder < margin or y_remainder > self.cell_size - margin:
            if x_remainder < margin:
                # Click closer to left vertical line
                wall = ((grid_x, grid_y), (grid_x, grid_y + 1))
            elif x_remainder > self.cell_size - margin:
                # Click closer to right vertical line
                wall = ((grid_x + 1, grid_y), (grid_x + 1, grid_y + 1))
            elif y_remainder < margin:
                # Click closer to top horizontal line
                wall = ((grid_x, grid_y), (grid_x + 1, grid_y))
            elif y_remainder > margin:
                # Click closer to bottom horizontal line
                wall = ((grid_x, grid_y + 1), (grid_x + 1, grid_y + 1))

        # Check if wall is within the field boundaries
        if wall and all(0 <= coord <= self.width for coord in [wall[0][0], wall[1][0]]) and \
                all(0 <= coord <= self.height for coord in [wall[0][1], wall[1][1]]):
            if wall not in self.permanent_walls:  # Check if it's not a permanent wall
                if wall in self.walls:
                    self.walls.remove(wall)
                else:
                    self.walls.add(wall)
        else:
            # Check if click is inside a cell
            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                cell = (grid_x, grid_y)
                if cell in self.colored_cells:
                    self.colored_cells.remove(cell)
                else:
                    self.colored_cells.add(cell)

    def handle_mouse_drag(self, event):
        """
        Handle mouse drag events on the canvas.

        :param event: The event object containing drag information
        """
        if not self.edit_mode:
            return  # Do nothing if not in edit mode

        self.is_dragging = True  # Set the flag when dragging starts

        # Calculate offsets to center the grid on the canvas
        offset_x = (event.widget.winfo_width() - self.width * self.cell_size) / 2
        offset_y = (event.widget.winfo_height() - self.height * self.cell_size) / 2

        # Adjust event coordinates based on offsets
        adjusted_x = event.x - offset_x
        adjusted_y = event.y - offset_y

        # Calculate grid coordinates
        grid_x = int(adjusted_x / self.cell_size)
        grid_y = int(adjusted_y / self.cell_size)

        # Check if the new position is within the field boundaries
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.robot_x = grid_x
            self.robot_y = grid_y

    def stop_dragging(self):
        """
        Stop the dragging action.
        """
        self.is_dragging = False  # Reset the flag when dragging stops
        self.dragging_robot = False  # Reset the flag when dragging stops

    def move_up(self):
        """
        Move the robot up by one cell.
        """
        if self.robot_y > 0 and ((self.robot_x, self.robot_y), (self.robot_x + 1, self.robot_y)) not in self.walls.union(self.permanent_walls):
            self.robot_y -= 1

    def move_down(self):
        """
        Move the robot down by one cell.
        """
        if self.robot_y < self.height - 1 and ((self.robot_x, self.robot_y + 1), (self.robot_x + 1, self.robot_y + 1)) not in self.walls.union(self.permanent_walls):
            self.robot_y += 1

    def move_left(self):
        """
        Move the robot left by one cell.
        """
        if self.robot_x > 0 and ((self.robot_x, self.robot_y), (self.robot_x, self.robot_y + 1)) not in self.walls.union(self.permanent_walls):
            self.robot_x -= 1

    def move_right(self):
        """
        Move the robot right by one cell.
        """
        if self.robot_x < self.width - 1 and ((self.robot_x + 1, self.robot_y), (self.robot_x + 1, self.robot_y + 1)) not in self.walls.union(self.permanent_walls):
            self.robot_x += 1

    def put_marker(self):
        """
        Place a marker at the robot's current position.
        """
        pos = (self.robot_x, self.robot_y)
        if pos not in self.markers:
            self.markers[pos] = 1

    def pick_marker(self):
        """
        Pick up a marker from the robot's current position.
        """
        pos = (self.robot_x, self.robot_y)
        if pos in self.markers:
            del self.markers[pos]

    def paint_cell(self):
        """
        Paint the cell at the robot's current position.
        """
        pos = (self.robot_x, self.robot_y)
        self.colored_cells.add(pos)

    def clear_cell(self):
        """
        Clear the paint from the cell at the robot's current position.
        """
        pos = (self.robot_x, self.robot_y)
        if pos in self.colored_cells:
            self.colored_cells.remove(pos)

    def toggle_edit_mode(self):
        """
        Toggle the edit mode on or off.
        """
        self.edit_mode = not self.edit_mode

    def increase_width(self):
        """
        Increase the width of the grid.
        """
        if self.edit_mode:
            self.width += 1
            self.reset_field()

    def decrease_width(self):
        """
        Decrease the width of the grid.
        """
        if self.edit_mode and self.width > 1:
            self.width -= 1
            self.reset_field()

    def increase_height(self):
        """
        Increase the height of the grid.
        """
        if self.edit_mode:
            self.height += 1
            self.reset_field()

    def decrease_height(self):
        """
        Decrease the height of the grid.
        """
        if self.edit_mode and self.height > 1:
            self.height -= 1
            self.reset_field()

    def reset_field(self):
        """
        Reset the field with new dimensions, including permanent walls and empty cells.
        """
        self.walls.clear()
        self.markers.clear()
        self.colored_cells.clear()
        self.setup_permanent_walls()