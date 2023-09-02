"""App class for the logic of the app"""
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QLineEdit, QLabel
from PyQt5.QtGui import QFont, QFontDatabase
import daemon
from filemanager import FileManager
from pynput import keyboard as kb
import re


# Color palette: https://colors.muz.li/palette/361d32/543c52/f55951/edd2cb/f1e8e6


class Font(QFont):
    def __init__(self, font_name: str, size: int, custom_font: bool = False, weight: int = None):
        font = font_name
        if custom_font:
            font_id = QFontDatabase.addApplicationFont(f"{font_name}.ttf")
            if font_id < 0:
                print("Error")
                raise Exception("Font not found")
            else:
                font = QFontDatabase.applicationFontFamilies(font_id)[0]
        super().__init__(font, size)
        if weight:
            self.setWeight(weight)


class QtStyleSheet:
    """Representation for a CSS Stylesheet"""

    @classmethod
    def to_string(cls, sheet_dictionary: dict) -> str:  # TODO: CHANGE GIVEN PARAM TO BE A DICTIONARY
        """Return a string representation of the stylesheet.The parameter name
        must be a CSS property and the given value will be the value in the
        stylesheet"""
        sheet = ""
        # Unwrap the kwargs parameters
        for param, value in sheet_dictionary.items():
            sheet += f"{param}: {value};"
        return sheet


class Label(QLabel):
    def __init__(self, content: str, stylesheet: str, font: Font, parent=None, pos_x=None, pos_y=None):
        """Initialize a QT Label"""
        super().__init__(content, parent)
        self.setFont(font)
        self.setStyleSheet(stylesheet)
        if pos_x and pos_y:
            self.position(pos_x, pos_y)
        # Adjust size of the label to the text
        self.adjustSize()

    def position(self, left, top):
        """Position the label relative to its parent"""
        self.move(left, top)

    def set_style(self, stylesheet: str):
        """Set the stylesheet of the label"""
        self.setStyleSheet(stylesheet)


class App:
    def __init__(self):
        """"Initialize the app"""
        super().__init__()
        # Initialize the main window
        self.curr_window = QMainWindow()
        self.curr_window.setWindowTitle("SafeKeys")
        self.curr_window.setFixedSize(700, 500)
        # Get the custom hotkey
        self.custom_key = FileManager.read_content("./elem/hk.txt")
        if self.custom_key is None:
            self.custom_key = str()
            # Define custom hotkey
            self.custom_hotkey()
        self.hotkeys = {  # TODO: ADD FUNCTIONALITIES TO THE HOTKEYS
            "<ctrl>+<alt>+c": None,
            "<ctrl>+<alt>+b": None,
            "<ctrl>+<alt>+u": None,
            "CUSTOM": None,
        }
        # self.listener = daemon.Daemon(self.hotkeys, None) # TODO: DEFINE on_move FUNC
        self.main_window()

    def clean_window(self):
        # Clean the main window
        if self.curr_window.isVisible():
            self.curr_window.hide()
        self.curr_window = QMainWindow()
        self.curr_window.setWindowTitle("SafeKeys")
        self.curr_window.setFixedSize(700, 500)

    def custom_hotkey(self):
        """Define the custom hotkey"""
        def on_press(key):
            """Read the pressed key of the user"""
            prohibited = [kb.Key.esc, kb.Key.cmd, kb.Key.print_screen,
                          kb.Key.scroll_lock, kb.Key.pause, kb.Key.caps_lock,
                          kb.Key.tab, kb.Key.backspace]
            if key == kb.Key.enter and self.custom_key != "":
                listener.stop()
                return
            elif key == kb.Key.enter and self.custom_key == "":
                # TODO: Raise window saying the key can't be empty
                pass
            # Check if the key is permited
            if key not in prohibited:
                if isinstance(key, kb.Key):
                    print(str(key))
                    char_key = re.search("(?<=\.)\w+", str(key))
                    char_key = char_key.group(0)
                    if char_key is not None and char_key not in self.custom_key:
                        self.custom_key += f"<{char_key}>+"
                else:
                    if str(key) not in self.custom_key:
                        self.custom_key += f"{key}+"
                        print(self.custom_key)
            else:
                # TODO: Raise window telling pressed key is prohibited
                pass
        # Styles
        window_stylesheet = {
            "background-color": "#361d32",
        }
        font_style = {
            "color": "#f55951",
        }
        label_stylesheet = QtStyleSheet.to_string(font_style)
        font = Font("Roboto-Regular", 16, True, 200)
        light_font = Font("Roboto-Regular", 14, True, 150)
        # Labels
        title = Label("Lets Define your new Hotkey!\n    Press your new hotkey...",
                      label_stylesheet,
                      font,
                      self.curr_window,
                      220,
                      175)
        press_enter = Label("Press enter when finished",
                            label_stylesheet,
                            light_font,
                            self.curr_window,
                            240,
                            275)
        self.curr_window.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))
        # Start the hotkey listener
        listener = kb.Listener(on_press=on_press)
        listener.start()
        self.curr_window.show()

    def main_window(self):
        """Main window of the program. Set all
        the widgets to show the main window"""
        # Stylesheets' dictionaries
        window_stylesheet = {
            "background-color": "#361d32",
        }
        font_style = {
            "color": "#f55951",
        }
        # Stylesheets
        label_stylesheet = QtStyleSheet.to_string(font_style)
        # Fonts
        title_font = Font("Roboto-Regular", 20, True, 250)
        content_font = Font("Roboto-Regular", 16, True, 200)
        # Clear the window to draw the elements of it
        self.curr_window.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))

        # Set the labels
        title = Label("SafeKeys", label_stylesheet, title_font, self.curr_window, 25, 15)
        hotkey = Label(f"Hotkey: CUSTOM", label_stylesheet, content_font, self.curr_window, 25,
                       300)  # TODO: ADD CUSTOM HOTKEY MESSAGE
        change = Label("Change Hotkey: ctrl + alt + c", label_stylesheet, content_font, self.curr_window, 25, 400)
        check = Label("See Hotkey: ctrl + alt + b", label_stylesheet, content_font, self.curr_window, 350, 300)
        about = Label("About us: ctrl + alt + u", label_stylesheet, content_font, self.curr_window, 350, 400)

        # Initialize mouse and keyboard listeners
        # listener = daemon.Daemon()  # TODO: GET CUSTOM HOTKEY

        self.curr_window.show()

    def change_hotkey_window(self):
        """Open the check hotkey window"""
