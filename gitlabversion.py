import sys
import requests
import urllib3
import os
import argparse
import json
from colorama import Fore, init

urllib3.disable_warnings()
init()

parse = argparse.ArgumentParser()
parse.add_argument("-u", type=str, help="Target url.", default="")
args = parse.parse_args()


def get_hash(url):
    print(Fore.WHITE + "[*] Getting'", end="")
    print(Fore.GREEN + url, end="")
    print(Fore.WHITE + "'fingerprint hash")
    json_url = "{}/assets/webpack/manifest.json".format(url)
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': url,
        'Origin': url
    }
    try:
        res = requests.get(url=json_url, headers=header, verify=False, timeout=10)
        version_hash = res.json()["hash"]
    except Exception as e:
        print(Fore.RED + "[-] Get hash failed!Please retry!")
        sys.exit()
    else:
        if version_hash != "":
            print(Fore.WHITE + "[+] Get hash success,hash: ", end="")
            print(Fore.GREEN + version_hash)
            return version_hash
        else:
            print(Fore.RED + "[-] Get hash failed!Please retry!")
            sys.exit()


def get_version(url, version_hash):
    try:
        print(Fore.WHITE + "[*] Prompt local fingerprint database match......")
        local_finger_json = load_local_finger()
        version = local_finger_json[version_hash]["versions"][0]
        build = local_finger_json[version_hash]["build"]
    except Exception as e:
        print(Fore.RED + "[-] Local fingerprint matching failed! Trying to obtain remote fingerprint library......")
        try:
            finger_url = "https://raw.githubusercontent.com/righel/gitlab-version-nse/main/gitlab_hashes.json"            
            res = requests.get(url=finger_url, verify=False, timeout=10)
            version = res.json()[version_hash]["versions"][0]
            build = res.json()[version_hash]["build"]
        except Exception as e:
            print(Fore.RED + "[-] Remote fingerprint matching failed!")
            sys.exit()
        else:
            update_local_finger(finger_json_string=res.text)
            print(Fore.WHITE + "[+] Fingerprint matching successful!\n[+] gitaddr: ", end="")
            print(Fore.GREEN + url)
            print(Fore.WHITE + "[+] version: ", end="")
            print(Fore.GREEN + version)
            print(Fore.WHITE + "[+] buildby: ", end="")
            print(Fore.GREEN + build)
    else:
        print(Fore.WHITE + "[+] Fingerprint matching successful!\n[+] gitaddr: ", end="")
        print(Fore.GREEN + url)
        print(Fore.WHITE + "[+] version: ", end="")
        print(Fore.GREEN + version)
        print(Fore.WHITE + "[+] buildby: ", end="")
        print(Fore.GREEN + build)


def write_file(filename, i_type, string):
    with open(filename, i_type, encoding="utf-8") as f:
        f.write(string)


def read_file(filename, r_type):
    if r_type == "read_by_line":
        lines = []
        with open(filename, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if line.strip() not in lines:
                    lines.append(line.strip())
        return lines
    elif r_type == "read_all":
        with open(filename, "r", encoding="utf-8") as f:
            res = f.read()
        return res
    else:
        print(Fore.RED + "[-] There is no such option for reading files!")
        sys.exit()


def update_local_finger(finger_json_string):
    if not os.path.exists("local_finger.json") or os.path.getsize("local_finger.json") == 0:
        write_file(filename="local_finger.json", i_type="w", string=finger_json_string)
    else:
        local_finger_json_str = read_file(filename="local_finger.json", r_type="read_all")
        if local_finger_json_str != finger_json_string:
            write_file(filename="local_finger.json", i_type="w", string=finger_json_string)
        else:
            pass
def load_local_finger():
    if os.path.exists("local_finger.json") and os.path.getsize("local_finger.json") != 0:
        res = read_file(filename="local_finger.json", r_type="read_all")
        try:
            local_finger_json = json.loads(res)
        except Exception as e:
            print(Fore.RED + "An error occurred while converting the local fingerprint library to json!")
            pass        
        else:
            return local_finger_json
    else:
        print(Fore.RED + "[-] The local fingerprint library file does not exist or the file content is empty!")
        pass
def run():
    if args.u != "" and ("http:" in args.u or "https" in args.u):
        version_hash = get_hash(url=args.u)
        get_version(url=args.u, version_hash=version_hash)
    else:
        print(Fore.RED + "[-] The url format is incorrect!")
        sys.exit()


if __name__ == '__main__':
    run()
