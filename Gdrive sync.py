import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def sync_folder(drive_folder_id, local_path):
    # 1. Authenticate
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Opens browser for login
    drive = GoogleDrive(gauth)

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # 2. List files in GDrive folder
    query = f"'{drive_folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    print(f"Found {len(file_list)} files in Google Drive. Starting sync...")

    for file in file_list:
        file_name = file['title']
        target_file_path = os.path.join(local_path, file_name)

        # 3. Check if file exists locally
        if os.path.exists(target_file_path):
            print(f"Skipping: {file_name} (Already exists)")
        else:
            print(f"Downloading: {file_name}...")
            try:
                file.GetContentFile(target_file_path)
            except Exception as e:
                print(f"Error downloading {file_name}: {e}")

if __name__ == "__main__":
    # Replace with your actual Folder ID (from the URL) and local path
    FOLDER_ID = '123_YOUR_FOLDER_ID_HERE_abc'
    LOCAL_DEST = './my_photos'
    
    sync_folder(FOLDER_ID, LOCAL_DEST)