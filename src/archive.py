import os
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import re
from bs4 import BeautifulSoup
import requests

class emailMessage:

    def __init__(self, email_id, email_from, email_body):
        self.email_from = email_from
        self.email_body = email_body
        self.email_id = email_id

    def decodeEmailBody(self):
        # TODO: Fix the encoding part... Email_body has too many characters to decode
        base64_message = self.email_body
        print(f'Base64 Message \n{base64_message}')
        print('Length: ' + str(len(base64_message)))
        # base64_bytes = base64_message.encode('ascii')
        # print(f'Base64_bytes \n{base64_bytes}')
        base64_message += '==='
        message_bytes = base64.b64decode(base64_message)
        # print(f'Message_bytes \n{message_bytes}')
        # message = message_bytes.decodebytes('ascii')
        # print(f'decoded Message \n{message_bytes}')
        # print(message_bytes)
        message = message_bytes.decode('utf-8') 
        return message

    def getWebsiteUrl(self):
        message = self.decodeEmailBody()
        url = re.findall("(?P<url>https://[^\s]+)", message)
        return url[1]

    def getUrlText(self):
        url = self.getWebsiteUrl()
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        url_text = soup.get_text()
        return url_text

    def getTitle(self):
        url = self.getWebsiteUrl()
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        self.title = soup.find('title')
        return self.title

    def parseText(self):
        text = self.getUrlText()
        title = self.getTitle()
        keywords = ['python', 'Python', 'Mathematics', 'Bachelor', 'entry level', 'entry-level', 'beginner']
        found_keywords = []
        for keyword in keywords:
            if keyword in text:
                found_keywords.append(keyword)
        email_dict = {"Title": title, "keywords":found_keywords}
        if email_dict['keywords']:
            return email_dict
        else:
            return None

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
        print(response)
        for val in response['payload']['headers']:
            if val['name'] == 'From':
                email_from = val['value']
            else:
                pass
        email_id = response['id']  
        try:
            email_body = response['payload']['parts'][0]['body']['data']
            # print(email_body)
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
    # print(email_messages[0].decodeEmailBody())
    # email_messages[0].getWebsiteUrl())
    # email_messages[0].getUrlText()
    # for mess in email_messages:
        # print(mess.parseText())
    # email_messages[4].parseText()

if __name__ == '__main__':
    main()

# TODO: Need to fix decoder method.
# Done: create a function that will check the email body contents and extract the https:// link so we can scrape the data from that page.
# Done: create a function that will scrape the webpage and search for keywords such as Python, data analysis, statistcs, ... and return those specific job 
# postings
# TODO: Create a function to send a text message alert to my phone notifying me of the specific jobs to apply to.

