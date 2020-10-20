import os
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import HttpError
import base64
import re
from bs4 import BeautifulSoup
import requests
from twilio.rest import Client
from email.mime.text import MIMEText

# A quick overview of how the code works.  
# We connect to our Gmail API and fetch all the email IDS.  We need the email IDS because we need to then pass this to the GMAIL API so we can read the emails.  Once we can read the 
# emails, we will parse the text to find the emails from Indeed.com because these will have the job postings that we want to look at.  The job postings include the URL from which the 
# job desciption resides. From here, we use Beatiful soup to parse the website and look in the job description to find keywords that we want.
#Done - Need to fix the email decoder as the base64 message is always off by a digit.
#TODO - Once we find the job postings we want to look at, we need to send a text to me of the job.

class emailMessage:

    ''' A class for the email messages to obtain specific pieces of the emails'''

    def __init__(self, email_id, email_from, email_body):
        self.email_from = email_from
        self.email_body = email_body
        self.email_id = email_id

    # Problem with the decode.  Need to fix this.
    # This will read the email body which arrives in base64 and will decode it to something we can read so we can parse it.
    def decodeEmailBody(self):
        base64_message = self.email_body
        message_str = base64.urlsafe_b64decode(base64_message.encode())
        message = message_str.decode('utf-8') 
        return message

    # Parse the body of the email and grab the URL from the job description.  We will use the job URL and beautifulsoup to parse the webpage.
    def getWebsiteUrl(self):
        message = self.decodeEmailBody()
        # url1 = re.findall("https://www.indeed.com/.*?\/clk/\s.*?", message)
        url = re.findall("(?P<url>https://www.indeed.com/.*?\/clk/[^\s]+)", message)
        return url

   # Pass the url to BS4 and read the text from the website. 
    def getUrlText(self):
        urlList = self.getWebsiteUrl()
        for url in urlList:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            url_text = soup.get_text()
        return url_text

    # Get job title from website
    def getTitle(self):
        urlList = self.getWebsiteUrl()
        for url in urlList:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            url_text = soup.get_text()
        return self.title

    # Parse the website of the job posting to find the specific keywords we want to find in the description.
    def parseText(self):
        text = self.getUrlText()
        title = self.getTitle()
        keywords = ['python', 'Python', 'Mathematics', 'Bachelor', 'entry level', 'entry-level', 'beginner']
        found_keywords = []
        for keyword in keywords:
            if keyword in text.lower():
                found_keywords.append(keyword)
        email_dict = {"Title": title, "keywords":found_keywords}
        if email_dict['keywords']:
            return email_dict
        else:
            return None

# See gmail API for the scopes explanation.  We want Read and Write Access Only
SCOPES=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# Connect to our gmail API and pull out all the message ids.
def getMessagesList(creds):
    service = build('gmail', 'v1', credentials=creds)
    response = service.users().messages().list(userId='me').execute()
    
    messages = response['messages']
    message_ids = []
    for message in messages:
        message_ids.append(message['id'])
    return message_ids

# parse through all email ids in my gmail inbox, and pull it out into messages list if it is from Indeed.
def getMessages(msg_ids, creds):
    messages = []
    for msg_id in msg_ids:
        service = build('gmail', 'v1', credentials=creds)
        response = service.users().messages().get(userId='me', id=msg_id).execute()
        # print(response)
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

def createMessage(message_text):
    message = MIMEText(message_text)
    message['to'] = 'zacharygilliom@gmail.com' 
    message['from'] = 'me'
    message['subject'] = 'Viable Job Listings' 
    print(message)
    return {'raw':base64.urlsafe_b64encode(message.as_string())}

def sendMessage(message, creds):
    service = build('gmail', 'v1', credentials=creds)
    try:
        messageSent = service.users().messages().send(userId='me', body=message).execute()
        print(f'Message Id: {message["id"]}')
        return messageSent
    except HttpError:
        print(f'An Error Occurred: {error}')

# See gmail API.  This is standard way of using the pickle credentials.
def getAuthorization(scope):

    creds = None

    if os.path.exists('../token.pickle'):
        with open('../token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    '../credentials.json', scope)
            creds = flow.run_local_server(port=0)

        with open('../token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def listJob(listOfUrls):
    JobPostingsList = []
    for urllist in listOfUrls:
        for url in urllist:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            title = str(title)
            titleLength = len(title)-20
            titleClean = title[7:titleLength]
            url_text = soup.get_text()
            keywords = parseText(url_text)
            JobPostings = {"Title":titleClean, "Keywords":keywords, 'URL':url}
            if JobPostings["Keywords"]:
                JobPostingsList.append(JobPostings)
    return JobPostingsList

def parseText(text):
    keywords = ['python', 'Python', 'Mathematics', 'Bachelor', 'entry level', 'entry-level', 'beginner', 'Go', 'golang', 'Golang']
    found_keywords = []
    for keyword in keywords:
        if keyword in text.lower():
            found_keywords.append(keyword)
    email_dict = found_keywords
    if email_dict:
        return email_dict
    else:
        return None

def buildBody(jobPostingsList):
    emailMessage = ""
    for job in jobPostingsList:
        emailMessage += "\n" + job["Title"] + ":"
        for keyword in job["Keywords"]:
            emailMessage += "--" + keyword  
        emailMessage += "\n" + job['URL']
    print(emailMessage)
    #account_sid = 'ACce8b10fd74495fcd45b4f350a1a7599a'
    #auth_token = 'fe7422e18bceaf1566afc8ae5f3a7a8d'
    #client = Client(account_sid, auth_token)
    #
    #message = client.messages.create(
    #                     body= textMessage, 
    #                     from_='+12196668102',
    #                     to='+15704125384'
    #                 )
    #
    return emailMessage

def main():
    creds = getAuthorization(scope=SCOPES)
    msg_ids = getMessagesList(creds)
    email_messages = getMessages(msg_ids, creds)
    URLList = []
    for mess in email_messages:
        URLList.append(mess.getWebsiteUrl())
    res = listJob(URLList)
    # for r in res:
    #     print(r)
    #     print('\n')
  
    bodyText = buildBody(res)
    email = createMessage(bodyText)
    sendMessage(email, creds)

    # sendText(res)
if __name__ == '__main__':
    main()

# Done: Need to fix decoder method.
# Done: create a function that will check the email body contents and extract the https:// link so we can scrape the data from that page.
# Done: create a function that will scrape the webpage and search for keywords such as Python, data analysis, statistcs, ... and return those specific job 
# postings
# TODO: Create a function to send a text message alert to my phone notifying me of the specific jobs to apply to.

