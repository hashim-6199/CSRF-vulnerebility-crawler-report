import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_forms(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    return soup.find_all("form")

def has_csrf_token(form):
    for input_tag in form.find_all("input"):
        if input_tag.get("type") == "hidden":
            if "csrf" in (input_tag.get("name") or "").lower():
                return True
    return False

def crawl_for_csrf(start_url):
    visited = set()
    forms_missing_csrf = []

    def crawl(url):
        if url in visited:
            return
        visited.add(url)
        try:
            r = requests.get(url)
        except Exception:
            return
        soup = BeautifulSoup(r.text, "html.parser")
        forms = soup.find_all("form")
        for form in forms:
            if not has_csrf_token(form):
                forms_missing_csrf.append({
                    "url": url,
                    "form": str(form)
                })
        # Simple link following
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(url, a_tag["href"])
            if urlparse(link).netloc == urlparse(start_url).netloc:
                crawl(link)

    crawl(start_url)
    return forms_missing_csrf

if __name__ == "__main__":
    target = input("Enter target URL (e.g., http://localhost:8000): ")
    result = crawl_for_csrf(target)
    for entry in result:
        print(f"[!] CSRF Token Missing at {entry['url']}\nForm:\n{entry['form']}\n")
