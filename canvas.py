import math
from tkinter import messagebox, simpledialog
from tkinter.colorchooser import askcolor
from bigvars import FONT_OPTIONS
from typing import Optional, Union, List, Tuple, Dict, Any
from PIL import ImageTk
import tkinter as tk
import tkinter.ttk as ttk
import _tkinter
import file_manager
import os

SHAPES: List[str] = ["Pencil", "Rectangle", "Oval", "Triangle", "Text"]


class CanvasApp:
    """
    Class that represents a canvas drawing app.

    Attributes:
        master (tk.Tk): The master window of the canvas.
        canvas (tk.Canvas): The canvas to be drawn over.
        actions (List[Dict[str, Any]]): A list containing all the done actions.
        file_path (str): The path the canvas has been saved to.
    """

    def __init__(self, master: tk.Tk, is_load: bool = False) -> None:
        """
        Initialize the canvas.
        :param master: The master window of the canvas.
        :param is_load: Whether to load an existing canvas or not.
                        Default value is False.
        """
        self.master: tk.Tk = master
        self.master.title("Canvas")

        self.file_path: List[str] = ['']  # The path the canvas has been saved to

        if os.name == 'posix':  # If linux
            self.master.attributes("-zoomed", True)
            self.__undo_image = ImageTk.PhotoImage(file="Images/Undo.png")
            self.__redo_image = ImageTk.PhotoImage(file="Images/Redo.png")
        else:
            self.__undo_image = ImageTk.PhotoImage(file="Images\\Undo.png")
            self.__redo_image = ImageTk.PhotoImage(file="Images\\Redo.png")
            self.master.state("zoomed")

        self.master.bind("<Escape>", lambda fs=False:
                         self.master.attributes("-fullscreen", False))
        self.master.bind("<Control-z>", lambda event: self.__undo())
        self.master.bind("<Control-y>", lambda event: self.__redo())
        self.master.bind("<Control-s>", lambda event: self.__save_canvas())
        self.master.bind("<Control-w>", lambda event: self.__on_exit())

        # Add a protocol that when the user clicks the red 'X' to exit the
        # program, it will ask him exit questions.
        self.master.protocol("WM_DELETE_WINDOW", self.__on_exit)

        self.canvas: tk.Canvas = tk.Canvas(self.master, bg="white")

        # Initialize an empty list containing all the done actions
        self.actions: List[Dict[str, Any]] = []
        # Initialize an empty list containing all undone actions
        self.__undone_actions: List[Dict[str, Any]] = []

        if is_load:  # If the user wants to load a canvas
            file_manager.load_canvas(self.canvas, self.actions,
                                     self.__on_text_right_click,
                                     self.file_path)

        # Make the canvas visible
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize values regarding the 'Moving Objects Mode'
        self.__selected_object: Union[str, int] = 0
        self.__selected_object_start_x: int = 0
        self.__selected_object_start_y: int = 0

        # Initialize default values regarding the drawing
        self.__outline_color: str = "white" if self.canvas.cget('bg') == "black"\
            else "black"
        self.__line_width: int = 2
        self.__eraser_width: int = 10
        self.__fill: str = ''
        self.__current_drawable: str = "Pencil"
        self.__current_object: Optional[int] = None

        self.__mode: str = 'Drawing Mode'

        # Initialize lists that will hold all the polygon dots and points
        self.__polygon_points: List[Tuple[int, int]] = []
        self.__polygon_dots: List[int] = []

        # Initialize an empty list
        # that will hold the buttons you can configure.
        self.__config_buttons: List[ttk.Button] = []

        # Create a frame to hold the object buttons and the menubar
        self.__frame = ttk.Frame(self.master, relief=tk.RAISED, borderwidth=2)

        self.__create_menus()  # Top menus (File, Tools, View, etc)
        self.__init_frame_buttons()  # Pencil, Oval, Text, etc

        # Initialize the 'Create the polygon' button
        self.__polygon_button = ttk.Button(self.__frame,
                                           text="Create the polygon",
                                           command=lambda:
                                           self.__create_polygon_from_dots())

        # Place the frame on the window
        self.__frame.place(relx=0, rely=0)

        # Initialize context menus different objects
        self.__init_text_context_menu()
        self.__init_context_menu()

        # Bind mouse events to methods that handle them
        self.canvas.bind("<ButtonPress-1>", self.__on_click)
        self.canvas.bind("<B1-Motion>", self.__on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.__on_release())
        self.canvas.bind("<Double-Button-3>", lambda event:
                         self.__set_selecting_mode())

    def __buttons_config(self, *buttons: ttk.Button) -> None:
        """
        This function configures the configurable buttons.
        :param *buttons: The buttons to configure.
        """
        for button in buttons:
            button.config(
                state=tk.DISABLED if not self.canvas.find_all()
                else tk.NORMAL
            )
        # These are not part of self.__config_buttons
        # because they are configured differently than the rest of the buttons
        self.__undo_button.config(state=tk.DISABLED if not self.actions
                                  else tk.NORMAL)
        self.__redo_button.config(state=tk.DISABLED if not
                                  self.__undone_actions else tk.NORMAL)

    def __init_frame_buttons(self) -> None:
        """
        This function initializes all the buttons that are on the frame.
        """
        self.__undo_button = ttk.Button(self.__frame,
                                        image=self.__undo_image,
                                        command=self.__undo,
                                        state=tk.DISABLED if not
                                        self.actions else tk.NORMAL)
        self.__undo_button.pack(side=tk.LEFT)
        self.__redo_button = ttk.Button(self.__frame,
                                        image=self.__redo_image,
                                        command=self.__redo,
                                        state=tk.DISABLED if not
                                        self.__undone_actions else tk.NORMAL)
        self.__redo_button.pack(side=tk.LEFT)

        for shape in SHAPES:  # Buttons for Pencil, Oval, etc
            shape_button: ttk.Button = ttk.Button(self.__frame, text=shape,
                                                  command=lambda s=shape:
                                                  self.__choose_drawable(s))
            shape_button.pack(side=tk.LEFT)

        polygon_button: ttk.Button = ttk.Button(self.__frame,
                                                text="Polygon",
                                                command=self.__set_polygon_mode)
        eraser_button: ttk.Button = ttk.Button(self.__frame, text="Toggle Eraser",
                                               command=lambda t="Eraser":
                                               self.__choose_drawable(t),
                                               state=tk.DISABLED if not
                                               self.canvas.find_all()
                                               else tk.NORMAL)
        move_button: ttk.Button = ttk.Button(self.__frame, text="Move Drawn Objects",
                                             command=self.__set_selecting_mode,
                                             state=tk.DISABLED if not
                                             self.canvas.find_all()
                                             else tk.NORMAL)

        self.__config_buttons = [move_button, eraser_button]
        self.__buttons_config(*self.__config_buttons)

        polygon_button.pack(side=tk.LEFT)
        eraser_button.pack(side=tk.LEFT)
        move_button.pack(side=tk.LEFT)

    def __init_text_context_menu(self) -> None:
        """
        This function initializes a context menu for text objects
        """
        self.__text_context_menu: tk.Menu = tk.Menu(self.master, tearoff=0)
        self.__text_context_menu.add_command(label="Change Text",
                                             command=self.__change_text)
        self.__text_context_menu.add_command(label="Change Text Color",
                                             command=self.__fill_object)
        self.__text_context_menu.add_command(label="Change Text Size",
                                             command=self.__change_text_size)
        self.__text_context_menu.add_command(label="Change Font",
                                             command=self.__change_font)
        change_order_menu = tk.Menu(self.__text_context_menu, tearoff=0)
        change_order_menu.add_command(label="Bring To The Front",
                                      command=lambda: self.__change_order(True)
                                      )
        change_order_menu.add_command(label="Send To The Back",
                                      command=lambda: self.__change_order(
                                          False)
                                      )
        self.__text_context_menu.add_cascade(label="Change Order",
                                             menu=change_order_menu)
        self.__text_context_menu.add_command(label="Delete Text",
                                             command=self.__delete_object)

    def __init_context_menu(self, is_polygon: bool = False) -> None:
        """
        This function initializes the context menu for non-text objects.
        :param is_polygon: Whether the object is a polygon or not
                           Defaults to False.
        """
        # Create a context menu
        self.__context_menu: tk.Menu = tk.Menu(self.master, tearoff=0)
        fill_menu = tk.Menu(self.__context_menu, tearoff=0)
        fill_menu.add_command(label="Fill Object",
                              command=self.__fill_object)
        fill_menu.add_command(label="Clear Object's fill",
                              command=lambda:
                              self.__fill_object(True))
        self.__context_menu.add_cascade(label="Fill Options", menu=fill_menu)
        change_order_menu = tk.Menu(self.__context_menu, tearoff=0)
        change_order_menu.add_command(label="Bring To The Front",
                                      command=lambda: self.__change_order(True)
                                      )
        change_order_menu.add_command(label="Send To The Back",
                                      command=lambda: self.__change_order(
                                          False)
                                      )
        self.__context_menu.add_cascade(label="Change order",
                                        menu=change_order_menu)
        self.__context_menu.add_command(label="Change Outline Color",
                                        command=self.__change_color)
        self.__context_menu.add_command(label="Change Outline Width",
                                        command=self.__change_object_width)
        if is_polygon:
            self.__context_menu.add_command(label="Rotate object",
                                            command=self.__rotate)
        self.__context_menu.add_command(label="Delete Object",
                                        command=self.__delete_object)

        # Bind the context menu to canvas objects
        self.canvas.bind("<Button-3>", self.__select_object_right_click)

    def __rotate(self) -> None:
        """
        This function gets the degrees the user wants to rotate the object by.
        """
        if self.__selected_object:
            obj_type = self.canvas.type(self.__selected_object)
            if obj_type != 'polygon':
                messagebox.showinfo("ERROR",
                                    "You can only rotate polygons")
                return
            angle = simpledialog.askinteger("Rotate Object",
                                            "Enter the degrees to rotate the object by:",
                                            parent=self.master)
            if angle:
                self.__rotate_object(angle)

    def __rotate_object(self, angle) -> None:
        """
        This function rotates the selected object.
        """
        if self.__selected_object:
            # Get the current coordinates of the object
            coords = self.canvas.coords(self.__selected_object)

            # Calculate the center point of the object
            center_x = sum(coords[::2]) / (len(coords) // 2)
            center_y = sum(coords[1::2]) / (len(coords) // 2)

            # Convert the rotation angle to radians
            angle_rad = math.radians(angle)

            # Calculate the new coordinates for each point in the object
            new_coords = []
            for x, y in zip(coords[::2], coords[1::2]):
                new_x = center_x + (x - center_x) * math.cos(angle_rad) - (
                            y - center_y) * math.sin(angle_rad)
                new_y = center_y + (x - center_x) * math.sin(angle_rad) + (
                            y - center_y) * math.cos(angle_rad)
                new_coords.extend([new_x, new_y])

            info = file_manager.get_item_info(self.canvas, self.__selected_object)

            action: Dict[str, Any] = {
                'type': 'rotate object',
                'old_object': self.__selected_object,
                'old_info': info
            }

            # Delete the original object from the canvas
            self.canvas.delete(self.__selected_object)

            # Draw a new object with the calculated coordinates
            # Assuming the object is a polygon; if not, you'll need to adjust this
            self.__selected_object = self.canvas.create_polygon(
                new_coords,
                fill=info['fill'],
                outline=info['outline'],
                width=info['width']
            )

            action['new_object'] = self.__selected_object
            action['new_info'] = file_manager.get_item_info(self.canvas,
                                                            self.__selected_object)
            self.actions.append(action)

    def __on_text_right_click(self, event: tk.Event) -> None:
        """
        This function shows the context menu for text objects when they are
        clicked on using the right mouse button ("<ButtonPress-3>").
        :param event: The "<ButtonPress-3>" event to handle.
        """
        # Display the context menu for text objects at the mouse position
        self.__text_context_menu.post(event.x_root, event.y_root)

    def __change_font(self) -> None:
        """
        This function changes a text object's font.
        """
        self.__disable_canvas_touch()
        new_window: tk.Toplevel = tk.Toplevel(self.master)
        new_window.title("Select Font")
        # Make it not resizeable
        new_window.resizable(False, False)

        label: ttk.Label = ttk.Label(new_window, text="Choose Font",
                                     font=("David", 14))
        label.pack(side=tk.TOP)

        # Create a frame for the font list and scrollbar
        font_frame: ttk.Frame = ttk.Frame(new_window)
        font_frame.pack(padx=10, pady=10)
        font_listbox: tk.Listbox = tk.Listbox(font_frame)
        font_listbox.pack(side=tk.LEFT)
        scrollbar: ttk.Scrollbar = ttk.Scrollbar(font_frame, orient=tk.VERTICAL,
                                                 command=font_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        font_listbox.config(yscrollcommand=scrollbar.set)

        # Add all the fonts to the listbox
        font_listbox.insert(tk.END, *FONT_OPTIONS)

        def select_font() -> None:
            """
            This function selects the font and
            updates the selected text object's font.
            """
            selected_index: Tuple[int, ...] = font_listbox.curselection()
            if selected_index:
                selected_font: str = FONT_OPTIONS[selected_index[0]]
                new_window.destroy()
                # Get the current text of the selected text object
                current_text: str = self.canvas.itemcget(
                    self.__selected_object,
                    "text")
                # Get the current size of the selected text object
                current_state = self.canvas.itemcget(self.__selected_object,
                                                     "font").split()
                current_size = current_state[1]
                # Update the font of the selected text object
                self.canvas.itemconfig(self.__selected_object,
                                       font=(selected_font, current_size),
                                       text=current_text)
                action: Dict[str, Any] = {
                    'type': 'change object font',
                    'object': self.__selected_object,
                    'prev_font': current_state,
                    'new_font': self.canvas.itemcget(self.__selected_object,
                                                     "font").split()
                }
                self.actions.append(action)
            self.__enable_canvas_touch()

        # Add a button so the user will be able to select the font
        select_button: ttk.Button = ttk.Button(new_window, text="Select",
                                               command=select_font)
        select_button.pack(pady=10)

        # Bind the "Enter" key to the select_font function
        new_window.bind('<Return>', lambda event: select_font())

    def __change_text(self) -> None:
        """
        This function changes the text of a text object.
        """
        # Create a new window so the user input
        # won't be deleted before its visibility changed
        self.__disable_canvas_touch()
        new_window: tk.Tk = tk.Tk()
        new_window.withdraw()

        prev_text = self.canvas.itemcget(self.__selected_object, 'text')

        new_text: Optional[str] = simpledialog.askstring(title="Change Text",
                                                         prompt="Enter the new text:",
                                                         initialvalue=prev_text,
                                                         parent=new_window)
        new_window.destroy()
        if new_text is not None:

            # Change the text of the selected text object
            self.canvas.itemconfig(self.__selected_object, text=new_text)

            action = {
                'type': 'change text',
                'object': self.__selected_object,
                'prev_text': prev_text,
                'new_text': new_text
            }
            self.actions.append(action)
        self.__enable_canvas_touch()

    def __change_text_size(self) -> None:
        """
        This function changes the size of the text object.
        """
        self.__disable_canvas_touch()
        # Create a new window so the user input
        # won't be deleted before its visibility changed
        new_window: tk.Tk = tk.Tk()
        new_window.withdraw()

        # Get the current font of the selected text object
        current_state: str = self.canvas.itemcget(self.__selected_object,
                                                  "font").split()
        current_font = current_state[0]

        # Prompt the user to enter a new size for text
        new_size: Optional[int] = simpledialog.askinteger(
            title="Change Text Size",
            prompt="Enter the new"
                   " text size:",
            parent=new_window,
            initialvalue=int(current_state[1]),
            minvalue=1,
            maxvalue=100)
        new_window.destroy()
        if new_size is not None:
            # Change the size of the selected text object
            # while keeping the font family
            self.canvas.itemconfig(self.__selected_object,
                                   font=(current_font, new_size))
            action: Dict[str, Any] = {
                'type': 'change text size',
                'object': self.__selected_object,
                'prev_font': current_state,
                'new_font': self.canvas.itemcget(self.__selected_object,
                                                 "font").split()
            }
            self.actions.append(action)
        self.__enable_canvas_touch()

    def __select_object_right_click(self, event: tk.Event) -> None:
        """
        This function shows the context menu for non-text objects when they are
        clicked on using the right mouse button (<ButtonPress-3>).
        """
        if len(self.canvas.find_all()) != 0:  # If the board is not empty
            # Find the object closest to the mouse cursor
            self.__selected_object = \
                self.canvas.find_closest(event.x, event.y)[0]
            if self.canvas.type(self.__selected_object) == 'text':
                self.__text_context_menu.post(event.x_root, event.y_root)
            else:
                self.__init_context_menu(
                    self.canvas.type(self.__selected_object) == 'polygon')
                # Display the context menu at the mouse position
                self.__context_menu.post(event.x_root, event.y_root)

    def __change_order(self, order_action: bool) -> None:
        """
        This function changes the order of the selected object, that is,
        brings it to the front or the back of the canvas.
        :param order_action (bool): True if the action is to bring to the front,
                                    False otherwise.
        """
        action: Dict[str, Any] = {
            'type': 'changing order',
            'prev_state': not order_action,
            'new_state': order_action,
            'object': self.__selected_object
        }
        self.actions.append(action)
        if order_action:
            # Bring the selected object to the front
            self.canvas.tag_raise(self.__selected_object)
        elif not order_action:
            # Send the selected object to the back
            self.canvas.tag_lower(self.__selected_object)

    def __change_color(self) -> None:
        """
        This function changes the outline color of the selected object.
        """
        if self.__selected_object:
            try:
                # Check the type of the selected object
                object_type: str = self.canvas.type(self.__selected_object)
                if object_type == "line":
                    # If the selected object is a line, call __fill_object,
                    # because otherwise, it will throw an error.
                    self.__fill_object()
                    return
                self.__disable_canvas_touch()
                # Prompt the user to select a new color
                color: Optional[str] = askcolor()[1]
                if color:
                    prev_state = self.canvas.itemcget(self.__selected_object,
                                                      'outline')

                    # Update the color of the selected object (line)
                    self.canvas.itemconfig(self.__selected_object, outline=color)

                    action: Dict[str, Any] = {
                        'type': 'change outline color',
                        'object': self.__selected_object,
                        'prev_state': prev_state,
                        'new_state': color
                    }
                    self.actions.append(action)
                self.__enable_canvas_touch()
            except _tkinter.TclError:
                messagebox.showerror("ERROR",
                                     "The object you have selected "
                                     "does not have a color option.\nThe "
                                     "computer must thought you meant an object"
                                     " you did not, please try again")

    def __delete_object(self) -> None:
        """
        This function deletes the selected object.
        """
        if self.__selected_object:
            action: Dict[str, Any] = {
                'type': 'delete object',
                'object': self.__selected_object,
                'info': file_manager.get_item_info(self.canvas, self.__selected_object)
            }
            self.actions.append(action)
            self.canvas.delete(self.__selected_object)
            self.__buttons_config(*self.__config_buttons)

    def __fill_object(self, is_clear: bool = False) -> None:
        """
        This function fills the selected object.
        :param is_clear (bool): Whether to clear the fill or not.
        """
        if self.__selected_object:
            try:
                prev_state = self.canvas.itemcget(self.__selected_object,
                                                  'fill')
                action: Dict[str, Any] = {
                    'type': 'change fill',
                    'object': self.__selected_object,
                    'prev_state': prev_state
                }
                if is_clear:
                    if prev_state == '':
                        # If the object's fill is already cleared, do nothing
                        return
                    action['new_state'] = ''
                else:
                    self.__disable_canvas_touch()
                    # Prompt the user to select a new color
                    color: Optional[str] = askcolor()[1]
                    if color:
                        action['new_state'] = color

                        # Update the color of the selected object
                        self.canvas.itemconfig(self.__selected_object,
                                               fill=color)
                    self.__enable_canvas_touch()
                self.actions.append(action)
            except _tkinter.TclError:
                messagebox.showerror("ERROR",
                                     "The object you have selected "
                                     "does not have a fill option.\nThe "
                                     "computer must thought you meant an object"
                                     " you did not, please try again")

    def __change_object_width(self) -> None:
        """
        This function changes the width of the outline of the selected object.
        """
        try:
            if self.__selected_object:
                self.__disable_canvas_touch()
                scale_window = tk.Toplevel(self.master)
                scale_window.resizable(False, False)
                scale_window.title("Change "
                                   f"{self.canvas.type(self.__selected_object)}"
                                   " Width")
                scale: ttk.Scale = ttk.Scale(scale_window, from_=1, to=100,
                                             orient=tk.HORIZONTAL)
                scale.pack()

                scale_window.bind("<Right>",
                                  lambda event: scale.set(scale.get() + 1))
                scale_window.bind("<Left>",
                                  lambda event: scale.set(scale.get() - 1))

                # Create a Canvas widget to display the width
                width_canvas: tk.Canvas = tk.Canvas(scale_window, width=200,
                                                    height=75)
                width_canvas.pack()

                # Draw a line on the Canvas widget with initial width
                line = width_canvas.create_line(50, 25, 150, 25,
                                                width=scale.get())

                def set_width() -> None:
                    """
                    This function sets the width based on the Scale widget value.
                    """
                    self.canvas.itemconfig(self.__selected_object,
                                           width=scale.get())
                    scale_window.destroy()
                    self.__enable_canvas_touch()

                def update_line(value) -> None:
                    """
                    This function updates the line's width on the Canvas widget.
                    """
                    width = value
                    width_canvas.itemconfigure(line, width=width)

                # Bind the Scale widget's command to the update_line function
                scale.config(command=update_line)

                # Add a button to set the width
                set_button: ttk.Button = ttk.Button(scale_window,
                                                    text="Set Width",
                                                    command=set_width)
                set_button.pack()

                # Bind the Enter key to the set_width function
                scale_window.bind('<Return>', lambda event: set_width())
        except _tkinter.TclError:
            messagebox.showerror("ERROR",
                                 "The object you have selected "
                                 "does not have a width option.\nThe "
                                 "computer must thought you meant an object"
                                 " you did not, please try again")

    def __create_menus(self) -> None:
        """
        This function creates the menu bar for the canvas.
        """
        menubar: tk.Menu = tk.Menu(self.__frame)

        # Configure the submenu 'File' inside the main menu
        file_menu: tk.Menu = tk.Menu(menubar, tearoff=0)

        # Configure the submenu 'Export As:' inside the 'File' menu
        export_as_menu = tk.Menu(file_menu, tearoff=0)
        export_as_menu.add_command(label="A .JPG File",
                                   command=lambda save_as="jpeg":
                                   self.__save_as_type(save_as))
        export_as_menu.add_command(label="A .PNG File",
                                   command=lambda save_as="png":
                                   self.__save_as_type(save_as))
        export_as_menu.add_command(label="A .PDF File",
                                   command=lambda save_as="pdf":
                                   self.__save_as_type(save_as))
        export_as_menu.add_command(label="A .EPS File",
                                   command=lambda save_as="eps":
                                   self.__save_as_type(save_as))
        export_as_menu.add_command(label="A .SVG File",
                                   command=lambda canvas=self.canvas:
                                   file_manager.save_as_svg(canvas))
        export_as_menu.add_command(label="A .GIF File",
                                   command=lambda save_as="gif":
                                   self.__save_as_type(save_as))

        file_menu.add_command(label="Save The Canvas",
                              command=self.__save_canvas)
        file_menu.add_command(label="Import A Canvas",
                              command=lambda:
                              file_manager.load_canvas(self.canvas,
                                                       self.actions,
                                                       self.__on_text_right_click,
                                                       self.file_path))

        file_menu.add_cascade(label="Export As:", menu=export_as_menu)
        file_menu.add_command(label="Exit", command=self.__on_exit)

        # Configure the 'Tools' submenu inside the main menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Change Outline Color",
                               command=self.__choose_outline_color)
        tools_menu.add_command(label="Change Outline Width",
                               command=lambda: self.__change_width("Line"))
        tools_menu.add_command(label="Change Eraser Width",
                               command=lambda: self.__change_width("Eraser"))

        # Create the 'View' submenu inside the main menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle fullscreen",
                              command=lambda:
                              self.master.attributes("-fullscreen",
                                                     not self.master.attributes(
                                                         "-fullscreen")))
        view_menu.add_command(label="Nightly Mode",
                              command=lambda: self.__change_mode("black"))
        view_menu.add_command(label="Daily Mode",
                              command=lambda: self.__change_mode("white"))

        # Create "Choose Mode" submenu inside the "Tools" menu
        choose_mode_menu = tk.Menu(tools_menu, tearoff=0)
        choose_mode_menu.add_command(label="Drawing Mode",
                                     command=self.__set_drawing_mode)
        choose_mode_menu.add_command(label="Moving Objects Mode",
                                     command=self.__set_selecting_mode)
        tools_menu.add_cascade(label="Change Mode",
                               menu=choose_mode_menu)

        # Add al the submenus to the main menu
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        menubar.add_command(label="Clear Canvas", command=self.__delete_all)
        menubar.add_cascade(label=f"Current Mode: {self.__mode}",
                            menu=choose_mode_menu)

        # Add the main menu to the master window
        self.master.config(menu=menubar)

    def __change_mode(self, bg: str) -> None:
        """
        This function changes the background of the canvas
        :param bg: The background color to change to.
        """
        self.__outline_color = "white" if bg == "black" else "black"
        self.canvas.config(bg=bg)

    def __create_polygon_from_dots(self) -> None:
        """
        This function creates the polygon from the dots drawn by the user.
        """
        # If the length of the polygon points is lesser than on,
        # the tkinter.Canvas.create_polygon will throw an error, so we can't allow that
        if len(self.__polygon_points) >= 1:
            # Create a polygon using the stored points
            polygon = self.canvas.create_polygon(self.__polygon_points,
                                                 outline=self.__outline_color,
                                                 width=self.__line_width,
                                                 fill=self.__fill)
            # Clear the list of polygon points for the next polygon
            self.__polygon_points.clear()
            # Delete all the clicked (drawn) polygon dots from the canvas
            self.canvas.delete(*self.__polygon_dots)

            action: Dict[str, Any] = {
                'type': 'drawing',
                'object': polygon,
                'info': file_manager.get_item_info(self.canvas, polygon)
            }
            self.actions.append(action)
        else:
            # Inform the user of his invalid input
            messagebox.showwarning(title="Can't create polygon from dots!",
                                   message="You need to choose at least one "
                                           "dot to create the polygon.")
        self.__buttons_config(*self.__config_buttons)

    def __change_width(self, tool: str) -> None:
        """
        This function changes the width of the tool.
        :param tool: The tool to change its width.
        """
        self.__disable_canvas_touch()
        scale_window = tk.Toplevel(self.master)
        scale_window.resizable(False, False)
        scale_window.title(f"{tool} Width")
        scale: ttk.Scale = ttk.Scale(scale_window, from_=1, to=100,
                                     orient=tk.HORIZONTAL)
        scale.pack()

        scale_window.bind("<Right>", lambda event: scale.set(scale.get() + 1))
        scale_window.bind("<Left>", lambda event: scale.set(scale.get() - 1))

        # Create a Canvas widget to display the width
        width_canvas: tk.Canvas = tk.Canvas(scale_window, width=200, height=75)
        width_canvas.pack()

        # Draw a line on the Canvas widget with initial width
        line = width_canvas.create_line(50, 25, 150, 25, width=scale.get())

        def set_width() -> None:
            """
            This function sets the width based on the Scale widget value.
            """
            width = scale.get()
            if tool == "Eraser":
                self.__eraser_width = width
            elif tool == "Line":
                self.__line_width = width
            scale_window.destroy()
            self.__enable_canvas_touch()

        def update_line(value) -> None:
            """
            This function updates the line's width on the Canvas widget.
            """
            width = value
            width_canvas.itemconfigure(line, width=width)

        # Bind the Scale widget's command to the update_line function
        scale.config(command=update_line)

        # Add a button to set the width
        set_button: ttk.Button = ttk.Button(scale_window, text="Set Width",
                                            command=set_width)
        set_button.pack()

        # Bind the Enter key to the set_width function
        scale_window.bind('<Return>', lambda event: set_width())

    def __create_text(self, event_x: int, event_y: int) -> None:
        """
        This function creates the user's input text in (event_x, event_y) location
        :param event_x: X position of the user's input.
        :param event_y: Y position of the user's input.
        """
        self.__disable_canvas_touch()
        # Ask the user for the text
        text: Optional[str] = simpledialog.askstring(title="Add Text",
                                                     prompt="Enter the Text:")
        if text is None:
            # If we get here, this means the user has canceled the operation
            self.__enable_canvas_touch()
            return
        # Ask the user for the size of the text
        selected_size: Optional[int] = simpledialog.askinteger("Choose text"
                                                               " size",
                                                               "Enter the desired"
                                                               " size:",
                                                               minvalue=1,
                                                               maxvalue=100)
        if selected_size is None:
            # If we get here, this means the user has canceled the operation
            self.__enable_canvas_touch()
            return
        # Ask the user for the color of the text
        text_color: Optional[str] = askcolor()[1]
        if text_color is None:
            # If we get here, this means the user has canceled the operation
            self.__enable_canvas_touch()
            return
        # Create a window that the user will choose a font from
        font_window = tk.Toplevel(self.master)
        font_window.title("Select Font")
        # Make it not resizeable
        font_window.resizable(False, False)

        label = ttk.Label(font_window, text="Choose Font", font=("David", 14))
        label.pack(side=tk.TOP)

        # Create a frame for the font list and scrollbar
        font_frame = ttk.Frame(font_window)
        font_frame.pack(padx=10, pady=10)
        font_listbox = tk.Listbox(font_frame)
        font_listbox.pack(side=tk.LEFT)
        scrollbar = ttk.Scrollbar(font_frame, orient=tk.VERTICAL,
                                  command=font_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        font_listbox.config(yscrollcommand=scrollbar.set)

        # Add all the fonts to the listbox
        font_listbox.insert(tk.END, *FONT_OPTIONS)

        def select_font() -> None:
            """
            This function selects the font and adds the text to the canvas
            """
            selected_index: Tuple[int, ...] = font_listbox.curselection()
            if selected_index:
                selected_font: str = FONT_OPTIONS[selected_index[0]]
                font_window.destroy()
                # Create the text object
                text_obj: int = self.canvas.create_text(event_x, event_y,
                                                        text=text,
                                                        font=(selected_font,
                                                              selected_size),
                                                        fill=str(text_color))
                # Bind right-click event for the text object
                self.canvas.tag_bind(text_obj, "<Button-3>",
                                     lambda event, obj=text_obj:
                                     self.__on_text_right_click(event))

                action: Dict[str, Any] = {
                    'type': 'drawing',
                    'object': text_obj,
                    'info': file_manager.get_item_info(self.canvas, text_obj)
                }
                self.actions.append(action)
                self.__buttons_config(*self.__config_buttons)
            self.__enable_canvas_touch()

        # Add a button so the user will be able to select the font
        select_button = ttk.Button(font_window, text="Select",
                                   command=select_font)
        select_button.pack(pady=10)

        # Bind the "Enter" key to the select_font function
        font_window.bind('<Return>', lambda event: select_font())

    def __on_click(self, event: tk.Event) -> None:
        """
        This function handles <ButtonPress-1> event.
        :param event: The <ButtonPress-1> event to handle.
        """
        if self.__mode == 'Drawing Mode':
            self.__start_x: int = event.x
            self.__start_y: int = event.y
            if self.__current_drawable == "Pencil":
                self.__current_object = self.canvas.create_line(
                    event.x, event.y, event.x, event.y,
                    fill=self.__outline_color,
                    width=self.__line_width
                )
            elif self.__current_drawable == "Rectangle":
                self.__current_object = self.canvas.create_rectangle(
                    event.x, event.y, event.x, event.y,
                    outline=self.__outline_color,
                    width=self.__line_width,
                    fill=self.__fill
                )
            elif self.__current_drawable == "Oval":
                self.__current_object = self.canvas.create_oval(
                    event.x, event.y, event.x, event.y,
                    outline=self.__outline_color,
                    width=self.__line_width,
                    fill=self.__fill
                )
            elif self.__current_drawable == "Triangle":
                self.__triangle_start_x: int = event.x
                self.__triangle_start_y: int = event.y
                self.__current_object = self.canvas.create_polygon(
                    event.x, event.y, event.x, event.y, event.x, event.y,
                    outline=self.__outline_color,
                    width=self.__line_width,
                    fill=self.__fill
                )
            elif self.__current_drawable == "Text":
                self.__create_text(event.x, event.y)
        elif self.__mode == 'Polygon From Dots Mode':
            # Create a dot at the clicked point
            dot = self.canvas.create_oval(event.x - 2,
                                          event.y - 2,
                                          event.x + 2,
                                          event.y + 2,
                                          fill=self.__outline_color,
                                          outline='')
            self.__polygon_dots.append(dot)
            # Add the clicked point to the list of polygon points
            self.__polygon_points.append((event.x, event.y))

    def __on_drag(self, event: tk.Event) -> None:
        """
        This function handles <B1-Motion> event.
        :param event: The <B1-Motion> event to handle.
        """
        if self.__mode == 'Drawing Mode':
            if self.__current_drawable == "Pencil":
                if self.__start_x is not None and self.__start_y is not None:
                    line = self.canvas.create_line(self.__start_x,
                                                   self.__start_y,
                                                   event.x, event.y,
                                                   fill=self.__outline_color,
                                                   width=self.__line_width)
                    self.__start_x = event.x
                    self.__start_y = event.y
                    action = {
                        'type': 'drawing',
                        'object': line,
                        'info': file_manager.get_item_info(self.canvas, line)
                    }
                    self.actions.append(action)
            elif self.__current_drawable in ["Rectangle", "Oval", "Triangle"]:
                if self.__current_drawable == "Triangle":
                    self.canvas.coords(self.__current_object,
                                       self.__triangle_start_x,
                                       self.__triangle_start_y,
                                       event.x, event.y,
                                       event.x - (
                                               event.x - self.__triangle_start_x) * 2,
                                       event.y)
                else:
                    self.canvas.coords(self.__current_object, self.__start_x,
                                       self.__start_y, event.x, event.y)
            elif self.__current_drawable == "Eraser":
                if not self.canvas.find_all():  # If the canvas is empty
                    self.__disable_canvas_touch()  # Until the user clicks ok
                    messagebox.showinfo(title="Eraser Off",
                                        message="Eraser turned off because there"
                                                " are no objects on the canvas."
                                                "\nYour current mode is changed"
                                                " to 'Pencil'")
                    self.__enable_canvas_touch()
                    self.__current_drawable = "Pencil"
                    self.__buttons_config(*self.__config_buttons)
                    return
                # Find all objects within a certain radius around the mouse cursor
                overlapping_objects: Tuple[
                    int, ...] = self.canvas.find_overlapping(
                    event.x - self.__eraser_width,
                    event.y - self.__eraser_width,
                    event.x + self.__eraser_width,
                    event.y + self.__eraser_width
                )
                # Delete all overlapping objects
                for obj_id in overlapping_objects:
                    action = {
                        'type': 'delete object',
                        'object': obj_id,
                        'info': file_manager.get_item_info(self.canvas, obj_id)
                    }
                    self.actions.append(action)
                    self.canvas.delete(obj_id)

    def __on_release(self) -> None:
        """
        This function handles <ButtonRelease-1> event.
        """
        if self.__current_object:
            action = {
                'type': 'drawing',
                'object': self.__current_object,
                'info': file_manager.get_item_info(self.canvas,
                                                   self.__current_object)
            }
            self.actions.append(action)
            self.__current_object = 0
            self.__buttons_config(*self.__config_buttons)
            self.master.update()

    def __disable_canvas_touch(self) -> None:
        """
        This function disables the canvas' touch.
        """
        # Unbind canvas events
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def __enable_canvas_touch(self) -> None:
        """
        This function enables the canvas' touch.
        """
        # Rebind canvas events
        self.canvas.bind("<ButtonPress-1>", self.__on_click)
        self.canvas.bind("<B1-Motion>", self.__on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.__on_release())

    def __choose_drawable(self, drawable: str) -> None:
        """
        This function changes the current drawable to the desired drawable.
        :param drawable: The desired drawable.
        """
        # Check if the current mode is 'Polygon From Dots Mode'
        if self.__mode == 'Polygon From Dots Mode':
            # Clear the list of polygon points for the next polygon
            self.__polygon_points.clear()
            self.canvas.delete(*self.__polygon_dots)
        self.__mode = "Drawing Mode"
        self.__set_drawing_mode()
        self.__current_drawable = drawable

    def __choose_outline_color(self) -> None:
        """
        This function changes the outline color.
        """
        self.__disable_canvas_touch()
        color: Optional[str] = askcolor()[1]
        if color:
            self.__outline_color = color
        self.__enable_canvas_touch()

    def __set_polygon_mode(self) -> None:
        """
        This function sets the polygon from dots mode.
        """
        if self.__mode == 'Polygon From Dots Mode':
            return
        self.__polygon_button = ttk.Button(self.__frame,
                                           text="Create the polygon",
                                           command=lambda:
                                           self.__create_polygon_from_dots())
        self.__polygon_button.pack(side=tk.LEFT)
        self.canvas.bind("<ButtonPress-1>", self.__on_click)
        self.canvas.bind("<B1-Motion>", self.__on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.__on_release())
        self.canvas.bind("<Double-Button-3>", lambda event:
                         self.__set_selecting_mode())
        # Set the current shape to "Polygon From Dots"
        self.__current_drawable = "Polygon From Dots"
        # Set the draw mode to 'Polygon From Dots', in order to wait for user input
        self.__mode = 'Polygon From Dots Mode'
        self.__create_menus()  # Update the menus
        self.master.update()
        # Clear any existing polygon points
        self.__polygon_points.clear()

    def __set_drawing_mode(self) -> None:
        """
        This function sets the drawing mode.
        """
        self.__mode = 'Drawing Mode'
        self.__create_menus()  # Update the menus
        self.master.update()
        self.__current_drawable = "Pencil"
        self.canvas.bind("<ButtonPress-1>", self.__on_click)
        self.canvas.bind("<B1-Motion>", self.__on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.__on_release())
        self.canvas.bind("<Double-Button-3>", lambda event:
                         self.__set_selecting_mode())
        self.__polygon_button.destroy()

    def __set_selecting_mode(self) -> None:
        """
        This function sets the selecting objects mode.
        """
        if not self.canvas.find_all():  # If the canvas is empty
            self.__disable_canvas_touch()  # Until the user clicks ok
            messagebox.showinfo(title="ERROR!",
                                message="There are no objects on the canvas"
                                        " for you to move."
                                        "\nYour current mode is changed"
                                        " to 'Pencil'")
            self.__current_drawable = "Pencil"
            self.__buttons_config(*self.__config_buttons)
            self.__enable_canvas_touch()
            return
        self.__mode = 'Moving Objects Mode'
        self.__create_menus()  # Update the menus
        self.master.update()
        self.canvas.bind("<ButtonPress-1>", self.__select_object)
        self.canvas.bind("<B1-Motion>", self.__drag_object)
        self.canvas.bind("<Double-Button-3>", lambda event:
                         self.__set_drawing_mode())
        self.__polygon_button.destroy()

    def __select_object(self, event: tk.Event) -> None:
        """
        This function selects the closest object from the event.
        :param event: The event to handle.
        """
        if not self.canvas.find_all():  # If the canvas is empty
            self.__disable_canvas_touch()  # Until the user clicks ok
            messagebox.showinfo(title="ERROR!",
                                message="There are no objects on the canvas"
                                        " for you to move."
                                        "\nYour current mode is changed"
                                        " to 'Pencil'")
            self.__current_drawable = "Pencil"
            self.__buttons_config(*self.__config_buttons)
            self.__enable_canvas_touch()
            return
        # Clear any previously selected object
        self.__selected_object = 0
        self.__selected_object_start_x = 0
        self.__selected_object_start_y = 0

        # Find the object under the mouse cursor
        self.__selected_object = self.canvas.find_closest(event.x, event.y)[0]

        if self.__selected_object:
            # If an object is selected, record its starting coordinates
            bbox = self.canvas.bbox(self.__selected_object)
            self.__selected_object_start_x = bbox[0]
            self.__selected_object_start_y = bbox[1]

    def __drag_object(self, event: tk.Event) -> None:
        """
        This function drags the selected object over the canvas.
        :param event: The event to handle.
        """
        if not self.canvas.find_all():  # If the canvas is empty
            self.__disable_canvas_touch()  # Until the user clicks ok
            messagebox.showinfo(title="ERROR!",
                                message="There are no objects on the canvas"
                                        " for you to move."
                                        "\nYour current mode is changed"
                                        " to 'Pencil'")
            self.__current_drawable = "Pencil"
            self.__buttons_config(*self.__config_buttons)
            self.__enable_canvas_touch()
            return
        if self.__selected_object:
            prev_state = self.canvas.coords(self.__selected_object)

            # Calculate the distance moved by the mouse
            dx: int = event.x - self.__selected_object_start_x
            dy: int = event.y - self.__selected_object_start_y

            # Move the selected object by the calculated distance
            self.canvas.move(self.__selected_object, dx, dy)

            # Update the starting coordinates for the next drag event
            self.__selected_object_start_x = event.x
            self.__selected_object_start_y = event.y

            new_state = self.canvas.coords(self.__selected_object)
            action = {
                'type': 'moving',
                'object': self.__selected_object,
                'prev_state': prev_state,
                'new_state': new_state
            }
            self.actions.append(action)

    def __delete_all(self, is_redo: bool = False) -> None:
        """
        This function deletes all the objects on the canvas.
        :param is_redo: Whether this is a call from the redo function or not.
        """
        if is_redo:
            confirm = True
        else:
            confirm = messagebox.askyesno("Delete All?",
                                          "Are you sure you want to"
                                          " clear the canvas?")
        if confirm:
            action: Dict[str, Union[List[Dict[str, Any]], str]] = {
                'type': 'delete all'
            }
            actions_list: List[Dict[str, Any]] = []
            for obj in self.canvas.find_all():
                actions_list.append(
                    {'info': file_manager.get_item_info(self.canvas, obj)}
                )
            action['actions'] = actions_list
            self.actions.append(action)
            self.canvas.delete("all")
            self.__set_drawing_mode()
            self.__polygon_button = ttk.Button(self.__frame,
                                               text="Create the polygon",
                                               command=lambda:
                                               self.__create_polygon_from_dots())
            self.__buttons_config(*self.__config_buttons)

    def __undo(self) -> None:
        """
        This function undoes the last-done action
        """
        if self.actions:
            last_action: Dict[str, Any] = self.actions.pop()
            action_type = last_action['type']
            if action_type == 'drawing':
                self.canvas.delete(last_action['object'])
            elif action_type == 'moving':
                self.canvas.coords(last_action['object'],
                                   *last_action['prev_state'])
            elif action_type == 'change outline color':
                self.canvas.itemconfig(last_action['object'],
                                       outline=last_action['prev_state'])
            elif action_type == 'changing order':
                if last_action['prev_state']:
                    self.canvas.tag_raise(last_action['object'])
                else:
                    self.canvas.tag_lower(last_action['object'])
            elif action_type == "change text":
                self.canvas.itemconfig(last_action['object'],
                                       text=last_action['prev_text'])
            elif action_type == "change fill":
                self.canvas.itemconfig(last_action['object'],
                                       fill=last_action['prev_state'])
            elif action_type == 'change width':
                self.canvas.itemconfig(last_action['object'],
                                       width=last_action['prev_state'])
            elif action_type == 'delete object':
                file_manager.recreate_object(self.canvas, self.actions,
                                             last_action['info'],
                                             self.__on_text_right_click)
            elif action_type in ['change text size', 'change object font']:
                self.canvas.itemconfig(last_action['object'],
                                       font=last_action['prev_font'])
            elif action_type == 'delete all':
                for item in last_action['actions']:
                    file_manager.recreate_object(self.canvas, self.actions,
                                                 item['info'],
                                                 self.__on_text_right_click)
            elif action_type == 'rotate object':
                self.canvas.delete(last_action['new_object'])
                last_action['old_object'] = self.canvas.create_polygon(
                    last_action['old_info']['coords'],
                    outline=last_action['old_info']['outline'],
                    width=last_action['old_info']['width'],
                    fill=last_action['old_info']['fill']
                )
                last_action['old_info'] = file_manager.get_item_info(
                    self.canvas, last_action['old_object']
                )
            self.__undone_actions.append(last_action)
        self.__buttons_config(*self.__config_buttons)
        self.master.update()

    def __redo(self) -> None:
        """
        This function redoes the last undone action.
        """
        if self.__undone_actions:
            last_undone_action = self.__undone_actions.pop()
            action_type = last_undone_action['type']
            if action_type == 'drawing':
                obj_info: Dict[str, Any] = last_undone_action['info']
                file_manager.recreate_object(self.canvas, self.actions,
                                             obj_info,
                                             self.__on_text_right_click)
            elif action_type == 'moving':
                self.canvas.coords(last_undone_action['object'],
                                   *last_undone_action['new_state'])
            elif action_type == 'change outline color':
                self.canvas.itemconfig(last_undone_action['object'],
                                       outline=last_undone_action['new_state'])
            elif action_type == 'changing order':
                if last_undone_action['prev_state']:
                    self.canvas.tag_lower(last_undone_action['object'])
                else:
                    self.canvas.tag_raise(last_undone_action['object'])
            elif action_type == "change text":
                self.canvas.itemconfig(last_undone_action['object'],
                                       text=last_undone_action['new_text'])
            elif action_type == "change fill":
                self.canvas.itemconfig(last_undone_action['object'],
                                       fill=last_undone_action['new_state'])
            elif action_type == 'change width':
                self.canvas.itemconfig(last_undone_action['object'],
                                       width=last_undone_action['new_state'])
            elif action_type == 'delete object':
                self.canvas.delete(last_undone_action['object'])
            elif action_type in ['change text size', 'change object font']:
                self.canvas.itemconfig(last_undone_action['object'],
                                       font=last_undone_action['new_font'])
            elif action_type == "delete all":
                self.__delete_all(True)
            elif action_type == 'rotate object':
                self.canvas.delete(last_undone_action['old_object'])
                last_undone_action['new_object'] = self.canvas.create_polygon(
                    last_undone_action['new_info']['coords'],
                    outline=last_undone_action['new_info']['outline'],
                    width=last_undone_action['new_info']['width'],
                    fill=last_undone_action['new_info']['fill']
                )
                last_undone_action['new_info'] = file_manager.get_item_info(
                    self.canvas, last_undone_action['new_object']
                )
            self.actions.append(last_undone_action)
        self.__buttons_config(*self.__config_buttons)
        self.master.update()

    def __save_canvas(self) -> None:
        """
        This function saves the canvas.
        """
        ans = False
        if self.file_path[0] != '':  # If the canvas has been saved
            ans = messagebox.askyesno("Save Canvas",
                                      "Your current canvas location is:"
                                      f" {self.file_path[0]}"
                                      "\nWould you like to change its location?")
        else:
            messagebox.showinfo("Save Canvas",
                                "Select where you want to save your canvas.")
        file_manager.save_canvas(self.canvas, self.file_path, ans)

    def __save_as_type(self, type_to_save_as: str) -> None:
        """
        This function saves the canvas as a .type_to_save file.
        :param type_to_save_as: The type to save the canvas as.
        """
        # Destroy the frame
        self.__frame.destroy()

        file_manager.save_as_type(self.master, self.canvas,
                                  f'{type_to_save_as}')

        # Create again the frame
        self.__frame = ttk.Frame(self.master)
        self.__create_menus()
        self.__init_frame_buttons()
        self.__frame.place(relx=0, rely=0)
        self.master.update()

    def __on_exit(self) -> None:
        """
        This function manages the exit of the program.
        """
        # Make sure the user wants to exit the program
        ans = messagebox.askyesno(title="Exit?",
                                  message="Are you sure you want to exit?")
        if ans:
            ans = messagebox.askyesno(title="Save Canvas",
                                      message="Would you like to save your "
                                              "canvas for future drawins?")
            if ans:
                self.__save_canvas()
            self.master.quit()
