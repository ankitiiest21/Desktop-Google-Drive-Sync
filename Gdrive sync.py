import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def main():
    # 1. Authentication
    gauth = GoogleAuth()
    # This will create a local file 'mycreds.txt' to store your login
    # so you don't have to authenticate in the browser every time.
    gauth.LoadCredentialsFile("mycreds.txt")
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    # 2. Configuration
    FOLDER_ID = 'YOUR_FOLDER_ID_HERE' # Get this from the Drive URL
    LOCAL_DIR = './downloaded_photos'
    
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    # 3. Fetch File List
    query = f"'{FOLDER_ID}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    print(f"Found {len(file_list)} files. Starting check...")

    # 4. Sync Logic
    for file in file_list:
        file_name = file['title']
        path = os.path.join(LOCAL_DIR, file_name)

        if os.path.exists(path):
            # Optional: Check file size if you want to ensure the previous 
            # interrupted download wasn't a partial file.
            if os.path.getsize(path) == int(file['fileSize']):
                print(f"[-] Skipping {file_name} (Exists)")
                continue

        print(f"[+] Downloading {file_name}...")
        file.GetContentFile(path)

if __name__ == "__main__":
    main()