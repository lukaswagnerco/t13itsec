byte_64_sufix = b"\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\01\x02\x03ITS5.0\x18\x02\x0DIT-Sicherheit1.0\x00"
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


collfile1 += byte_64_sufix
collfile2 += byte_64_sufix


print(f"new length of collfile1: {len(collfile1)} with content:\n {collfile1}")
print(f"new length of collfile2: {len(collfile2)} with content:\n {collfile2}")

print(f"Byte at colfile1 65 is: {collfile1[65]}")
print(f"Byte at colfile2 65 is: {collfile2[65]}")