from django.core.mail import send_mail
from django.conf import settings
import random
import string


def retrieve_mail(retriever, retriever_password):
    subject = 'Retrieve password'
    message = f'Here is your new password: {retriever_password}\nDont forget it next time!'
    sender = settings.EMAIL_HOST_USER
    recipient_list = [retriever]
    send_mail(subject, message, sender, recipient_list, fail_silently=False)


def generate_password():
    password_list = []

    [password_list.append(random.choice(string.ascii_letters)) for _ in range(random.randint(8, 10))]
    [password_list.append(random.choice(string.digits)) for _ in range(random.randint(2, 4))]
    [password_list.append(random.choice(string.punctuation)) for _ in range(random.randint(2, 4))]
    random.shuffle(password_list)
    password = "".join(password_list)
    return password
