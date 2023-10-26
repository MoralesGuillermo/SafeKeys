"""App class for the logic of the app"""
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QLabel, QDialog, QShortcut
from PyQt5.QtGui import QFont, QFontDatabase, QKeyEvent, QKeySequence, QMouseEvent
from PyQt5.QtCore import Qt, QPoint
from pynput.mouse import Controller as MController
import keyboard

import HotkeyDAO as HD

# Color palette: https://colors.muz.li/palette/361d32/543c52/f55951/edd2cb/f1e8e6
filepath = os.path.join(os.getcwd(), "elem", "hk.csv")

# Default Key Sequence
CHANGE_KEY = Qt.CTRL + Qt.ALT + Qt.Key_C
ABOUT_US_KEY = Qt.CTRL + Qt.ALT + Qt.Key_U
CHECK_KEY = Qt.CTRL + Qt.ALT + Qt.Key_B

# Key Map
key_value_map = dict()
for k, v in vars(Qt).items():
    if isinstance(v, Qt.Key):
        key_value_map[int(v)] = k.partition("_")[2]

modifiers = {
    Qt.Key_Control: Qt.CTRL,
    Qt.Key_Shift: Qt.SHIFT,
    Qt.Key_Alt: Qt.ALT,
}

print(modifiers)


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
    def to_string(cls, sheet_dictionary: dict) -> str:
        """Return a string representation of the stylesheet.The parameter name
        must be a CSS property and the given value will be the value in the
        stylesheet"""
        sheet = ""
        # Unwrap the dictionary's items
        for param, value in sheet_dictionary.items():
            sheet += f"{param}: {value};"
        return sheet


class Dialog(QDialog):
    def __init__(self, title: str, text: str, button: str, stylesheet: str = None):
        super().__init__()
        self.title = title
        self.text = text
        self.button = button
        self.style = stylesheet

    def show(self):
        """"Show the dialog box"""
        # Add items to the dialog box
        self.setWindowTitle(self.title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        label = QLabel(self.text, self)
        button = QPushButton(self.button, self)
        label.move(100, 100)
        button.move(200, 150)
        button.clicked.connect(self.__close)
        if self.style:
            self.setStyleSheet(self.style)
        self.exec()

    def __close(self):
        """Close the dialog box function"""
        self.close()


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.secondary_window = None
        self.hidden = False
        self.hotkey_label = None
        self.custom_key = str()
        self.file_dao = HD.HotkeyDAO(filepath)
        self.__read_dao_model()
        self.__read_custom_key()
        self.__activate_shortcuts()
        self.__init_ui()
        self.hide_if_hidden()

    def __read_dao_model(self):
        self.file_dao.read_file()

    def __read_custom_key(self):
        if self.file_dao.key is not None:
            return self.file_dao.key
        self.custom_key = str()
        self.custom_key_window()
        self.change_hidden_status()

    def __change_hidden_status(self):
        self.hidden = not self.hidden

    def __activate_shortcuts(self):
        self.__generate_all_keys()
        self.__activate_all_keys()

    def __generate_all_keys(self):
        def generate(hotkey):
            return QShortcut(QKeySequence(hotkey), self)

        global CHANGE_KEY, ABOUT_US_KEY, CHECK_KEY
        self.change_key_hotkey = generate(CHANGE_KEY)
        self.about_us_hotkey = generate(ABOUT_US_KEY)
        self.check_key_hotkey = generate(CHECK_KEY)
        self.custom_key_hotkey = generate(self.custom_key)

    def __activate_all_keys(self):
        def activate(hotkey: QShortcut, event):
            hotkey.activated.connect(event)

        activate(self.change_key_hotkey, self.custom_key_window)
        activate(self.about_us_hotkey, self.about_us_window)
        activate(self.check_key_hotkey, self.check_key_window)
        activate(self.custom_key_hotkey, self.safemode)

    def __init_ui(self):
        """Main window's UI"""
        self.setWindowTitle("Safekeys")
        self.setFixedSize(700, 500)
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
        self.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))

        # Set the labels
        title = Label("SafeKeys", label_stylesheet, title_font, self, 25, 15)
        self.hotkey_label = Label(f"Hotkey: CUSTOM", label_stylesheet, content_font, self, 25, 300)
        change = Label("Change Hotkey: ctrl + alt + c", label_stylesheet, content_font, self, 25, 400)
        check = Label("See Hotkey: ctrl + alt + b", label_stylesheet, content_font, self, 350, 300)
        about = Label("About us: ctrl + alt + u", label_stylesheet, content_font, self, 350, 400)

        self.show()

    def hide_if_hidden(self):
        if self.hidden:
            self.hide()
            self.__change_hidden_status()

    def custom_key_window(self):
        """Go to the custom key window"""
        self.secondary_window = ChangeHotKey(self)

    def get_custom_key(self):
        return self.custom_key

    def set_custom_key(self, value):
        self.custom_key = value
        self.__apply_hotkey()

    def about_us_window(self):
        self.secondary_window = AboutUs(self)

    def check_key_window(self):
        self.secondary_window = SeeHotkey(self, self.file_dao.read_raw())

    def __apply_hotkey(self):
        """Make all the changes for the new hotkey"""
        self.custom_key_hotkey.setKey(QKeySequence(self.custom_key))

    def safemode(self):
        self.secondary_window = SafeMode(self, self.custom_key)
        self.hide()


