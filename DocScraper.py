import requests
from bs4 import BeautifulSoup
import sys

def scrape_documentation(url, headers=None):
    """
    Fetches the URL and returns an ordered list of (type, content, level) items,
    where `type` is one of:
      - 'heading' (level 1–6)
      - 'paragraph'
      - 'codeblock'
      - 'list' (unordered or ordered)
    """
    headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # We'll walk the body children in document order
    body = soup.body or soup  # fallback to whole doc if <body> missing
    content = []

    def process_element(el):
        tag = el.name
        if tag in [f"h{i}" for i in range(1, 7)]:
            level = int(tag[1])
            text = el.get_text(strip=True)
            content.append(("heading", text, level))
        elif tag == "p":
            text = el.get_text(strip=True)
            if text:
                content.append(("paragraph", text, None))
        elif tag == "pre":
            code = el.get_text()
            content.append(("codeblock", code, None))
        elif tag == "ul":
            items = [li.get_text(strip=True) for li in el.find_all("li", recursive=False)]
            content.append(("list_unordered", items, None))
        elif tag == "ol":
            items = [li.get_text(strip=True) for li in el.find_all("li", recursive=False)]
            content.append(("list_ordered", items, None))
        # You could extend: blockquotes, tables, images, etc.

    # Traverse in-order
    for el in body.descendants:
        if isinstance(el, BeautifulSoup.Tag) and el.name in ["h1","h2","h3","h4","h5","h6","p","pre","ul","ol"]:
            process_element(el)

    return content

def save_as_markdown(content, filename="output.md"):
    """
    Writes the scraped content to a Markdown file.
    """
    lines = []
    for typ, txt, lvl in content:
        if typ == "heading":
            lines.append("#" * lvl + " " + txt)
            lines.append("")  # blank line
        elif typ == "paragraph":
            lines.append(txt)
            lines.append("")
        elif typ == "codeblock":
            lines.append("```")
            lines.append(txt.rstrip())
            lines.append("```")
            lines.append("")
        elif typ == "list_unordered":
            for item in txt:
                lines.append(f"- {item}")
            lines.append("")
        elif typ == "list_ordered":
            for idx, item in enumerate(txt, start=1):
                lines.append(f"{idx}. {item}")
            lines.append("")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved documentation to {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python docs_scraper.py <URL> [output.md]")
        sys.exit(1)

    url = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "output.md"

    data = scrape_documentation(url)
    if not data:
        print("No documentation elements found on that page.")
    else:
        save_as_markdown(data, out_file)

if __name__ == "__main__":
    main()

