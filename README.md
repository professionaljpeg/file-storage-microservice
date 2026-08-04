# file-storage-microservice
A file storage microservice that uploads, recieves, deletes, and validates files from multiple applications. It uses a web

# How to Request data
First, get an API key from the website classwork.engr.oregonstate.edu:12726 and store the key in your code or in a text file to use later.
Then, use the API key along with the URL 'http://classwork.engr.oregonstate.edu:12627/api/v1/files' to upload a file.

## Command Line Example (bash)
```
curl -X POST -H "X-API-Key: my-super-secret-key-1" -F "file=@/path/to/document.pdf" http://classwork.engr.oregonstate.edu:12627/api/v1/files
```
## Python Example
```
base_url = 'http://classwork.engr.oregonstate.edu:12627/api/v1/files'
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(base_url, headers=headers, files=files)
    
    if response.headers.get('Content-Type') == 'application/json':
        print(response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
```

# How to Recieve Data
Receiving data is similar to requesting it, the only real difference is the URL that you're using.
In this instance, you're using http://classwork.engr.oregonstate.edu:12627/api/v1/files/file_you_want.pdf, with the name of the file that you're using at the end of the url.

## Command Line Example (bash)
```
curl -O -H "X-API-Key: my-super-secret-key-1" http://classwork.engr.oregonstate.edu:12627/api/v1/files/document.pdf
```

## Python Example
```
file_url = http://classwork.engr.oregonstate.edu:12627/api/v1/files/document.pdf
response = requests.get(file_url)

if response.status_code == 200:
    with open('downloaded_test.pdf', 'wb') as f:
        f.write(response.content)
    print("Success: File downloaded and saved as 'downloaded_test.pdf'")
else:
    print(f"Failed to download: {response.status_code}")
