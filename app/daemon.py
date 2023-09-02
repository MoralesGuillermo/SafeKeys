"""Daemon class for listener management"""
from pynput import keyboard as kb
from pynput import mouse as ms


class Daemon:
    """Daemon management class"""
    def __init__(self, hotkey_map: dict, on_move_func):
        # Listeners
        self.kb_daemon = kb.GlobalHotKeys(hotkey_map)
        self.ms_daemon = ms.Listener(on_move=on_move_func)
        # On_move function to control the mouse
        self.on_move = on_move_func

    def start(self):
        """Start the listeners"""
        self.ms_daemon.start()
        self.kb_daemon.start()

    def stop(self):
        """"Stop the listeners"""
        self.ms_daemon.stop()
        self.kb_daemon.stop()
