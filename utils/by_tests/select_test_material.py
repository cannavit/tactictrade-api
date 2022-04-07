import os
import random
import string
# Select one random file from inside of the folder avatars


def avatar_random_file():

    # Select one random file from inside of the folder avatars
    folder = os.path.join(os.path.dirname(__file__), 'avatars')
    files = os.listdir(folder)
    random_file = random.choice(files)

    return os.path.join(folder, random_file)


# Select one ramdon image from insode of trading_images
def trading_random_image():
    
    # Select one random file from inside of the folder avatars
    folder = os.path.join(os.path.dirname(__file__), 'tests_material/trading_images')
    files = os.listdir(folder)

    # delete '.DS_Store' from the list
    files.remove('.DS_Store')

    random_file = random.choice(files)

    # Get the file name with out the extension
    file_name = os.path.splitext(random_file)[0]

    # Get the file name with extension
    file_with_extension = os.path.splitext(random_file)[1]

    
    
    return   {
        "path": os.path.join(folder, random_file),
        "name": file_name,
        "extension": file_with_extension,
        "folder": folder,
        "file": file_name+file_with_extension,
    }