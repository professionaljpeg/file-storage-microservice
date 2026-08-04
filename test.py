import requests

appName = 'test7'
headers = {'X-API-Key': '5897376cf290c02b.Fj9-tjRaD2Fa6fwRKt8t4sl2tJpuFGS-fHCxF4CXUuM'}
base_url = 'http://classwork.engr.oregonstate.edu:12627/api/v1/files'
file_url = f'{base_url}/document.pdf'

# Testing POST requests (file upload)
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(base_url, headers=headers, files=files)
    
    if response.headers.get('Content-Type') == 'application/json':
        print(response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")

# Testing GET requests (file download)
response = requests.get(file_url)

if response.status_code == 200:
    # FIX: Save the file to disk instead of printing binary to the terminal
    with open('downloaded_test.pdf', 'wb') as f:
        f.write(response.content)
    print("Success: File downloaded and saved as 'downloaded_test.pdf'")
else:
    print(f"Failed to download: {response.status_code}")

# Testing DELETE requests (file deletion)
response = requests.delete(file_url, headers=headers)

if response.headers.get('Content-Type') == 'application/json':
    print(response.json())
else:
    print(f"Error {response.status_code}: {response.text}")