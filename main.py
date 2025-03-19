import os.path
import json
import click
from click import secho

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive.file"]

@click.group()
def cli():
    pass
  
  
  
def signup():
  creds = None
  
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    
    with open("token.json", "w") as token:
      token.write(creds.to_json())
    
  return creds

@cli.command("setup", help="Create dexp folder in destination location")
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def setup(folder):
  
  creds = signup()
  try:
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(q= "mimeType = 'application/vnd.google-apps.folder' and name = 'dexp' and trashed = False", fields="files(id,name,trashed)").execute()
    items = results.get("files", [])

    secho(items)

    if len(items) > 1:
      return secho("More than one folder with the name 'dexp', please delete/rename them.", fg="yellow")

    if len(items) == 0:
      file_metadata = {
          "name": "dexp",
          "mimeType": "application/vnd.google-apps.folder",
      }
    
      file = service.files().create(body=file_metadata, fields="id").execute()
      secho(f'Folder ID: "{file.get("id")}".')
      with open("data.json", "w") as datafile:
        datafile.write(f'{{"id":"{file.get("id")}"}}')
      
    if len(items) == 1:
      with open("data.json", "w+") as datafile:
        datafile.write(f'{{"id":"{items[0].get("id")}", "dir":"{os.path.abspath(folder).replace("\\", "/")}"}}')
        
    with open("data.json", "r") as datafile:
      data = json.load(datafile)
      
      if not os.path.exists(folder.replace("\\", "/") + "/dexp"):
        os.mkdir(os.path.abspath(folder).replace("\\", "/") + "/dexp")
        secho(f"dexp folder created in {data["dir"]}!", fg="green")
      else:
        return secho("dexp folder already exists in the destination folder!", fg="red")
        
    return secho("Setup complete!", fg="green")

  except HttpError as error:
    secho(f"An error occurred: {error}")

@cli.command("save", help="Save the dexp folder to Drive")
def save():
  creds = signup()
  with open("data.json", "r") as datafile:
    data = json.load(datafile)
    path = data["dir"]
    folderid = data["id"]
    
  if not os.path.exists("data.json"):
    return secho("Please run <dexp setup> to set up the folder first", fg="red")
  
  try:
    print("saving...")
  
  except HttpError as error:
    secho(f"An error occurred: {error}")

if __name__ == "__main__":
  cli()