import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from concurrent.futures import ThreadPoolExecutor

def download_file(drive_file, local_path):
    """Worker function to download a single file."""
    file_name = drive_file['title']
    # Sanitize filename for Windows
    clean_name = "".join([c for c in file_name if c not in '<>:"/\\|?*'])
    target_path = os.path.join(local_path, clean_name)

    if os.path.exists(target_path):
        print(f"[-] Skipping: {file_name}")
        return
    
    try:
        print(f"[+] Downloading: {file_name}...")
        drive_file.GetContentFile(target_path)
    except Exception as e:
        print(f"[!] Error downloading {file_name}: {e}")

def recursive_sync(drive, folder_id, local_path, executor):
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    query = f"'{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    files_to_download = []

    for file in file_list:
        target_path = os.path.join(local_path, file['title'])
        
        # If it's a folder, recurse immediately (don't thread the folder walking)
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            recursive_sync(drive, file['id'], target_path, executor)
        else:
            # If it's a file, add it to our "to-do" list for threads
            files_to_download.append(file)

    # Hand off the file downloads to the thread pool
    for f in files_to_download:
        executor.submit(download_file, f, local_path)

def start_sync():
    # 1. Auth Setup
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("my_login.txt")
    if gauth.credentials is None: gauth.LocalWebserverAuth()
    elif gauth.access_token_expired: gauth.Refresh()
    else: gauth.Authorize()
    gauth.SaveCredentialsFile("my_login.txt")
    
    drive = GoogleDrive(gauth)

    # 2. User Input
    print("\n--- GDrive Wedding Photo Sync Utility ---")
    folder_id = input("Enter Google Drive Folder ID: ").strip()
    raw_path = input(r"Enter Local Destination Path (e.g. C:\Photos): ").strip()
    
    # Handle the raw path automatically
    save_path = os.path.normpath(raw_path)

    # 3. Execution with 10 concurrent threads
    print(f"\nStarting sync in: {save_path}")
    with ThreadPoolExecutor(max_workers=10) as executor:
        recursive_sync(drive, folder_id, save_path, executor)
    
    print("\n[COMPLETE] All threads finished. Check your folder!")

if __name__ == "__main__":
    start_sync()