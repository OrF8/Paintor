from PIL import Image, ImageTk
from tkinter import messagebox
from bigvars import HELP
from typing import List
import canvas
import tkinter as tk
import sys
import os

if os.name == 'posix':  # If linux
    IMAGE_PATHS: List[str] = [
        "Images/step1.png", "Images/step2.png", "Images/step3.png",
        "Images/step4.png", "Images/step5.png", "Images/step6.png",
        "Images/step7.png", "Images/step8.png", "Images/step9.png",
        "Images/step10.png", "Images/last.png"
    ]
else:
    IMAGE_PATHS: List[str] = [
        "Images\\step1.png", "Images\\step2.png", "Images\\step3.png",
        "Images\\step4.png", "Images\\step5.png", "Images\\step6.png",
        "Images\\step7.png", "Images\\step8.png", "Images\\step9.png",
        "Images\\step10.png", "Images\\last.png"
    ]


def on_enter(event: tk.Event, fg: str = '') -> None:
    """
    This function handles the "<Enter>" event.
    :param event: The event to handle.
    :param fg: The color to change the foreground to.
               Defaults to empty string.
    """
    event.widget.config(bg="light gray")
    if fg != '':
        event.widget.config(fg=fg)


def on_leave(event: tk.Event, bg: str = "white", fg: str = "black") -> None:
    """
    Thi function handles the "<Leave>" event.
    :param event: The event to handle.
    :param bg: The color to change the background to.
               Defaults to white
    :param fg: The color to change the foreground to.
               Defaults to black.
    """
    event.widget.config(bg=bg, fg=fg)


class State:
    """
    This class is used
    to check if the user wants to load an existing canvas or not, and
    whether he exited the hello screen or not.

    Attributes:
        state (bool):
        'T'
        if the user wants to load an existing canvas,
        'F'
        if the user does not want to load an existing canvas,
        '' if the user exited the hello screen.
    """
    def __init__(self, state: str = 'F') -> None:
        """
        Initializes the IsClicked object with False as the default value.
        """
        self.state: str = state


