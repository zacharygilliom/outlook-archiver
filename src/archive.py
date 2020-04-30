import os
import requests
import msal
from O365 import Account
from O365.message import Message
from O365.mailbox import MailBox
import config

#client_secret = '8YWEDMKed/Qb@@EPxKT_D7v4LzzLKbK0'
#client_id = '3459265f-d17d-47bd-80c7-3507c243ff64'
#tenant_id = 'f8cdef31-a31e-4b4a-93e4-5f571e91255a'

client_secret = config.client_secret
client_id = config.client_id
tenant_id = config.tenant_id
credentials = (client_id, client_secret)
account = Account(credentials)

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

inbox = mailbox.inbox_folder()

for messages in inbox.get_messages():
    print(messages)


m = mailbox.new_message()
m.to.add('zacharygilliom@gmail.com')
m.body = 'Hey There'
m.send()

