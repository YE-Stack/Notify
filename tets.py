# curl 'https://api.twilio.com/2010-04-01/Accounts/AC05527c10148eab4a7742610285965992/Messages.json' -X POST \
# --data-urlencode 'To=whatsapp:+919746338718' \
# --data-urlencode 'From=whatsapp:+14155238886' \
# --data-urlencode 'Body=Your appointment is coming up on July 21 at 3PM' \
# -u AC05527c10148eab4a7742610285965992:c8ce9c6e7347e2232c773b7327492731


import firebase_admin
import credentials as local
from firebase_admin import credentials
from firebase_admin import db


# Fetch the service account key JSON file contents
cred = credentials.Certificate('/home/ebby/Documents/yestack1-firebase-adminsdk-m6qi4-fd9ce115c6.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, local.firebase_config)

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('/result')
print(ref.get())
