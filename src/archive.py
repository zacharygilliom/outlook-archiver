import os
from O365 import Account
from O365.message import Message
from O365.mailbox import MailBox
import config

client_secret = config.client_secret
client_id = config.client_id
tenant_id = config.tenant_id
credentials = (client_id, client_secret)
account = Account(credentials)

class email:

    def __init__(self, title, received):
        self.title = title
        self.received = received

    def getTitle(self):
        return self.title
    
    def getReceived(self):
        date_received = self.received.strftime("%x")
        month_received = self.received.strftime("%B")
        return {'date': date_received, 'month': month_received}

class emailDestinationDirectory:

    def __init__(self, emailDirectory):
        self.emailDirectory = emailDirectory

    def ldir(self):
        return os.listdir(self.emailDirectory)



def getMessages(inbox):
    messages = []
    for message in inbox.get_messages():
        m = email(title=message.subject, received=message.received)
        messages.append(m)
    return messages


# When authentication runs out, uncomment the below three lines to re-authenticate.
# -------------------------------------------------------------------
#if account.authenticate(scopes=['basic', 'mailbox', 'message_all']):
#    print("authenticated successfully")
# -------------------------------------------------------------------

# For single user accounts, I think this is the way to authenticate for a corporate account.
# ______________________________________________________________________________
#account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
#
#if account.authenticate(scope=['basic']):
#    print('Authentication Complete!')
# _______________________________________________________________________________

mailbox = account.mailbox(resource='zachgilliom@outlook.com')
dir_path = '/home/zacharygilliom/Documents/email-folder/'

inbox = mailbox.inbox_folder()

inbox_messages = getMessages(inbox=inbox)

for m in inbox_messages:
    print(m.getTitle())
    print(m.getReceived())

destination_directory = emailDestinationDirectory(dir_path)

print(destination_directory.ldir())

print(os.listdir(dir_path))
