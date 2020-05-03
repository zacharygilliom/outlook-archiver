import os
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64

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

def getMessagesList(creds):

    service = build('gmail', 'v1', credentials=creds)
    response = service.users().messages().list(userId='me').execute()
    
    messages = response['messages']
    message_ids = []
    for message in messages:
        message_ids.append(message['id'])
    print(message_ids) 
    return message_ids

def getMessages(msg_ids, creds):
    msg_snippets = {}
    for msg_id in msg_ids:
        service = build('gmail', 'v1', credentials=creds)
        response = service.users().messages().get(userId='me', id=msg_id).execute()
        # response = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['id', 'From', 'snippet', 'body']).execute()
        # msg_snippets[response['id']] = [response['payload']['headers'][0]['value'], response['payload']['headers'][1]['value']]
        # print(response['payload']['body']['data'], '\n')
        try: 
            print(response['payload']['body']['data'], '\n')
        except:
            print('No body data found')
    return msg_snippets 

def getAuthorization(scope):

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scope)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def main():
    creds = getAuthorization(scope=SCOPES)
    msg_ids = getMessagesList(creds)
    getMessages(msg_ids, creds)

if __name__ == '__main__':
    main()
# TODO: Added functino to parse the base 64 encoded body email.
# TODO: Added function to check for the sender of the email to check for indeed.com so we can parse through the body of the email and find the job listings.

