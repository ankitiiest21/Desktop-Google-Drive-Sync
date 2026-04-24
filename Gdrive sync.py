import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def start_sync():
    # Setup Auth
    gauth = GoogleAuth()
    # This saves your login so you don't have to auth every single time
    gauth.LoadCredentialsFile("my_login.txt")
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("my_login.txt")

    drive = GoogleDrive(gauth)

    # CONFIG: Change these two!
    FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE' 
    SAVE_PATH = r'C:/Users/c007u/Downloads/Trips/Bali & Jakarta'

    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    # Get the list of photos from Drive
    print("Checking Google Drive... hang tight.")
    files = drive.ListFile({'q': f"'{FOLDER_ID}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false"}).GetList()
    for f in files:
    # SKIP if it's a folder to avoid the crash
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            print(f"[-] Skipping folder: {f['title']} (Logic only handles files)")
            continue
        
        target = os.path.join(SAVE_PATH, f['title'])
    
        if os.path.exists(target):
            print(f"[-] Skipping {f['title']} - already exists.")
        else:
            print(f"[+] Downloading {f['title']}...")
            f.GetContentFile(target)

    print("Success! All photos synced.")

if __name__ == "__main__":
    start_sync()