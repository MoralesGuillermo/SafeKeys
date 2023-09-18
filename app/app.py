"""App class for the logic of the app"""
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QLineEdit, QLabel, QDialog, QShortcut
from PyQt5.QtGui import QFont, QFontDatabase, QKeyEvent, QKeySequence
from PyQt5.QtCore import Qt

import HotkeyDAO as HD


# Color palette: https://colors.muz.li/palette/361d32/543c52/f55951/edd2cb/f1e8e6
filepath = os.path.join(os.getcwd(), "elem", "hk.csv")

# Default Key Sequence
change_key = Qt.CTRL+Qt.ALT+Qt.Key_C
about_us = Qt.CTRL + Qt.ALT + Qt.Key_U
check_key = Qt.CTRL + Qt.ALT + Qt.Key_B


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
        global change_key, about_us, check_key
        super().__init__()
        self.secondary_window = None
        file_dao = HD.HotkeyDAO(filepath)
        file_dao.read_file()
        self.custom_key = file_dao.key
        self.hidden = False
        self.hotkey_label = None
        if self.custom_key is None:
            self.hidden = True
            self.custom_key = str()
            self.custom_key_window()

        # Activate shortcuts
        self.change_key_hotkey = QShortcut(QKeySequence(change_key), self)
        self.change_key_hotkey.activated.connect(self.custom_key_window)

        self.about_us_hotkey = QShortcut(QKeySequence(about_us), self)
        self.about_us_hotkey.activated.connect(self.about_us_window)

        self.check_key_hotkey = QShortcut(QKeySequence(check_key), self)
        self.check_key_hotkey.activated.connect(self.check_key_window)

        self.custom_key_hotkey = QShortcut(QKeySequence(self.custom_key), self)
        self.custom_key_hotkey.activated.connect(self.safemode)
        # Initialize the UI
        self.__init_ui()
        if self.hidden:
            self.hide()
            self.hidden = False

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

    def custom_key_window(self):
        """Go to the custom key window"""
        self.secondary_window = ChangeHotKey(self)

    def get_custom_key(self):
        """Return the current hotkey"""
        return self.custom_key

    def set_custom_key(self, value):
        """ Set the custom key"""
        self.custom_key = value
        self.__apply_hotkey()

    def about_us_window(self):
        self.secondary_window = AboutUs(self)

    def check_key_window(self):
        self.secondary_window = SeeHotkey(self)

    def __apply_hotkey(self):
        """Make all the changes for the new hotkey"""
        self.custom_key_hotkey.setKey(QKeySequence(self.custom_key))

    def safemode(self):
        self.secondary_window = SafeMode(self)
        self.hide()


class ChangeHotKey(QWidget):
    """Change the user's Hotkey"""
    def __init__(self, main: MainWindow):
        super().__init__()
        self.new_key = ""           # New hotkey that will be written in the model
        self.key_value = 0          # Value for the new key sequence
        self.key_string = ""        # Key string for the key_label
        self.key_label = None       # Label to show the hotkey
        self.dialog = None          # Dialog window of the window
        self.main = main            # Main window
        self.key_map = {}           # Key's values and names dictionary
        for keyname, value in vars(Qt).items():
            if isinstance(value, Qt.Key):
                self.key_map[value] = keyname.partition("_")[2]
        self.modifiers = {  # Modifier keys map dictionary
            Qt.Key_Control: Qt.CTRL,
            Qt.Key_Shift: Qt.SHIFT,
            Qt.Key_Alt: Qt.ALT,
        }
        self.key_vals = []       # Already pressed keys
        self.__init_ui()        # Key listener

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
                    self.key_value -= int(delete)   # Decrease by the last pressed key amount
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
                if self.key_value != check_key and self.key_value != about_us and self.key_value != change_key:
                    # Set the new hotkey
                    # Write the hotkey to the model
                    file_dao = HD.HotkeyDAO(filepath)
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
                    pass   # TODO: DELETE THE KEY AND DELETE THE KEY LABEL

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
    def __init__(self, main: MainWindow):
        super().__init__()
        self.main = main
        self.__init_ui()

    def __init_ui(self):
        """"Initialize the window's UI"""
        pass  # TODO: Make UI
        self.show()


class AboutUs(QWidget):
    """About us window"""
    def __init__(self, main: MainWindow):
        super().__init__()
        self.main = main
        self.__init_ui()

    def __init_ui(self):
        """Initialize the window's UI"""
        pass    # TODO: MAKE UI
        self.show()


class SafeMode(QWidget):
    """"Safemode active window"""
    def __init__(self,  main: MainWindow):
        super().__init__()
        self.main = main
        self.__init_ui()

    def __init_ui(self):
        """Initialize the UI of the window"""
        pass  # TODO: MAKE UI
        self.show()
