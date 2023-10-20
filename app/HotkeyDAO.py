""""DAO object to retrieve data from hk.py"""
import filemanager as fm


class HotkeyDAO:
    def __init__(self, filepath):
        self._filepath = filepath
        self._raw_file = str
        self._key = None

    @property
    def filepath(self) -> str:
        """self.filepath attr getter"""
        return self._filepath

    @filepath.setter
    def filepath(self, path) -> None:
        """Set self.filepath"""
        self._filepath = path

    @property
    def key(self) -> int:
        """self.filepath attr getter"""
        return self._key

    @key.setter
    def key(self, key) -> None:
        """Set self.filepath"""
        self._key = key

    def read_file(self) -> None:
        """Read the given hotkey file. """
        self._raw_file = fm.FileManager.read_content(self.filepath)
        if self._raw_file is None:
            print(f"GIVEN FILE {self.filepath} has not been found: DAO")
        else:
            self.key = sum(map(lambda x: int(x), self._raw_file.split(",")))

    def read_raw(self):
        """Return the values of the hotkey"""
        self._raw_file = fm.FileManager.read_content(self.filepath)
        return self._raw_file

    def write_file(self, content) -> None:
        """Write the hotkey file"""
        fm.FileManager.write_file(self.filepath, content)
