import os
from O365 import Account
from O365.message import Message
from O365.mailbox import MailBox
import config
from pathlib import Path

client_secret = config.client_secret
client_id = config.client_id
tenant_id = config.tenant_id
credentials = (client_id, client_secret)
account = Account(credentials)

class email:

    def __init__(self, title, received, path):
        self.title = title
        self.received = received
        self.path = path

    def getTitle(self):
        return self.title
    
    def getReceived(self):
        date_received = self.received.strftime("%x")
        month_received = self.received.strftime("%B")
        return {'date': date_received, 'month': month_received}

    def getPath(self):
        return self.path

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


def getMessages(inbox, folder_path):
    messages = []
    for message in inbox.get_messages():
        # TODO: Need to fix the path where the file is saved.  I think this should be a method in the email class.
        emailfilepath = message.save_as_eml(to_path=Path(os.path.join(folder_path, f'{message.subject}.eml')))
        m = email(title=message.subject, received=message.received, path=emailfilepath)
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
if __name__ == '__main__':
    mailbox = account.mailbox(resource='zachgilliom@outlook.com')
    dir_path = '/home/zacharygilliom/Documents/email-folder/'

    inbox = mailbox.inbox_folder()
    
    inbox_messages = getMessages(inbox=inbox, folder_path=dir_path)

    for m in inbox_messages:
        print(m.getTitle())
        print(m.getReceived())
        print(m.getPath())

    destination_directory = emailDestinationDirectory(dir_path)

    destination_directory.createDirectory(inbox_messages[0].getReceived())

    # TODO: Go through all the messages and create a file in the appropriate month subdirectory.