class ChangeHotKey(QWidget):
    """Change the user's Hotkey"""

    def __init__(self, main: MainWindow):
        super().__init__()
        self.new_key = ""  # New hotkey that will be written in the model
        self.key_value = 0  # Value for the new key sequence
        self.key_string = ""  # Key string for the key_label
        self.key_label = None  # Label to show the hotkey
        self.dialog = None  # Dialog window of the window
        self.main = main  # Main window
        self.key_map = {}  # Key's values and names dictionary
        for keyname, value in vars(Qt).items():
            if isinstance(value, Qt.Key):
                self.key_map[value] = keyname.partition("_")[2]
        self.modifiers = {  # Modifier keys map dictionary
            Qt.Key_Control: Qt.CTRL,
            Qt.Key_Shift: Qt.SHIFT,
            Qt.Key_Alt: Qt.ALT,
        }
        self.key_vals = []  # Already pressed keys
        self.__init_ui()  # Key listener

    def __init_ui(self):
        """Initialize the UI of the window"""
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
                      self,
                      220,
                      175)
        press_enter = Label("Press enter when finished",
                            label_stylesheet,
                            light_font,
                            self,
                            240,
                            275)
        self.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))
        self.show()

    def __append_to_key_string(self, string: str) -> None:
        """Append the given string to the key string"""
        if self.key_string != "":
            self.key_string += f"+{string}"
        else:
            self.key_string += string

    def __append_to_new_key(self, string: str) -> None:
        """Append a new key value to self.new_key"""
        if self.new_key != "":
            self.new_key += f",{string}"
        else:
            self.new_key += string

    def keyPressEvent(self, key: QKeyEvent) -> None:
        """Read the pressed key of the user"""
        prohibited = [Qt.Key_Tab, Qt.Key_Insert, Qt.Key_Print, Qt.Key_Pause,
                      Qt.Key_SysReq, Qt.Key_Home, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_CapsLock,
                      Qt.Key_NumLock, Qt.Key_ScrollLock, Qt.Key_F4]
        key_val = key.key()
        if key_val not in prohibited:
            if key_val == Qt.Key_Backspace:
                if self.new_key != "":
                    # Delete the last pressed key
                    delete = self.new_key.split(",")[-1]
                    self.key_value -= int(delete)  # Decrease by the last pressed key amount
                    # Remove the last key pressed from the new_key and the key_string
                    self.new_key = ",".join(self.new_key.split(",")[:-1])
                    self.key_string = "+".join(self.key_string.split("+")[:-1])
                    # Update the label
                    self.key_label.clear()
                    self.key_label.setText(self.key_string)
                    self.key_label.show()
                    pass
            elif key_val == Qt.Key_Return and self.new_key == "":
                # Can't use an empty key as the hotkey
                self.dialog = Dialog("Error",
                                     "The hotkey can't be empty",
                                     "Close",
                                     None)
                self.dialog.show()
            elif key_val == Qt.Key_Return and self.new_key != "":
                # Check if the hotkey is not one of the default ones
                if self.key_value != CHECK_KEY and self.key_value != ABOUT_US_KEY and self.key_value != CHANGE_KEY:
                    # Set the new hotkey
                    # Write the hotkey to the model
                    file_dao = HD.HotkeyDAO(filepath)
                    print(self.new_key)
                    file_dao.write_file(self.new_key)
                    # Change the hotkey in the main window
                    self.main.set_custom_key(self.key_value)
                    self.close()
                    self.main.show()
                else:
                    self.dialog = Dialog("Error",
                                         "The hotkey can't be one of the default hotkeys",
                                         "Close",
                                         None)
                    self.dialog.show()
                    self.key_label.clear()
                    self.key_label.show()
                    self.new_key = str()
                    self.key_string = str()
                    self.key_value = 0
            elif key_val == Qt.Key_Escape:
                # Return to the main window
                self.main.show()
                self.close()
            else:
                # Append the pressed key to the hotkey
                if not key.isAutoRepeat() and str(key_val) not in self.new_key.split(","):
                    if self.modifiers.get(key_val) is not None:
                        if str(self.modifiers.get(key_val)) not in self.new_key:
                            self.__append_to_new_key(str(self.modifiers[key_val]))
                            print(self.new_key)
                            self.key_value += self.modifiers[key_val]
                            self.__append_to_key_string(self.key_map[key_val])
                    else:
                        self.__append_to_new_key(str(key_val))
                        self.key_value += key_val
                        self.__append_to_key_string(self.key_map[key_val])
                    font_style = {
                        "color": "#FFFFFF",
                    }
                    label_stylesheet = QtStyleSheet.to_string(font_style)
                    font = Font("Roboto-Regular", 14, True, 200)
                    self.key_label = Label(f"{self.key_string}",
                                           label_stylesheet,
                                           font,
                                           self,
                                           270,
                                           240)
                    self.key_label.show()
        else:
            self.dialog = Dialog("Error",
                                 "A prohibited key was pressed\nCheck the documentation on prohibited keys",
                                 "Close",
                                 None)
            self.dialog.show()


