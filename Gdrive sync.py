import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def recursive_sync(drive, folder_id, local_path):
    # 1. Create the local folder if it doesn't exist
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        print(f"Created folder: {local_path}")

    # 2. List everything in this specific Drive folder
    query = f"'{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    for file in file_list:
        file_name = file['title']
        # Sanitize filename (remove characters Windows doesn't like)
        clean_name = "".join([c for c in file_name if c not in '<>:"/\\|?*'])
        target_path = os.path.join(local_path, clean_name)

        # 3. If it's a FOLDER, go deeper (Recursion)
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            print(f"--- Entering Folder: {file_name} ---")
            recursive_sync(drive, file['id'], target_path)
        
        # 4. If it's a FILE, download it
        else:
            if os.path.exists(target_path):
                print(f"[-] Skipping: {file_name}")
            else:
                print(f"[+] Downloading: {file_name}")
                file.GetContentFile(target_path)

def start_sync():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("my_login.txt")
    if gauth.credentials is None: gauth.LocalWebserverAuth()
    elif gauth.access_token_expired: gauth.Refresh()
    else: gauth.Authorize()
    gauth.SaveCredentialsFile("my_login.txt")
    
    drive = GoogleDrive(gauth)

    # UPDATED FOLDER ID AND PATH
    FOLDER_ID = '1D0yr5gxKYTBbrMSYON9QsxuvzLvzOifY'
    SAVE_PATH = r'C:\Users\z004nvnc\Downloads\Wedding\Ankit & Muskan\Candid\Pankatti,Baraat,Shaadi'

    print("Starting Deep Sync... This may take a while.")
    recursive_sync(drive, FOLDER_ID, SAVE_PATH)
    print("\nDONE! Your wedding photos are fully synced.")

if __name__ == "__main__":
    start_sync()