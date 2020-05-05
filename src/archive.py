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

class emailMessage:

    def __init__(self, email_id, email_from, email_body):
        self.email_from = email_from
        self.email_body = email_body
        self.email_id = email_id

    def decodeEmailBody(self):
        # TODO: Fix the encodig part... Email_body has too many characters to decode
        base64_message = self.email_body
        # base64_bytes = base64_message.encode('utf-8')
        message_bytes = base64.b64decode(base64_message)
        message = message_bytes.decode('utf-8')
        return message


SCOPES=['https://www.googleapis.com/auth/gmail.readonly']

def getMessagesList(creds):

    service = build('gmail', 'v1', credentials=creds)
    response = service.users().messages().list(userId='me').execute()
    
    messages = response['messages']
    message_ids = []
    for message in messages:
        message_ids.append(message['id'])
    return message_ids

def getMessages(msg_ids, creds):
    messages = []
    for msg_id in msg_ids:
        service = build('gmail', 'v1', credentials=creds)
        response = service.users().messages().get(userId='me', id=msg_id).execute()
        for val in response['payload']['headers']:
            if val['name'] == 'From':
                email_from = val['value']
            else:
                pass
        email_id = response['id']  
        try:
            email_body = response['payload']['parts'][0]['body']['data']
        except:
            email_body = None
        if 'Indeed' in email_from:
            email = emailMessage(email_id, email_from, email_body)
            messages.append(email)
    return messages

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
    email_messages = getMessages(msg_ids, creds)
    print(email_messages[0].decodeEmailBody())

if __name__ == '__main__':
    main()

# TODO: Need to fix decoder method.
# TODO: create a function that will check the email body contents and extract the https:// link so we can scrape the data from that page.
# TODO: create a function that will scrape the webpage and search for keywords such as Python, data analysis, statistcs, ... and return those specific job 
# postings
# TODO: Create a function to send a text message alert to my phone notifying me of the specific jobs to apply to.