class SeeHotkey(QWidget):
    """Show hotkey window"""

    def __init__(self, main: MainWindow, hotkey_numbers: str) -> None:
        super().__init__()
        self.main = main
        self.hotkey_numbers = hotkey_numbers
        self.key_text = self.__unmap_key()
        self.__init_ui()

    def __unmap_key(self):
        global key_value_map
        key_text = str()
        key = str()
        for key_value in self.hotkey_numbers.split(","):
            if self.__check_if_modifier(int(key_value)):
                normal_value = self.__get_key_normal_value(modifiers, int(key_value))
                key = key_value_map[normal_value]
            else:
                key = key_value_map[int(key_value)]
            key_text += f"{key}+"
        key_text = key_text[:-1]    # Strip extra + sign at the end
        return key_text

    @staticmethod
    def __check_if_modifier(key_val: int) -> bool:
        global modifiers
        try:
            check = list(modifiers.keys())[list(modifiers.values()).index(key_val)]
            return check is not None
        except ValueError:
            return False        # Value wasn't found

    @staticmethod
    def __get_key_normal_value(dictionary, key_value: int) -> int:
        value = list(dictionary.keys())[list(dictionary.values()).index(key_value)]
        return value

    def __init_ui(self):
        """"Initialize the window's UI"""
        # Styles
        window_stylesheet = {
            "background-color": "#361d32",
        }
        font_style = {
            "color": "#f55951",
        }
        label_stylesheet = QtStyleSheet.to_string(font_style)
        font = Font("Roboto-Regular", 16, True, 200)
        key = Label(f"Current hotkey: {self.key_text}",
                    label_stylesheet,
                    font,
                    self,
                    220,
                    175)
        self.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))
        self.show()


