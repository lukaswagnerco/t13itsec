byte_64_sufix = b"aaaaaaaaaaaaaaaaaaaaaaaaaa\x02\x0DIT-Sicherheit5.0\x18\x02\x0DIT-Sicherheit1.0\x00"
prefix = b"!!!TUMFile\xff\x07studentX\x2B"


print(len(byte_64_sufix))
print(len(prefix))





with open("datei1", "wb") as f:
    f.write(collfile1)

with open("datei2", "wb") as f:
    f.write(collfile2)

check_files('datei1', 'datei2')

# Upload them to get a flag :)
response = requests.post(URL, files={'file1': collfile1, 'file2': collfile2})
print(response.text)
