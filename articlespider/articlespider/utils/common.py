import hashlib, re

def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    match_re = re.match('.*?(\d+).*', text)
    if match_re:
        num = int(match_re.group(1))
    else:
        num = 0
    return num


if __name__ == '__main__':
    print(get_md5('http://www.baudu.com'.encode('utf-8')))
