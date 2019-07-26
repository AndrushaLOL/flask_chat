from twilio.rest import Client
import random


accound_sid = 'AC5e7ec870589fd95b4b7b27d137852ab0'
auth_token = 'b7356d8d93e01b7a0741e330cabd830a'
client = Client(accound_sid, auth_token)


def generate_code():
    return random.randint(1000, 9999)


def send_sms(to, code):
    body = f'your verification code: {code}'
    message = client.messages.create(
        body=body,
        from_='+12562697602',
        to=to
    )
    return message.sid
