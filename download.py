from html.parser import HTMLParser
import requests, gzip

domain = "openwrt.org"
isA = False
version = None
_link = None
_efi = False

class HTMLVersionParser(HTMLParser):
        
    def handle_starttag(self, tag, attrs):
        global isA
        if tag == "a":
            isA = True

    def handle_endtag(self, tag):
        global isA
        if tag == "a":
            isA = False
        
    def handle_data(self, data):
        global isA, version
        if "OpenWrt " in data and isA and version == None:
            version = data.split(" ")[1]

class HTMLDownloadLinkParser(HTMLParser):
        
    def handle_starttag(self, tag, attrs):
        global isA
        if tag == "a":
            isA = True

    def handle_endtag(self, tag):
        global isA
        if tag == "a":
            isA = False
        
    def handle_data(self, data):
        global isA, _link
        #print(data)
        if ".img.gz" in data and isA and "combined" in data and _link == None:
            if _efi:
                if ".img.gz" in data and isA and "combined" in data and _link == None and "efi" in data:
                    _link = data
            else:
                if ".img.gz" in data and isA and "combined" in data and _link == None and "efi" not in data:
                    _link = data

_version = HTMLVersionParser()
_downloadlink = HTMLDownloadLinkParser()


def getVersion():
    global domain, _version, version
    page = requests.get("https://downloads.{domain}/".format(domain=domain))
    html = page.content.decode("utf-8")
    _version.feed(html)
    return version

def getDownloadFile(v):
    global domain, _downloadlink
    page = requests.get("https://downloads.{domain}/releases/{version}/targets/x86/64/".format(domain=domain, version=v))
    _downloadlink.feed(page.content.decode("utf-8"))
    return "https://downloads.{domain}/releases/{version}/targets/x86/64/openwrt-{version}-x86-64-{file}".format(domain=domain, version=v, file=_link)

def Downloader(efi):
    global _efi
    _efi = efi
    _version = getVersion()
    _url = getDownloadFile(_version)
    print("Downloading Version:", _version)
    r = requests.get(_url)
    _fname = "openwrt-{version}-x86-64-{file}".format(version=_version, file=_link)
    with open(_fname, 'wb') as f:
        f.write(r.content)
        f.close()
        print("File {} is Saved!".format(_fname))

def IsEfi():
    info = input("EFI File? (YES or NO): ")
    if info.lower() == "yes":
        Downloader(True)
    else:
        Downloader(False)
       
if __name__ == "__main__":
        IsEfi()
