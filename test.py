import requests

# Testing POST requests (file upload)
url = 'http://classwork.engr.oregonstate.edu:12627/api/v1/files'
files = {'file': open('document.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())

# Testing GET requests (file download)
url = 'http://classwork.engr.oregonstate.edu:12627/api/v1/files/document.pdf'
response = requests.get(url)
print(response.content)

# Testing DELETE requests (file deletion)
response = requests.delete(url)
print(response.json())
