import tkinter as tk
from tkinter import ttk
from utils import center_window
from backend import RobotSimulatorBackend

class RobotSimulatorGUI:
    def __init__(self, root, width=7, height=7, cell_size=50):
        """
        Initialize the GUI for the robot simulator.

        :param root: The root window of the Tkinter application
        :param width: Width of the grid
        :param height: Height of the grid
        :param cell_size: Size of each cell in the grid
        """
        self.root = root
        self.root.title("Robot Simulator")

        # Initialize the backend logic
        self.backend = RobotSimulatorBackend(width, height, cell_size)

        # Configure the root window's grid layout
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar()
        self.status_var.set("Click between cells to add/remove walls")

        # Variables to store current grid dimensions
        self.width_var = tk.StringVar(value=f"Width: {self.backend.width}")
        self.height_var = tk.StringVar(value=f"Height: {self.backend.height}")

        self.setup_gui()

        # Bind mouse events to canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)  # Bind mouse release event
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Bind mouse wheel event

        # Bind the resize event to adjust the canvas size
        self.root.bind("<Configure>", self.on_resize)

        # Center the window on the screen
        center_window(self)

        # Schedule draw_field() to be called after the window is fully created
        self.root.after(100, self.draw_field)

    def on_mouse_wheel(self, event):
        """
        Handle mouse wheel events to change the zoom level of the grid.

        :param event: The event object containing mouse wheel information
        """
        if event.delta > 0:
            self.backend.cell_size += 5  # Increase cell size to zoom in
        else:
            self.backend.cell_size = max(5, self.backend.cell_size - 5)  # Decrease cell size to zoom out, with a minimum size

        self.draw_field()

    def setup_gui(self):
        """
        Set up the GUI components.
        """
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=0, column=0, pady=5, sticky=(tk.N, tk.S))

        # Add control buttons for robot movement
        ttk.Button(control_frame, text="↑", command=self.move_up).grid(row=0, column=1)
        ttk.Button(control_frame, text="↓", command=self.move_down).grid(row=2, column=1)
        ttk.Button(control_frame, text="←", command=self.move_left).grid(row=1, column=0)
        ttk.Button(control_frame, text="→", command=self.move_right).grid(row=1, column=2)

        marker_frame = ttk.Frame(control_frame)
        marker_frame.grid(row=3, column=0, columnspan=3, pady=5)
        ttk.Button(marker_frame, text="Put Marker", command=self.put_marker).grid(row=0, column=0, padx=5)
        ttk.Button(marker_frame, text="Pick Marker", command=self.pick_marker).grid(row=0, column=1, padx=5)
        ttk.Button(marker_frame, text="Paint Cell", command=self.paint_cell).grid(row=1, column=0, padx=5)
        ttk.Button(marker_frame, text="Clear Cell", command=self.clear_cell).grid(row=1, column=1, padx=5)

        # Add a button to toggle edit mode
        ttk.Button(marker_frame, text="Toggle Edit Mode", command=self.toggle_edit_mode).grid(row=2, column=0,
                                                                                              columnspan=2, pady=5)

        # Add buttons to increase/decrease grid size
        size_frame = ttk.Frame(control_frame)
        size_frame.grid(row=4, column=0, columnspan=3, pady=5)
        ttk.Button(size_frame, text="Increase Width", command=self.increase_width).grid(row=0, column=0, padx=5)
        ttk.Button(size_frame, text="Decrease Width", command=self.decrease_width).grid(row=0, column=1, padx=5)
        ttk.Label(size_frame, textvariable=self.width_var).grid(row=0, column=2, padx=5)  # Display current width
        ttk.Button(size_frame, text="Increase Height", command=self.increase_height).grid(row=1, column=0, padx=5)
        ttk.Button(size_frame, text="Decrease Height", command=self.decrease_height).grid(row=1, column=1, padx=5)
        ttk.Label(size_frame, textvariable=self.height_var).grid(row=1, column=2, padx=5)  # Display current height

        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        # Calculate canvas size based on grid dimensions
        canvas_width = (self.backend.width + 1) * self.backend.cell_size
        canvas_height = (self.backend.height + 1) * self.backend.cell_size
        self.canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height,
                                background=self.backend.field_color)
        self.canvas.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.N, tk.S, tk.E, tk.W))

        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=1, column=1)

    def on_resize(self, event):
        """
        Handle window resize events to adjust the canvas size.

        :param event: The event object containing resize information
        """
        # Calculate new canvas size to occupy the right half of the window
        new_width = self.root.winfo_width() // 2
        new_height = self.root.winfo_height()
        self.canvas.config(width=new_width, height=new_height)
        self.draw_field()

    def toggle_edit_mode(self):
        """
        Toggle the edit mode on or off.
        """
        self.backend.toggle_edit_mode()
        # Change canvas background color based on edit mode
        self.canvas.config(background=self.backend.edit_field_color if self.backend.edit_mode else self.backend.field_color)
        self.status_var.set("Edit mode enabled" if self.backend.edit_mode else "Edit mode disabled")
        self.draw_field()

    def on_canvas_click(self, event):
        """
        Handle click events on the canvas.

        :param event: The event object containing click information
        """
        self.backend.handle_canvas_click(event)
        self.draw_field()

    def on_mouse_drag(self, event):
        """
        Handle mouse drag events on the canvas.

        :param event: The event object containing drag information
        """
        if not self.backend.edit_mode:
            return

        self.backend.handle_mouse_drag(event)
        self.draw_field()

    def on_mouse_release(self, event):
        """
        Handle mouse release events on the canvas.

        :param event: The event object containing release information
        """
        self.backend.stop_dragging()  # Reset the drag flag when the mouse button is released
        self.draw_field()

    def draw_field(self):
        """
        Draw the grid, walls, markers, and robot on the canvas.
        """
        self.canvas.delete("all")

        # Calculate offsets to center the grid
        offset_x = (self.canvas.winfo_width() - self.backend.width * self.backend.cell_size) / 2
        offset_y = (self.canvas.winfo_height() - self.backend.height * self.backend.cell_size) / 2

        # Draw colored cells
        for (x, y) in self.backend.colored_cells:
            cell_x = x * self.backend.cell_size + offset_x
            cell_y = y * self.backend.cell_size + offset_y
            self.canvas.create_rectangle(
                cell_x, cell_y, cell_x + self.backend.cell_size, cell_y + self.backend.cell_size,
                fill='gray'
            )

        # Draw all walls (permanent and user-added) with the same style
        all_walls = self.backend.permanent_walls.union(self.backend.walls)
        for wall in all_walls:
            (x1, y1), (x2, y2) = wall
            self.canvas.create_line(
                x1 * self.backend.cell_size + offset_x, y1 * self.backend.cell_size + offset_y,
                x2 * self.backend.cell_size + offset_x, y2 * self.backend.cell_size + offset_y,
                width=8, fill=self.backend.grid_color  # Same style for all walls
            )

        # Draw grid lines on top of everything
        for i in range(self.backend.width + 1):
            x = i * self.backend.cell_size + offset_x
            self.canvas.create_line(x, offset_y, x, self.backend.height * self.backend.cell_size + offset_y,
                                    fill=self.backend.grid_color, width=2)

        for i in range(self.backend.height + 1):
            y = i * self.backend.cell_size + offset_y
            self.canvas.create_line(offset_x, y, self.backend.width * self.backend.cell_size + offset_x, y,
                                    fill=self.backend.grid_color, width=2)

        # Draw markers
        for (x, y) in self.backend.markers.keys():
            marker_x = (x + 0.5) * self.backend.cell_size + offset_x
            marker_y = (y + 0.5) * self.backend.cell_size + offset_y
            marker_size = self.backend.cell_size * 0.3  # Increased size by half
            self.canvas.create_oval(
                marker_x - marker_size, marker_y - marker_size,
                marker_x + marker_size, marker_y + marker_size,
                fill='gray', outline='black'
            )

        # Draw robot as diamond on top of markers
        robot_center_x = (self.backend.robot_x + 0.5) * self.backend.cell_size + offset_x
        robot_center_y = (self.backend.robot_y + 0.5) * self.backend.cell_size + offset_y
        diamond_size = self.backend.cell_size * 0.4

        diamond_points = [
            robot_center_x, robot_center_y - diamond_size / 2,
                            robot_center_x + diamond_size / 2, robot_center_y,
            robot_center_x, robot_center_y + diamond_size / 2,
                            robot_center_x - diamond_size / 2, robot_center_y
        ]
        self.canvas.create_polygon(diamond_points, fill=self.backend.robot_color, outline='black')

        self.canvas.update()

    def paint_cell(self):
        """
        Paint the cell at the robot's current position.
        """
        self.backend.paint_cell()
        self.draw_field()

    def clear_cell(self):
        """
        Clear the paint from the cell at the robot's current position.
        """
        self.backend.clear_cell()
        self.draw_field()

    def move_up(self):
        """
        Move the robot up by one cell.
        """
        self.backend.move_up()
        self.draw_field()

    def move_down(self):
        """
        Move the robot down by one cell.
        """
        self.backend.move_down()
        self.draw_field()

    def move_left(self):
        """
        Move the robot left by one cell.
        """
        self.backend.move_left()
        self.draw_field()

    def move_right(self):
        """
        Move the robot right by one cell.
        """
        self.backend.move_right()
        self.draw_field()

    def put_marker(self):
        """
        Place a marker at the robot's current position.
        """
        self.backend.put_marker()
        self.draw_field()

    def pick_marker(self):
        """
        Pick up a marker from the robot's current position.
        """
        self.backend.pick_marker()
        self.draw_field()

    def on_mouse_move(self, event):
        """
        Handle mouse move events on the canvas.

        :param event: The event object containing mouse move information
        """
        cell_width = self.canvas.winfo_width() / (self.backend.width + 1)
        cell_height = self.canvas.winfo_height() / (self.backend.height + 1)

        x = event.x / cell_width
        y = event.y / cell_height

        # Update status message based on mouse position
        if abs(x - round(x)) < 0.2 and abs(y - round(y)) < 0.2:
            self.status_var.set("Click to add/remove wall")
        else:
            self.status_var.set("Move mouse between cells to add/remove walls")

    def increase_width(self):
        """
        Increase the width of the grid.
        """
        self.backend.increase_width()
        self.width_var.set(f"Width: {self.backend.width}")  # Update width display
        self.draw_field()

    def decrease_width(self):
        """
        Decrease the width of the grid.
        """
        self.backend.decrease_width()
        self.width_var.set(f"Width: {self.backend.width}")  # Update width display
        self.draw_field()

    def increase_height(self):
        """
        Increase the height of the grid.
        """
        self.backend.increase_height()
        self.height_var.set(f"Height: {self.backend.height}")  # Update height display
        self.draw_field()

    def decrease_height(self):
        """
        Decrease the height of the grid.
        """
        self.backend.decrease_height()
        self.height_var.set(f"Height: {self.backend.height}")  # Update height display
        self.draw_field()