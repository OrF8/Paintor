from PIL import ImageGrab
from tkinter import filedialog, messagebox
from typing import List, Dict, Any, Union, Callable
import tkinter as tk
import time
import json
import canvasvg
import os

REQUIRED_KEYS: Dict[str, List[str]] = {
        "line": ["type", "coords", "fill", "width"],
        "rectangle": ["type", "coords", "fill", "width", "outline"],
        "oval": ["type", "coords", "fill", "width", "outline"],
        "polygon": ["type", "coords", "fill", "width", "outline"],
        "text": ["type", "coords", "fill", "text", "font"]
    }


def get_item_info(canvas: tk.Canvas, item: Union[str, int]) -> Dict[str, Any]:
    """
    This function gets the info of object item
    :param canvas: The canvas the item belongs to.
    :param item: The item to get the info of.
    :return: A dictionary containing all of item's info.
    """
    obj_type: str = canvas.type(item)
    obj_info: Dict[str, Any] = {}
    if obj_type == "line":
        obj_info = {
            "type": obj_type,
            "coords": canvas.coords(item),
            "fill": canvas.itemcget(item, "fill"),
            "width": canvas.itemcget(item, "width")
        }
    elif obj_type in ["rectangle", "oval", "polygon"]:
        obj_info = {
            "type": obj_type,
            "coords": canvas.coords(item),
            "fill": canvas.itemcget(item, "fill"),
            "outline": canvas.itemcget(item, "outline"),
            "width": canvas.itemcget(item, "width")
        }
    elif obj_type == "text":
        obj_info = {
            "type": obj_type,
            "coords": canvas.coords(item),
            "text": canvas.itemcget(item, "text"),
            "fill": canvas.itemcget(item, "fill"),
            "font": canvas.itemcget(item, "font"),
        }
    return obj_info


def save_canvas(canvas: tk.Canvas, file_path: List[str] = '',
                is_change: bool = False) -> None:
    """
    This function saves the canvas as a .JSON file
    to continue drawing on it later.
    :param canvas: The canvas to save.
    :param file_path: The path the canvas has been saved to.
                      Defaults to ''.
    :param is_change: Whether to change to canvas' location or not.
                      Defaults to False.
    """
    path = file_path[0]
    if path == '' or is_change:  # If the canvas hos not been saved yet
        # Prompt the user to choose the file to save the canvas
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")],
                                            initialfile="canvas")
    if path:  # If the user has chosen a location
        if is_change:
            # Delete the other location of the canvas
            os.remove(file_path[0])
        # Gather information about all drawn objects on the canvas
        objects: List[Dict[str, Any]] = [{"mode": canvas.cget("bg")}]
        for item in canvas.find_all():
            obj_info = get_item_info(canvas, item)
            objects.append(obj_info)

        # Write the gathered information to the .JSON file
        with open(path, "w") as file:
            json.dump(objects, file)
            if path == '':
                messagebox.showinfo("Success!",
                                    "Your canvas has been saved to:"
                                    f"\n{path}\nBe sure to remember its location!")
        file_path[0] = path


