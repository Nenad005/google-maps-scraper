import requests as r
import json

with open('test.json', 'r') as f:
    links = json.loads(f.read())

for link in links:
    response = r.get(link)
    with open('exit.html', 'wb') as f:
        f.write(response.content)
    input()