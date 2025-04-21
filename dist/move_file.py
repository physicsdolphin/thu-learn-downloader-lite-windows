import os
import shutil
from pathlib import Path

def auto_rename(target_path):
    """
    Simulates Windows-style auto-renaming: filename (1).ext, filename (2).ext, etc.
    """
    base = target_path.stem
    ext = target_path.suffix
    folder = target_path.parent

    i = 1
    while True:
        new_name = f"{base} ({i}){ext}"
        new_path = folder / new_name
        if not new_path.exists():
            return new_path
        i += 1

def copy_files_with_rules(source_folder, target_folder):
    """
    Recursively copies files from the source folder to the target semester folder with the given rules.
    If the file already exists and contains 'commit' or 'comment', it will be renamed.
    """
    source = Path(source_folder)
    target = Path(target_folder)

    # Traverse the usernames and semesters
    for username_folder in os.listdir(source):
        username_path = source / username_folder
        if os.path.isdir(username_path):  # Ensure it's a folder
            for semester_folder in os.listdir(username_path):
                semester_path = username_path / semester_folder
                if os.path.isdir(semester_path):  # Ensure it's a semester folder
                    # Define the corresponding target semester folder
                    target_semester_folder = target / semester_folder
                    target_semester_folder.mkdir(parents=True, exist_ok=True)  # Ensure target exists

                    # Recursively copy files from the semester folder, maintaining the subdirectory structure
                    for root, dirs, files in os.walk(semester_path):
                        for file_name in files:
                            file_path = Path(root) / file_name
                            # Generate the target path by preserving the directory structure
                            relative_path = file_path.relative_to(semester_path)  # Path relative to the semester folder
                            target_file_path = target_semester_folder / relative_path

                            # Ensure the target subdirectories exist
                            target_file_path.parent.mkdir(parents=True, exist_ok=True)

                            filename_lower = file_name.lower()

                            if target_file_path.exists():
                                # If the file exists and contains "submit" or "comment", auto-rename it
                                if "submit" in filename_lower or "comment" in filename_lower:
                                    new_destination = auto_rename(target_file_path)
                                    shutil.copy2(file_path, new_destination)
                                    print(f"Copied with rename: {file_name} -> {new_destination.name}")
                                else:
                                    print(f"Skipped (exists): {file_name}")
                            else:
                                shutil.copy2(file_path, target_file_path)
                                print(f"Copied: {file_name}")

# Example usage:
source_folder = r".\downloads"  # Your source folder
target_folder = r"G:\Involution Corridor\网络学堂资料"  # Target folder
copy_files_with_rules(source_folder, target_folder)
