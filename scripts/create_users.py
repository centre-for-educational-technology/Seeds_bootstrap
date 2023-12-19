from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import random, string
import pandas as pd



def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def run():
    ids = []
    pwds = []
    for i in range(50):
        user_name = 'user' + str(i)
        user_email = 'user' + str(i) + '@seeds.org'
        temp_pwd = randomword(5)
        user_pwd = make_password(temp_word)
        first_name = user_name
        last_name = 'seeds'
        try:
            print('creating user-',i)
            obj = User.objects.create(first_name=first_name,last_name=last_name,username=user_name,email=user_email,password=user_pwd)
            ids.append(user_email)
            pwds.append(temp_pwd)
        except:
            print('error occurred.')

    df = pd.DataFrame({'id':ids,'pwd':pwds})
    df.to_csv('seeds_users.csv',index=False)