import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def setup():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(q= "mimeType = 'application/vnd.google-apps.folder' and name = 'dexp' and trashed = False", fields="files(id,name,trashed)").execute()
    items = results.get("files", [])

    print(items)

    if len(items) > 1:
      return print("More than one folder with the name 'dexp', please delete/rename them.")

    if len(items) == 0:
      file_metadata = {
          "name": "dexp",
          "mimeType": "application/vnd.google-apps.folder",
      }
    
      file = service.files().create(body=file_metadata, fields="id").execute()
      print(f'Folder ID: "{file.get("id")}".')
      with open("data.json", "w") as datafile:
        datafile.write(f'{{"id":"{file.get("id")}"}}')
      
    if len(items) == 1:
      with open("data.json", "r+") as datafile:
        data = json.load(datafile)
        if data["id"] != items[0]["id"]:
          data["id"] = items[0]["id"]
          json.dump(data)
    
    return print("Setup complete!")
        

  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  setup()