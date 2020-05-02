import os
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class emailDestinationDirectory:

    def __init__(self, emailDirectory):
        self.emailDirectory = emailDirectory

    def ldir(self):
        return os.listdir(self.emailDirectory)

    def checkDirectory(self, emailDate):
        if self.ldir():
            for folder in self.ldir():
                if folder == emailDate['month']:
                    return False
                elif folder != emailDate['month']:
                    return True
                    os.mkdir(os.path.join(self.emailDirectory, emailDate))
        elif not self.ldir():
            return True 

    def createDirectory(self, emailDate):
        if self.checkDirectory(emailDate):
            os.mkdir(os.path.join(self.emailDirectory, emailDate['month']))
            # TODO: For some reason this errors out now that the April directory is already created, 
            return f"The {emailDate['month']} was created Successfully"
        else:
            print(f"The {emailDate['month']} Directory already exists!")
            return False

SCOPES=['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials = creds)

    results = service.users().messages().get(userId='me',id='171c8162074b5cc8').execute()
    # messages = results.get('messages', [])

    if not results:
        print('No messages found')
    else:
        print('messages')
        print(results['snippet'])
if __name__ == '__main__':
    main()


