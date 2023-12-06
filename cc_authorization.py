import requests
import random

def authorize_cc(cc_num, name, exp, curr_amnt):
    url = 'http://blitz.cs.niu.edu/CreditCard/'
    jsonsend = {'vendor': "Very Fancy", 'trans': random.randrange(1, 10**10), 'cc': cc_num, 'name': name, 'exp': exp, 'amount': curr_amnt}
    result = requests.post(url, json=jsonsend)
    return result

def test_cc():
    return authorize_cc('6011123443211234', 'test', '12/2024', '100.00')