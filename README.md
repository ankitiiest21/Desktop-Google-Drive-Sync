Industrial-Grade Google Drive Sync Utility
A robust, multithreaded Python utility designed to recursively sync large Google Drive folders to a local machine. It safely bypasses the Google Drive web interface file size/count limitations by streaming files directly via the Google Drive API.

Features
Multithreaded Downloader: Downloads up to 10 files simultaneously with adaptive thread throttling.

Failsafe Backoff: Automatically handles rate limits (403 Forbidden) by lowering worker counts and utilizing exponential backoff.

MD5 Checksum Verification (to be added): Ensures 100% data integrity by checking files against Google Drive's MD5 hashes to skip matches or overwrite corrupted/partial downloads.

Persistent Authentication: Caches tokens locally to bypass browser re-authentication on subsequent runs.

Dynamic Local Input: Accepts custom folder IDs and local destination paths at runtime.

Technical Prerequisites
Ensure your local environment has Python installed:

Python 3.8 or higher

pip (Python package manager)

Phase 1: Google Cloud Console & API Setup
To connect the script to Google Drive, you must register a desktop application on the Google Cloud Platform (GCP) to generate a client secrets configuration.

1. Create a Google Cloud Project
Open the Google Cloud Console.

Sign in with your personal Gmail account.

Click the project dropdown menu in the top-left corner (next to the "Google Cloud" logo) and select New Project.

Name the project (e.g., Drive-Sync-Utility) and click Create. Ensure this new project is selected in the top-left dropdown before moving to the next step.

2. Enable the Google Drive API
Use the top search bar to search for Google Drive API.

Click on the API from the results list and click the blue Enable button.

3. Configure the OAuth Consent Screen
Because you are using a personal Gmail account (not a Google Workspace account), your app must be configured as an External testing application:

Navigate to APIs & Services > OAuth consent screen via the left-hand sidebar.

Select External as the User Type and click Create.

App Information: Fill in the mandatory fields:

App name: PhotoGrabber

User support email: Select your Gmail address from the dropdown.

Developer contact information: Enter your Gmail address.

Click Save and Continue.

Scopes: Do not modify anything here. Scroll to the bottom and click Save and Continue.

Test Users: Because your app configuration is unverified, Google blocks all logins unless the accounts are explicitly added to the guest list:

Click + Add Users.

Enter your exact Gmail address.

Click Add, then click Save and Continue.

Review the summary dashboard and click Back to Dashboard.

4. Generate Desktop App Client Credentials
On the left-hand sidebar, click on Clients (or Credentials depending on your console configuration view).

Click + Create Client (or Create Credentials > OAuth client ID) at the top of the window.

Set the Application type dropdown to Desktop App.

Name the client configuration (e.g., Sync-Script-Desktop) and click Create.

A confirmation dialog will pop up. Click Download JSON to save the credential configuration file.

Locate the downloaded file on your computer, rename it to exactly client_secrets.json, and move it to your project folder where your Python script lives.

Phase 2: Local Project Setup
Clone or structure your directory: Ensure your project folder contains your script (e.g., sync.py) and the credentials file in the same root level:

Plaintext
drive-sync-project/
├── client_secrets.json
└── sync.py
Initialize a Virtual Environment (Recommended):

Bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
Install Dependencies:
Install the required PyDrive2 client wrapper package:

Bash
pip install PyDrive2
Phase 3: Script Execution Guide
Run the utility from your terminal or command prompt:

Bash
python sync.py
Initial Authentication (First Run Only):

A browser tab will automatically open asking you to sign in with your Google Account.

Choose the exact Gmail account you added under the Test Users section in Phase 1.

A warning screen saying "Google hasn't verified this app" will appear. This is normal for development applications. Click Advanced, then click Go to PhotoGrabber (unsafe), and grant permissions.

Once completed, you can close the browser tab. The script will save an authentication state token file named my_login.txt inside your folder so you do not have to perform this login loop again.

Provide Runtime Variables:

Enter Google Drive Folder ID: Paste the target folder ID string found at the end of your Google Drive folder URL.

Example: If the link is https://drive.google.com/drive/folders/1D0yr5gxKYTBbrMSYON9QsxuvzLvzOifY, paste 1D0yr5gxKYTBbrMSYON9QsxuvzLvzOifY.

Enter Local Destination Path: Input the absolute path where files should save.

Example: C:\Users\YourName\Downloads\Wedding\Candid

Troubleshooting & Failures
Interrupted Downloads / Corrupted Files
If the terminal execution closes unexpectedly due to network drops, simply run python sync.py again with the same parameters. The script validates the MD5 checksum layout; it will identify partial file arrays, bypass completely matching images, and resume downloading the missing target files cleanly.

Logging System (errors.txt)
If specific file requests consistently break or time out despite the automatic rate-limiting dynamic worker reductions, they are recorded to an auto-generated file named errors.txt located in the root script folder. You can reference this file to check for explicit API permission drops or file structural errors.
