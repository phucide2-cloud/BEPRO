import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

THREAD_URL = "https://bepro.slack.com/archives/C06UCHA7LR3/p1786711073365449?thread_ts=1786525060.562109&cid=C06UCHA7LR3"
#THREAD_URL ='https://bepro.slack.com/archives/C06UCHA7LR3/p1786525060562109'
THREAD_ID = '1786525060.562109'
CHANNEL_ID= 'C06UCHA7LR3'
CHAT_BOX = f'//*[@id="{CHANNEL_ID}-{THREAD_ID}-thread-list-Thread_input"]/div/div[2]/div/div/div[2]/div/div[1]/p'

PROFILE_DIR = Path(__file__).parent / "chrome-bot-profile"
POLL_SECONDS = 3
ACTIVITY = 'https://app.slack.com/client/T135YQX3K/activity-inbox'


def browser_config():
    has_display = bool(os.environ.get("DISPLAY"))
    if has_display:
        return False, ["--start-maximized"]
    return True, []


async def main():
    print()
    print('=' * 70)
    print("SLACK AUTOMATIC  TRACKER")
    print("=" * 70)
    print(f"Checking every {POLL_SECONDS} seconds")
    print(f'Checking for tracking deadline')
    print("=" * 70)
    headless, args = browser_config()
    print(f"Launching browser in {'headless' if headless else 'headed'} mode")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=False,

            viewport={
                "width": 1000,
                "height": 500
            },

            #args=['--start-maximized']

        )



        page = await context.new_page()

        print("Opening SLACK...")




        await page.goto(THREAD_URL,
                        wait_until="domcontentloaded"

                        )
        #await page.wait_for_timeout(100000)

        button = page.locator('//*[@id="page_contents"]/div/div/div[2]/p/a[2]')
        if await button.is_visible():
            await button.click()
            print("✅ Pre-tracking button clicked")
            await asyncio.sleep(5)  # Wait for page to respond

        else:
            print("⚠️ Pre-tracking button not found")


        await asyncio.sleep(2)


        print("Watching thread...")
        latest = []
        while True:
            try:
                messages = await  page.locator('.p-rich_text_block').all_text_contents()
                if len(latest) == 0:
                    latest = messages[-5:]

                elif latest == messages[-5:]:
                    print(f'Latest message:')
                    for message in latest:
                        print(f'---{message}')

                    # reply_box = page.locator(CHAT_BOX)
                    #
                    # if await reply_box.count() > 0:
                    #     print("✅ reply_box located")
                    #     await reply_box.click()
                    #     await page.keyboard.type("1")
                    #     #await page.keyboard.press("Enter")
                    # else:
                    #     print("❌ reply_box NOT found")


                else:
                    latest = messages[-5:]
                    print(f'THE LATEST MESSAGE CHANGE: {latest}')
                    print('='* 70)
                    print('CHECKING IF THE MATCH OR NOT (deadline)')

                    if any('Deadline' in message for message in latest):
                        print(f'NEW MATCH FOUND:')

                        reply_box = page.locator(CHAT_BOX)

                        if await reply_box.count() > 0:
                            print("✅ reply_box located")
                            await reply_box.click()
                            await page.keyboard.type("1")
                            await page.wait_for_timeout(300)
                            await page.keyboard.press("Enter")
                            print('Successfully claim one match')
                            # Wait for result apply
                            await asyncio.sleep(10)
                        else:
                            print("❌ reply_box NOT found")
                    else:
                        print('NOT FOUND')

                print(f'NEXT CHECK IN {POLL_SECONDS} SECONDS')
                await asyncio.sleep(POLL_SECONDS)

            except Exception as e:
                print("Error:", str(e))
                await page.wait_for_timeout(1000)
        last_message = ""
        last_message = ""
        # while True:
        #     try:
        #         messages = await page.locator(".p-rich_text_block").all_text_contents()
        #         if len(messages) == 0:
        #             print("0")
        #             continue
        #         latest = messages[-1]
        #         if latest != last_message:
        #             last_message = latest
        #             print("New message:", latest)
        #             if ("Deadline" in latest): #or ("If you want" in latest or "If you possible" in latest)):
        #                 print("Deadline detected")
        #                 reply_box = page.locator(
        #                     '//*[@id="C06UCHA7LR3-1786525060.562109-thread-list-Thread_input"]/div/div[2]/div/div/div[2]/div/div[1]/p'
        #                 )
        #
        #                 await reply_box.click()
        #                 await page.keyboard.type("1")
        #                 #await page.keyboard.press("Enter")
        #         await page.wait_for_timeout(2000)
        #     except Exception as err:
        #         print("Error:", str(err))
        #         await page.wait_for_timeout(1000)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
