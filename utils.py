from urllib import request

from bs4 import BeautifulSoup


def proxy_list(protocol="HTTP", country = None):
    res = request.urlopen("https://scrapingant.com/free-proxies/")
    # drop emojis
    soup = BeautifulSoup(
        res.read().decode("utf-8")
                  .encode('ascii', 'ignore')
                  .decode('ascii'),
        features='lxml')

    out = []
    for row in soup.find("table").find_all("tr")[1:]:
        row_text = [cell.text.strip() for cell in row.find_all("td")]
        
        if row_text[2] != protocol:
            continue

        if country and row_text[3] not in country:
            continue

        out.append("{ip}:{port}".format(ip=row_text[0], port=row_text[1]))

    return out