class AboutUs(QWidget):
    """About us window"""
    def __init__(self, main: MainWindow):
        super().__init__()
        self.main = main
        self.set_window_size(700, 500)
        self.window_stylesheet = self.initialize_window_stylesheet({"background-color": "#361d32"})
        self.font_color = self.__initialize_font_color({"color": "#f55951"})
        self.font = Font("Roboto-Regular", 16, True, 200)
        self.__init_ui()

    def set_window_size(self, x, y):
        self.setFixedSize(x, y)

    def initialize_window_stylesheet(self, window_stylesheet: dict):
        return self.__initialize(window_stylesheet)

    def __initialize_font_color(self, color_stylesheet):
        return self.__initialize(color_stylesheet)

    @staticmethod
    def __initialize(stylesheet):
        return QtStyleSheet.to_string(stylesheet)

    def __init_ui(self):
        self.setStyleSheet(self.window_stylesheet)
        self.add_labels_to_window()
        self.show()

    def add_labels_to_window(self):
        about_us_label = Label("Safekeys is a private project made by Guillermo M. Morales",
                               self.font_color,
                               self.font,
                               self,
                               50,
                               200)
        github_label = Label('Github: <a  style="color:white" href="https://github.com/MoralesGuillermo">'
                             'https://github.com/MoralesGuillermo</a>',
                             self.font_color,
                             self.font,
                             self,
                             110,
                             250)
        self.__permit_open_external_links(github_label)

    @staticmethod
    def __permit_open_external_links(label: Label):
        label.setOpenExternalLinks(True)


class SafeMode(QWidget):
    """"Safemode active window"""

    def __init__(self, main: MainWindow, unlock_key):
        super().__init__()
        self.main = main
        self.setWindowTitle("Safekeys - Safemode")
        self.setFixedSize(700, 400)
        # Activate hotkey to deactivate safemode
        self.unlock = QShortcut(QKeySequence(unlock_key), self)
        self.unlock.activated.connect(self.unlock_computer)
        # Block keys
        keyboard.block_key("esc")
        keyboard.block_key("f4")
        keyboard.block_key("tab")
        self.secondary = QWidget()
        self.setMouseTracking(True)  # Enable mouse tracking
        self.__init_ui()
        # Move cursor to the widget window (Pyqt's mouse event listener)
        global_pos = self.mapToGlobal(QPoint(0, 0))
        self.coordinates = (global_pos.x() + 350, global_pos.y() + 200)
        mouse = MController()
        mouse.position = self.coordinates

    def __init_ui(self):
        """Initialize the UI of the window"""
        # Styles
        window_stylesheet = {
            "background-color": "#361d32",
        }
        font_style = {
            "color": "#f55951",
        }
        label_stylesheet = QtStyleSheet.to_string(font_style)
        font = Font("Roboto-Regular", 24, True, 200)
        light_font = Font("Roboto-Regular", 14, True, 150)
        # Labels
        title = Label("Safemode active",
                      label_stylesheet,
                      font,
                      self,
                      220,
                      175)
        # Set the stylesheet
        self.setStyleSheet(QtStyleSheet.to_string(window_stylesheet))
        self.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse movements. Return mouse to its position
        when moved
        """
        mouse = MController()
        mouse.position = self.coordinates

    def unlock_computer(self):
        """Deactivate safemode"""
        # Unblock keys
        keyboard.unblock_key("esc")
        keyboard.unblock_key("f4")
        keyboard.unblock_key("tab")
        self.hide()
        self.main.show()
        # Delete the instance
        del self
