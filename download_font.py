import urllib.request
url = 'https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC-Regular.ttf'
print("Downloading font...")
urllib.request.urlretrieve(url, 'NotoSansSC-Regular.ttf')
print("Font downloaded.")