def tutorial(window: tk.Tk, is_load: State) -> None:
    """
    This function shows a tutorial on how to use the Or's Illustrator.
    :param window: A window to destroy.
    :param is_load: Whether or not the user wants to load an existing canvas.
    """
    window.destroy()
    window = tk.Tk()
    window.resizable(False, False)
    window.title("Tutorial")
    current_image_index = 0

    def show_new_image(plus: bool = True) -> None:
        """
        This function shows the next image and configures the buttons.
        :param plus: Whether or not to increment the current index.
                     If plus=True, increment the index.
                     Else, decrement the index.
        """
        nonlocal current_image_index
        if plus:
            # Increment index to show the next image
            current_image_index += 1
        else:
            if current_image_index == 0:
                # If we get here, this means the user pressed the left arrow
                # and the image is the first image,
                # so do nothing (return)
                return
            # Decrement index to show the previous image
            current_image_index -= 1
        # Check if this is the last image
        if current_image_index == len(IMAGE_PATHS):
            window.destroy()
            return
        if current_image_index == len(IMAGE_PATHS)-1:
            next_button.config(text="Exit Tutorial")
        else:
            next_button.config(text="Next Step")
        if current_image_index == 0:
            prev_button.config(state=tk.DISABLED)
        else:
            prev_button.config(state=tk.NORMAL)
        # Load the image
        img = Image.open(IMAGE_PATHS[current_image_index])
        img_tk = ImageTk.PhotoImage(img)
        # Update the label to show the new image
        label.configure(image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection

    # Display the initial image
    image = Image.open(IMAGE_PATHS[current_image_index])
    image_tk = ImageTk.PhotoImage(image)
    # Display the image on a label
    label = tk.Label(window, image=image_tk)
    label.image = image_tk  # Keep a reference to avoid garbage collection
    label.pack()

    # Bind the right and left arrows to show images
    window.bind('<Right>', lambda event: show_new_image())
    window.bind('<Left>', lambda event: show_new_image(False))

    # Button to show the next image
    next_button = tk.Button(window, text="Next Step", command=show_new_image,
                            relief="flat")
    next_button.bind("<Enter>", on_enter)
    next_button.bind("<Leave>", on_leave)
    next_button.pack(side=tk.RIGHT)

    # Button to show the previous image
    prev_button = tk.Button(window, text="Previous Step",
                            command=lambda: show_new_image(False),
                            relief="flat", state=tk.DISABLED)
    prev_button.bind("<Enter>", on_enter)
    prev_button.bind("<Leave>", on_leave)
    prev_button.pack(side=tk.RIGHT)

    # Button to exit the tutorial
    exit_button = tk.Button(window, text="Exit The Tutorial",
                            command=window.destroy,
                            relief="flat")
    exit_button.bind("<Enter>", on_enter)
    exit_button.bind("<Leave>", on_leave)
    exit_button.pack(side=tk.LEFT)

    window.mainloop()

    # Return to the main window after the tutorial window has been destroyed
    hello_window(is_load)


def click(tk_window: tk.Tk, is_load_button: State) -> None:
    """
    This function changes the state of is_lod_button variable to let the
    "if __name__ == '__main__'"
    part of the program know that the user wants
    to load an existing canvas.
    :param tk_window: A window to destroy.
    :param is_load_button: The button to change its state.
    """
    is_load_button.state = 'T'
    tk_window.destroy()


def on_exit(window: tk.Tk, is_load: State) -> None:
    """
    This function that handles the "WM_DELETE_WINDOW" event.
    :param window: A window to destroy.
    :param is_load: Whether or not the user wants to load an existing canvas.
    """
    # Make sure the user wants to exit the program
    ans = messagebox.askyesno(title="Exit?",
                              message="Are you sure you want to exit?")
    if ans:
        # Change the state to make sure that the
        # "if __name__ == '__main__'"
        # part of the program know that the user exited the program.
        is_load.state = ''
        window.destroy()


def hello_window(is_load: State) -> None:
    """
    This function shows the initial window.
    """
    window: tk.Tk = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", lambda: on_exit(window, is_load))
    window.geometry("480x100")
    window.resizable(False, False)
    window.title("Or's Illustrator")

    frame: tk.Frame = tk.Frame(window)
    frame.configure(bg="black")
    frame.pack(fill=tk.BOTH, expand=True)

    label: tk.Label = tk.Label(frame, text="Welcome to Or's Illustrator!",
                               font=("David", 23), bg="black", fg="white")
    label.pack(fill=tk.BOTH, expand=True)

    load_button = tk.Button(window, text="Load an existing canvas",
                            command=lambda: click(window, is_load),
                            relief="raised", borderwidth=0,
                            bg="black", fg="white")
    new_canvas_button = tk.Button(window, text="Create an empty canvas",
                                  command=window.destroy, relief="raised",
                                  borderwidth=0, bg="black", fg="white")
    tutorial_button = tk.Button(window, text="Watch a tutorial",
                                command=lambda: tutorial(window, is_load),
                                relief="raised", borderwidth=0,
                                bg="black", fg="white")

    load_button.bind("<Enter>", lambda event, color="black":
                     on_enter(event, fg=color))
    load_button.bind("<Leave>", lambda event, color="black", fg="white":
                     on_leave(event, color, fg))
    new_canvas_button.bind("<Enter>", lambda event, color="black":
                           on_enter(event, fg=color))
    new_canvas_button.bind("<Leave>", lambda event, color="black", fg="white":
                           on_leave(event, color, fg))
    tutorial_button.bind("<Enter>", lambda event, color="black":
                         on_enter(event, fg=color))
    tutorial_button.bind("<Leave>", lambda event, color="black", fg="white":
                         on_leave(event, color, fg))

    load_button.pack(side=tk.LEFT)
    tutorial_button.pack(side=tk.LEFT)
    new_canvas_button.pack(side=tk.LEFT)
    window.mainloop()


def main() -> None:
    """
    This function runs the first part of the program.
    """
    if "--help" in sys.argv:
        print(HELP)
    else:
        is_load: State = State()
        hello_window(is_load)
        if is_load.state != '':  # If the user didn't exit from the hello screen
            # Create a new root
            root: tk.Tk = tk.Tk()
            # Create a new canvas
            canvas.CanvasApp(root,
                             True if is_load.state == 'T' else False)
            # run the new root
            root.mainloop()


if __name__ == "__main__":
    main()
