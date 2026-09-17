import re
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
async def download_announces_html(url: str,class_code: str,province_code: str, headless: bool = True) -> list[str]:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless)
        announces_list = []
        try:
            context = await browser.new_context(extra_http_headers=HEADERS)
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            first_part = url.split("/", 3)
            url_first_part = "/".join(first_part[:3]) + "/"
            rows = page.locator("div.results-row").filter(
                has=page.locator("span.result-code strong").filter(
                    has_text=re.compile(
                        rf"^\s*{re.escape(class_code)}\s*$",
                        re.IGNORECASE
                    )
                )
            )

            try:
                await rows.first.wait_for(state="visible", timeout=1000)
            except PlaywrightTimeoutError:
                print(f"Nessuna riga trovata per il codice {class_code}")
            else:
                numero_righe = await rows.count()
                print(f"Trovate {numero_righe} righe")

                for i in range(numero_righe):
                    row = rows.nth(i)
                    link = row.locator("a.outline-action")
                    href = await link.get_attribute("href")
                    print(f"Href trovato sulla riga {i + 1}")
                    print(f"Href:{url_first_part + href}")
                    announces_list.append(url_first_part + href)
        finally:
            await browser.close()
            return announces_list