
from playwright.sync_api import sync_playwright, TimeoutError

def get_ind_nz_score():

    with sync_playwright() as p:

        # Launch Google Chrome
        browser = p.chromium.launch(
            channel="chrome",
            headless=False
        )

        page = browser.new_page()

        try:
            # Open Cricbuzz
            page.goto(
                "https://www.cricbuzz.com/",
                wait_until="domcontentloaded"
            )

            # Target the India vs New Zealand 1st ODI match
            match_selector = 'a[href*="nz-vs-ind-1st-odi"]'

            # Wait until the match appears
            page.wait_for_selector(
                match_selector,
                state="visible",
                timeout=20000
            )

            # Locate the match
            match = page.locator(match_selector).first

            # Extract match details
            score = match.inner_text()

            print("\n====== IND vs NZ SCORE ======")
            print(score.strip())
            print("=============================")

            # Save screenshot
            page.screenshot(path="score.png", full_page=True)

            print("Screenshot saved: score.png")

        except TimeoutError:
            print("IND vs NZ match not found or not loaded.")

            page.screenshot(path="score.png")

        finally:
            browser.close()


if __name__ == "__main__":
    get_ind_nz_score()
