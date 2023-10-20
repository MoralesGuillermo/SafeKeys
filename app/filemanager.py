"""Reader object to read files"""
import os


class FileManager:
    @staticmethod
    def read_content(path: str):
        """Read the content of a file"""
        try:
            with open(path, "r") as file:
                content = file.read()
                file.close()
            return content
        except FileNotFoundError:
            print(f"GIVEN FILE {path} WAS NOT FOUND")
            return None

    @staticmethod
    def write_file(path: str, content: str) -> bool:
        """"Write a file with the given content"""
        # Make the missing directories
        try:
            with open(path, "w") as file:
                file.write(content)
                file.close()
            return True
        except FileExistsError and FileNotFoundError:
            print("FILE COULDN'T BE WRITTEN")
            return False

    @staticmethod
    def change_mode(path: str, mode: int):
        """Modify a file's permissions"""
        try:
            os.chmod(path, mode)
            return True
        except FileNotFoundError:
            raise Exception(f"Given file {path} couldn't be modified. FileNotFound")
