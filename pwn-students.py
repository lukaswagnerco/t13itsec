import subprocess
import re
import zipfile
import os
from operator import truediv

import requests
import shutil
import sys

from parser import get_itsec_grade, check_files

FASTCOLL_ZIPNAME = 'fastcoll.zip'
FASTCOLL_DIR = 'fastcoll'
FASTCOLL_EXE = 'fastcoll'
PREFIX_FILE = 'md5_prefix'

# Copy the URL from the scoreboard here
URL = "https://t13-94410145767ecbf4.itsec.sec.in.tum.de"

def setup():
    """ Downloads and compiles fastcoll. Requires a C++ compiler (g++) and the boost library installed system-wide. """
    try:

        print("hello")
        os.mkdir(FASTCOLL_DIR)

        print("Fetching fastcoll...")
        # First download and compile fastcoll
        r = requests.get("https://www.win.tue.nl/hashclash/fastcoll_v1.0.0.5-1_source.zip")
        with open(FASTCOLL_ZIPNAME, 'wb') as f:
            f.write(r.content)
        z = zipfile.ZipFile(FASTCOLL_ZIPNAME)
        z.extractall(FASTCOLL_DIR)
        os.remove(FASTCOLL_ZIPNAME)

        print("Building fastcoll...")
        gpp_path = shutil.which("g++")
        if gpp_path is None:
            print("g++ is not installed, please install it first!")
            shutil.rmtree(FASTCOLL_DIR)
            sys.exit(-1)
        
        try:
            subprocess.check_call([gpp_path, "-D", "BOOST_TIMER_ENABLE_DEPRECATED", "block0.cpp", "block1.cpp", "block1stevens00.cpp", "block1stevens01.cpp", "block1stevens10.cpp", "block1stevens11.cpp", "block1wang.cpp", "main.cpp", "md5.cpp", "-lboost_program_options", "-lboost_filesystem", "-o", FASTCOLL_EXE], cwd=FASTCOLL_DIR)
            print("Ok fastcoll is ready, let's go!")
        except subprocess.CalledProcessError:
            print("You probably don't have the boost library installed, try installing it or simply pwn on sandkasten :)")
            shutil.rmtree(FASTCOLL_DIR)
            sys.exit(-1)
    except FileExistsError:
        # Ok probably already downloaded
        pass

def create_md5_collision(prefix, fastcoll_bin):
    """ Performs an identical-prefix collision attack on md5. For the specified prefix it generates two distinct suffixes that generate an identical md5 hash. """
    print(f"Generating an md5 collision with your prefix: {prefix}...")
    with open(PREFIX_FILE, 'wb') as f:
        f.write(prefix)

    stdout = subprocess.check_output([fastcoll_bin, PREFIX_FILE]).decode()

    collfile1, collfile2 = re.search(r"Using output filenames: '(.+)' and '(.+)'", stdout).groups()
    runtime = re.search(r"Running time: (.+) s", stdout).group(1)

    # Try generating the md5 hash for both of these files (e.g. via the md5sum utility)!
    print(f"Generated collision files {collfile1} and {collfile2} in {runtime} seconds!")

    with open(collfile1, 'rb') as cf1, open(collfile2, 'rb') as cf2:
        return (cf1.read(), cf2.read())

fastcoll_bin = shutil.which("fastcoll")
if fastcoll_bin is None:
    # Try to setup fastcoll if not installed.
    # Note that the binary is already available on the sandkasten and on the autograder
    # if you do not want to build it on your system.
    setup()
    fastcoll_bin = f"{FASTCOLL_DIR}/{FASTCOLL_EXE}"

# Adjust this to suite your needs


def build_suffix(jump1, jump2):
    grade_5 = b"\x02\x0dIT-Sicherheit5.0\x00"
    grade_1 = b"\x02\x0dIT-Sicherheit1.0\x00"


    jump1 -= 4
    jump2 -= 4

    if jump1 > jump2:
        temp = jump1
        jump1 = jump2
        jump2 = temp

    total_length = jump2 + len(grade_5) + 5

    suffix = bytearray(total_length)

    suffix[jump1 : jump1+len(grade_1)] = grade_1

    jump_target = jump2+len(grade_5)
    jump_position = jump1+len(grade_1)+2
    jump_distance = jump_target-jump_position

    suffix[(jump_position-2)] = 0x01
    suffix[jump_position-1] = jump_distance

    suffix[jump2 : jump2+len(grade_5)] = grade_5

    mod = len(suffix)%64

    for i in range(mod):
        suffix += b"\x01"

    return suffix

prefix = b"!!!TUMFile\xff\x07studentX\xa6"




# Generate your two differing certificates
# TODO

while True:
    collfile1, collfile2 = create_md5_collision(prefix, fastcoll_bin)
    print(f"length of collfile1: {len(collfile1)} with content:\n {collfile1}")
    print(f"length of collfile2: {len(collfile2)} with content:\n {collfile2}")
    if collfile1[187] != collfile2[187]:
        print(f"unterschiedliche stelle: 187 und ist in collfile1: {collfile1[187]} und in collfile2: {collfile2[187]}")
        jump1 = collfile1[187]
        jump2 = collfile2[187]
        print(f"jump1: {jump1}")
        print(f"jump2: {jump2}")
        if ((jump1 < 10) or (jump2 < 10)):
            continue
        if (abs(jump1-jump2) < 25):
            continue
        suffix = build_suffix(jump1, jump2)
        collfile1 += suffix
        collfile2 += suffix
        print(f"length of collfile1: {len(collfile1)} with content:\n {collfile1}")
        print(f"length of collfile2: {len(collfile2)} with content:\n {collfile2}")
        get_itsec_grade(collfile1)
        get_itsec_grade(collfile2)
        break
