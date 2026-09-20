from bs4 import BeautifulSoup


def extract_announces_links(html: str) -> list[str]:    #TODO cambiare metodo e integrarlo effettivamente per aiutare lo scraping
    soup = BeautifulSoup(html, "html.parser")

    return [
        title.get_text(" ", strip=True)
        for title in soup.select("h1, h2, h3")
        if title.get_text(strip=True)
    ]