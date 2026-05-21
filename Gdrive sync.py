import os
import time
import logging
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Setup Logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileStore("errors.txt"), # Logs errors to this file
        logging.StreamHandler()           # Still shows progress in terminal
    ]
)

def download_with_retry(drive_file, local_path, max_retries=3):
    """Downloads a file with a retry loop and backoff."""
    file_name = drive_file['title']
    clean_name = "".join([c for c in file_name if c not in '<>:"/\\|?*'])
    target_path = os.path.join(local_path, clean_name)

    if os.path.exists(target_path):
        return f"SKIPPED: {file_name}"

    attempt = 0
    wait_time = 2  # Start with 2 seconds wait

    while attempt < max_retries:
        try:
            drive_file.GetContentFile(target_path)
            return f"SUCCESS: {file_name}"
        except Exception as e:
            attempt += 1
            logging.warning(f"Attempt {attempt} failed for {file_name}. Error: {e}")
            if attempt < max_retries:
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                logging.error(f"PERMANENT FAILURE: {file_name} after {max_retries} attempts.")
                with open("errors.txt", "a") as f:
                    f.write(f"Failed to download {file_name} (ID: {drive_file['id']}) - Error: {e}\n")
                return f"ERROR: {file_name}"

def recursive_search(drive, folder_id, local_path, all_files):
    """Walks the drive and collects all file objects to be downloaded."""
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    query = f"'{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()

    for item in file_list:
        target_path = os.path.join(local_path, item['title'])
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            recursive_search(drive, item['id'], target_path, all_files)
        else:
            all_files.append((item, local_path))

def start_sync():
    # Authentication
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("my_login.txt")
    if gauth.credentials is None: gauth.LocalWebserverAuth()
    elif gauth.access_token_expired: gauth.Refresh()
    else: gauth.Authorize()
    gauth.SaveCredentialsFile("my_login.txt")
    drive = GoogleDrive(gauth)

    # User Input
    print("\n--- Failsafe GDrive Sync (v2.0) ---")
    folder_id = input("Enter Google Drive Folder ID: ").strip()
    raw_path = input(r"Enter Local Destination Path: ").strip()
    save_path = os.path.normpath(raw_path)

    # Step 1: Map out all files first
    print("Indexing files... (Recursive scan)")
    all_tasks = []
    recursive_search(drive, folder_id, save_path, all_tasks)
    print(f"Total files found to verify/download: {len(all_tasks)}")

    # Step 2: Threaded Download with Dynamic Throttle
    current_workers = 10
    completed_count = 0

    while all_tasks and current_workers > 0:
        print(f"\n[Starting batch with {current_workers} threads]")
        failed_tasks = []
        
        with ThreadPoolExecutor(max_workers=current_workers) as executor:
            future_to_file = {executor.submit(download_with_retry, f, p): f for f, p in all_tasks}
            
            for future in as_completed(future_to_file):
                result = future.result()
                if "SUCCESS" in result or "SKIPPED" in result:
                    completed_count += 1
                else:
                    # If we hit an error, we keep track to retry in a smaller batch
                    failed_tasks.append(future_to_file[future])
        
        if failed_tasks:
            print(f"\n[!] {len(failed_tasks)} tasks encountered errors. Reducing thread count...")
            current_workers = max(1, current_workers // 2) # Halve the workers
            all_tasks = failed_tasks # Re-run only the failed ones
            time.sleep(5) # Cooldown
        else:
            all_tasks = [] # Everything finished

    print(f"\n[FINISH] Process complete. Total successful/skipped: {completed_count}")
    print("Any critical errors have been logged to 'errors.txt'.")

if __name__ == "__main__":
    start_sync()