def check_required_keys(obj: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    This function check if all the required keys for this object
    are present in the object.
    :param obj: The object to check whether the required keys are present in.
    :param required_keys: The required keys to be present in the object.
    :return: True if the required keys are present in the object, False otherwise.
    """
    for key in required_keys:
        if key not in obj:
            return False
    return True


def is_parsed_correctly(objects: List[Dict[str, Any]]) -> bool:
    """
    This function makes sure that the .JSON file is parsed correctly.
    :param objects: The objects in the .JSON file
                    to check if they are parsed correctly.
    :return (bool): True if the .JSON file is parsed correctly, False otherwise.
    """
    mode = objects[0]
    try:
        if mode['mode'] not in ['white', 'black']:
            return False
    except KeyError:
        return False
    for obj in objects[1:]:
        try:
            obj_type = obj["type"]
        except KeyError:
            return False
        if obj_type is None or obj_type not in REQUIRED_KEYS:
            return False
        if not check_required_keys(obj, REQUIRED_KEYS[obj_type]):
            return False
    # If we get here, this means that all the objects in the .JSON file are
    # parsed correctly, so return Tre
    return True


def recreate_object(canvas: tk.Canvas, actions_list: List[Dict[str, Any]],
                    obj_info: Dict[str, Any],
                    text_right_click_callback: Callable[[tk.Event], None]) -> None:
    """
    This function recreates an object.
    :param canvas: The canvas the object belongs to.
    :param actions_list: A list of actions to add all the actions to.
    :param obj_info: The object's information.
    :param text_right_click_callback: A callback to bind text objects to.
    """
    new_obj_info = obj_info
    obj_type = obj_info["type"]
    action: Dict[str, Any] = {
        'type': 'drawing'
    }
    if obj_type == "line":
        obj = canvas.create_line(obj_info["coords"], fill=obj_info.get("fill", ""),
                                 width=obj_info.get("width", 1))
        new_obj_info['object'] = obj
        action['object'] = obj
        action['info'] = get_item_info(canvas, obj)
    elif obj_type == "rectangle":
        obj = canvas.create_rectangle(obj_info["coords"], fill=obj_info.get("fill", ""),
                                      outline=obj_info.get("outline", ""),
                                      width=obj_info.get("width", 1))
        action['object'] = obj
        action['info'] = get_item_info(canvas, obj)
    elif obj_type == "oval":
        obj = canvas.create_oval(obj_info["coords"], fill=obj_info.get("fill", ""),
                                 outline=obj_info.get("outline", ""),
                                 width=obj_info.get("width", 1))
        new_obj_info['object'] = obj
        action['object'] = obj
        action['info'] = get_item_info(canvas, obj)
    elif obj_type == "polygon":
        obj = canvas.create_polygon(obj_info["coords"], fill=obj_info.get("fill", ""),
                                    outline=obj_info.get("outline", ""),
                                    width=obj_info.get("width", 1))
        new_obj_info['object'] = obj
        action['object'] = obj
        action['info'] = get_item_info(canvas, obj)
    elif obj_type == "text":
        text_obj = canvas.create_text(obj_info["coords"], text=obj_info["text"],
                                      fill=obj_info.get("fill", ""),
                                      font=obj_info.get("font", ""))
        # Bind right-click event for text objects
        canvas.tag_bind(text_obj, "<Button-3>",
                        lambda event=obj_info["coords"]:
                        text_right_click_callback(event))
        new_obj_info['object'] = text_obj
        action['object'] = text_obj
        action['info'] = get_item_info(canvas, text_obj)
    actions_list.append(action)


def load_canvas(canvas: tk.Canvas, actions_list: List[Dict[str, Any]],
                text_right_click_callback: Callable[[tk.Event], None],
                file_path: List[str]) -> None:
    """
    This function loads the canvas from a .JSON file.
    :param canvas: The canvas to load the .json file to.
    :param actions_list: A list of actions to add all the actions to.
    :param text_right_click_callback: A function to bind mouse button 3's clicks
                                      to in order for the text context menu to
                                      be displayed for loaded text objects.
    :param file_path: The path of the file will be saved here.
    """
    # Prompt the user to choose the file to load the canvas from
    path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if path:
        # Read the .JSON file and load the drawn objects
        with open(path, "r") as file:
            try:
                objects: List[Dict[str, Any]] = json.load(file)
            except json.decoder.JSONDecodeError as e:
                messagebox.showerror("ERROR!",
                                     "Your.JSON file is not parsed correctly!"
                                     f"\n{e}"
                                     "\nIt may not have been created by this software!"
                                     "\nThe software will now create an empty canvas."
                                     " If you wish to load an existing canvas, "
                                     "restart the program or import a canvas."
                                     )
                return
        if not is_parsed_correctly(objects):
            messagebox.showerror("ERROR!",
                                 "Your.JSON file is not parsed correctly!"
                                 "\nIt may not have been created by this software!"
                                 "\nThe software will now create an empty canvas."
                                 " If you wish to load an existing canvas, "
                                 "restart the program or import a canvas.")
            return
        canvas.config(bg=objects[0]['mode'])
        objects = objects[1:]
        # Recreate the drawn objects on the canvas
        for obj in objects:
            recreate_object(canvas, actions_list, obj, text_right_click_callback)
        file_path[0] = path


def get_filetypes(type_to_save_as: str) -> str:
    """
    This function returns the available filetypes associated with type_to_save_as.
    :param type_to_save_as: Type of the files to save.
    """
    if type_to_save_as == "jpg":
        return "*.jfif *.jpe *.jpg *.jpeg"
    elif type_to_save_as == "pdf":
        return "*.pdf"
    elif type_to_save_as == "eps":
        return "*.eps *.ps"
    elif type_to_save_as == "gif":
        return "*.gif"
    elif type_to_save_as == "png":
        return "*.png *.apng"
    return ''


def save_as_type(master: tk.Tk, canvas: tk.Canvas, type_to_save_as: str) -> None:
    """
    This function saves the canvas as a .type_to_save_as file.
    :param master: The parent of the canvas.
    :param canvas: The canvas to save.
    :param type_to_save_as: The type to save the canvas as.
    """
    # Prompt the user to choose the file path for saving the file
    file_path = filedialog.asksaveasfilename(defaultextension=f".{type_to_save_as}",
                                             filetypes=[
                                                 (f"{type_to_save_as.upper()} files",
                                                  f"{get_filetypes(type_to_save_as)}")],
                                             initialfile="canvas")
    if file_path:

        was_fullscreen = master.attributes("-fullscreen")

        # Change to a fullscreen
        master.attributes("-fullscreen", True)
        # Make sure the canvas is on top of the master
        master.attributes("-topmost", False)
        master.update()

        # Wait for the screen to turn fullscreen
        time.sleep(0.2)

        # Take the screenshot
        img = ImageGrab.grab(canvas.winfo_x(), canvas.winfo_y())

        # Change to the previous screensize
        master.attributes("-fullscreen", was_fullscreen)

        # Save the screenshot
        img.save(file_path, f"{type_to_save_as.upper()}", resolution=100.0)

        messagebox.showinfo("Success!",
                            "Your canvas has been exported to:\n"
                            f"{file_path}\nAs a .{type_to_save_as.upper()} file")


def save_as_svg(canvas: tk.Canvas) -> None:
    """
    This function saves the canvas as a .svg file.
    :param canvas: The canvas to save.
    """
    # Prompt the user to choose the file path for saving the file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".svg",
        filetypes=[
            (".SVG files",
             "*.svg")],
        initialfile="canvas")
    if file_path:
        # Save the file
        canvasvg.saveall(file_path, canvas)
        messagebox.showinfo("Success!",
                            "Your canvas has been exported to:"
                            f"\n{file_path}\nAs a .SVG file")
