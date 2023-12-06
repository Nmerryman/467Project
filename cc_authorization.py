import requests

def authorize_cc(vendor, trans_num, cc_num, name, exp, curr_amnt):
    url = 'http://blitz.cs.niu.edu/CreditCard/'
    jsonsend = {'vendor': vendor, 'trans': trans_num, 'cc': cc_num, 'name': name, 'exp': exp, 'amount': curr_amnt}
    result = requests.post(url, json=jsonsend)
    return result

if __name__ == '__main__':
    # trans_num ALWAYS has to be unique
    response = authorize_cc('VE001-99', '907-987654321-298', '6011 1234 4321 1234', 'John Doe', '12/2024', '654.32')
    print(response.text)