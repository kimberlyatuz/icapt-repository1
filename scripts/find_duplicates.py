import os
from collections import defaultdict

def find_duplicates(directory):
    files = defaultdict(list)

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            filesize = os.path.getsize(filepath)
            files[(filename, filesize)].append(filepath)

    duplicates = {key: value for key, value in files.items() if len(value) > 1}
    return duplicates

def delete_duplicates(duplicates):
    for (filename, filesize), paths in duplicates.items():
        # Keep the first occurrence and delete the rest
        for path in paths[1:]:  # Skip the first file
            try:
                os.remove(path)
                print(f"Deleted: {path}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")

if __name__ == "__main__":
    # Adjust this path to your actual static files directory
    directory_to_search = r'C:\Users\LENOVO\Desktop\DJANGO2PROJECT\ICAPT\static'  # Use raw string for Windows paths
    duplicates = find_duplicates(directory_to_search)

    if duplicates:
        for (filename, filesize), paths in duplicates.items():
            print(f"Duplicate file: {filename} ({filesize} bytes)")
            for path in paths:
                print(f"    {path}")

        # Ask for confirmation before deletion
        confirm = input("Do you want to delete these duplicate files? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            delete_duplicates(duplicates)
        else:
            print("Deletion aborted.")
    else:
        print("No duplicate files found.")