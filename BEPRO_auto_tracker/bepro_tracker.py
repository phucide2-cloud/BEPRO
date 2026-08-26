import asyncio
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright
import requests

# =========================
# SETTINGS
# =========================

URL = "https://bepro-erp.web.app/analysis/editor/assignment-request?viewType=tracking"
BOT_TOKEN = '8388787458:AAHio7R_c6R2mddfSdf2gW-29npO_j-Sywc'
CHAT_ID = '7825502104'
# Browser profile lưu session đăng nhập
PROFILE_DIR = Path(__file__).parent / "bepro_browser_profile"
# Kiểm tra mỗi 10 giây
POLL_SECONDS = 0.1

# Ưu tiên Mode 1.0 trước Mode 0.5
MODES = ["Mode 1.0", "Mode 0.5"]
# MODES = ["Tracking"]

# Login credentials (use environment variables for security)
import os

EMAIL = 'phucide1@gmail.com'
PASSWORD = 'Phuc2468456'


# =========================
# NOTIFICATION
# =========================

async def notify(page, message):
    print("\n" + "=" * 70)
    print("🚨 AVAILABLE SLOT")
    print(message)
    print("=" * 70 + "\n")

    # Browser notification
    try:
        await page.evaluate(
            """(msg) => {
                try {
                    if (Notification.permission === "granted") {
                        new Notification(
                            "BEPRO Slot Available",
                            { body: msg }
                        );
                    } else if (Notification.permission !== "denied") {
                        Notification.requestPermission().then(permission => {
                            if (permission === "granted") {
                                new Notification(
                                    "BEPRO Slot Available",
                                    { body: msg }
                                );
                            }
                        });
                    }
                } catch (e) {}
            }""",
            message,
        )
    except Exception:
        pass

    # Windows beep
    try:
        import winsound

        for _ in range(3):
            winsound.Beep(1200, 400)
            await asyncio.sleep(0.2)

    except Exception:
        pass

    # Sending Telegram
    message = "Hello! Đây là tin nhắn gửi bằng Python 🚀, phát hiện trận đấu có thể đăng kí"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=data)

    print("SENDING TELEGRAM SUCCESSFULLY!!")


# =========================
# LOGIN
# =========================

async def login(page):
    """
    Automatically login with email and password.
    """
    try:
        print("Attempting auto-login...")

        # Fill email
        email_input = page.locator('//*[@id="identifier"]')
        if await email_input.is_visible():
            await email_input.fill(EMAIL)
            print("✅ Email entered")
        else:
            print("⚠️ Email field not found")
            return False

        await asyncio.sleep(0.5)

        # Fill password
        password_input = page.locator('//*[@id="password"]')
        if await password_input.is_visible():
            await password_input.fill(PASSWORD)
            print("✅ Password entered")
        else:
            print("⚠️ Password field not found")
            return False

        await asyncio.sleep(0.5)

        # Click login button
        login_button = page.locator('//*[@id="root"]/div/div/div/div/div/form/div/button')
        if await login_button.is_visible():
            await login_button.click()
            print("✅ Login button clicked")
            await page.wait_for_load_state("networkidle")
            print("✅ Login successful!")
            return True
        else:
            print("⚠️ Login button not found")
            return False

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False


# =========================
# FIND AVAILABLE SLOT
# =========================

async def find_available_slot(page, mode_text):
    """
    Tìm button chứa Mode 1.0 hoặc Mode 0.5.

    AVAILABLE:
        button KHÔNG có disabled

    UNAVAILABLE:
        button có disabled=""
    """

    buttons = page.locator("button")

    count = await buttons.count()
    print(f'IDENTIFY {count} BUTTONS')

    print(f"Checking {mode_text}: {count} buttons found")

    for i in range(count):

        button = buttons.nth(i)

        try:

            # Button phải visible
            if not await button.is_visible():
                continue

            # Lấy text bên trong button
            text = (await button.inner_text()).strip()
            print(f'TEXT INSIDE BUTTON: {text}')

            # Không phải Mode cần tìm
            if mode_text not in text:
                continue

            # =========================
            # KIỂM TRA DISABLED
            # =========================

            disabled = await button.get_attribute("disabled")
            cursor = await button.evaluate(
                "(el) => el.style.cursor"
            )
            print(f'--Status of disable: {disabled}')
            print(f'--Status of cursor: {cursor}')

            # Có disabled → unavailable
            if disabled is not None or cursor == "not-allowed":
                print(
                    f"  [{i}] {mode_text}: unavailable "
                    f"(disabled)"
                )
                continue

            # Không có disabled → AVAILABLE
            print(
                f"  [{i}] {mode_text}: ⭐ AVAILABLE"
            )

            return button, i

        except Exception as e:
            print(f"Error checking button {i}: {e}")
            continue

    return None, None


# =========================
# GET SLOT INFORMATION
# =========================

async def get_slot_info(button):
    """
    Cố gắng lấy thông tin ngày / giờ nằm gần slot.
    """

    try:

        info = await button.evaluate(
            """button => {

                let node = button;

                // Đi lên một vài level để tìm container
                for (let i = 0; i < 5 && node; i++) {

                    const text =
                        (node.innerText || "")
                        .replace(/\\s+/g, " ")
                        .trim();

                    if (text.length > 0 && text.length < 500) {
                        return text;
                    }

                    node = node.parentElement;
                }

                return "";

            }"""
        )

        return info

    except Exception:
        return ""


# =========================
# CLICK PRE-TRACKING BUTTON
# =========================

async def click_pre_tracking_button(page):
    """
    Click the button required before entering tracking loop.
    """
    try:
        print("Clicking pre-tracking button...")
        button = page.locator('//*[@id="root"]/div/div[2]/div/div/div[1]/div[1]/div/div/div[2]/button')
        if await button.is_visible():
            await button.click()
            print("✅ Pre-tracking button clicked")
            await asyncio.sleep(1)  # Wait for page to respond
            return True
        else:
            print("⚠️ Pre-tracking button not found")
            return False
    except Exception as e:
        print(f"❌ Failed to click pre-tracking button: {e}")
        return False


# =========================
# CLICK SUBMIT
# =========================

async def click_submit(page):
    print("Looking for Submit button...")

    try:

        # Tìm button Submit
        submit = page.get_by_role(
            "button",
            name=re.compile(
                r"^Submit$",
                re.IGNORECASE
            )
        )

        count = await submit.count()

        print(f"Submit buttons found: {count}")

        if count == 0:
            print("❌ Submit button not found.")
            return False

        # Click Submit
        await submit.first.scroll_into_view_if_needed()

        await asyncio.sleep(0.3)

        await submit.first.click()

        print("✅ Submit clicked!")

        return True

    except Exception as e:

        print(f"❌ Failed to click Submit: {e}")

        return False


# =========================
# MAIN TRACKER
# =========================

async def main():
    print()
    print("=" * 70)
    print("BEPRO AUTOMATIC SLOT TRACKER")
    print("=" * 70)
    print()
    print(f"Checking every {POLL_SECONDS} seconds")
    print("Priority:")
    print("  1. Mode 1.0")
    print("  2. Mode 0.5")
    print()
    print("Available = button WITHOUT disabled attribute")
    print()
    print("=" * 70)
    print()

    async with async_playwright() as p:

        # =========================
        # OPEN BROWSER
        # =========================

        context = await p.chromium.launch_persistent_context(

            str(PROFILE_DIR),

            headless=False,

            viewport={
                "width": 1600,
                "height": 800
            },

            args=[
                "--start-maximized"
            ]
        )

        # Nếu browser đã có tab
        if context.pages:

            page = context.pages[0]

        else:

            page = await context.new_page()

        # =========================
        # OPEN BEPRO
        # =========================

        print("Opening BEPRO...")

        await page.goto(
            URL,
            wait_until="domcontentloaded"
        )

        await page.wait_for_timeout(5000)

        # print()
        # print("Attempting automatic login...")
        # print()

        # login_success = await login(page)

        # if not login_success:
        #     print()
        #     print("Auto-login failed. Waiting 30 seconds for manual login...")
        #     await page.wait_for_timeout(30000)

        print()
        print("Tracker started!")
        print()

        # =========================
        # CLICK PRE-TRACKING BUTTON
        # =========================
        await asyncio.sleep(
            3
        )

        await click_pre_tracking_button(page)

        # =========================
        # MAIN LOOP
        # =========================

        while True:

            try:

                print()
                print("-" * 70)
                print("Checking BEPRO...")
                print("-" * 70)

                # =====================================
                # MODE 1.0 FIRST
                # =====================================

                selected_button = None
                selected_mode = None
                selected_index = None

                for mode in MODES:

                    button, index = await find_available_slot(
                        page,
                        mode
                    )

                    if button is not None:
                        selected_button = button
                        selected_mode = mode
                        selected_index = index

                        # STOP searching
                        break

                # =====================================
                # NOTHING AVAILABLE
                # =====================================

                if selected_button is None:
                    print()
                    print(
                        "No available Mode 1.0 / Mode 0.5."
                    )

                    print(
                        f"Next check in {POLL_SECONDS} seconds..."
                    )

                    await page.wait_for_timeout(
                        POLL_SECONDS * 1000
                    )

                    continue

                # =====================================
                # AVAILABLE FOUND
                # =====================================

                print()
                print("=" * 70)
                print("🚨 SLOT FOUND!")
                print(f"Mode: {selected_mode}")
                print(f"Button index: {selected_index}")
                print("=" * 70)

                # Get surrounding information
                slot_info = await get_slot_info(
                    selected_button
                )

                message = (
                    f"{selected_mode} is AVAILABLE!"
                )

                if slot_info:
                    message += (
                        f"\n\n{slot_info[:300]}"
                    )

                # =====================================
                # NOTIFY
                # =====================================

                await notify(
                    page,
                    message
                )

                # =====================================
                # CLICK SLOT
                # =====================================

                print()
                print(
                    f"Clicking {selected_mode}..."
                )

                await selected_button.scroll_into_view_if_needed()

                await asyncio.sleep(0.3)

                await selected_button.click()

                print(
                    f"✅ {selected_mode} clicked!"
                )

                # Give website time to register selection
                await page.wait_for_timeout(100)

                # =====================================
                # CLICK SUBMIT
                # =====================================

                submit_success = await click_submit(
                    page
                )

                if submit_success:

                    print()
                    print("=" * 70)
                    print("🎉 DONE!")
                    print("Slot selected and Submit clicked.")
                    print("=" * 70)
                    print()

                    # wait for 1 minute
                    await asyncio.sleep(6000)

                    # Stop after successful submission
                    break

                else:

                    print()
                    print(
                        "⚠️ Slot was clicked but Submit "
                        "could not be clicked automatically."
                    )

                    print(
                        "Please check the browser manually."
                    )

                    break


            # =====================================
            # CTRL + C
            # =====================================

            except KeyboardInterrupt:

                print()
                print("Tracker stopped.")

                break


            # =====================================
            # OTHER ERROR
            # =====================================

            except Exception as e:

                print()
                print(
                    "⚠️ Tracker error:"
                )

                print(e)

                print()

                print(
                    f"Retrying in {POLL_SECONDS} seconds..."
                )

                await asyncio.sleep(
                    POLL_SECONDS
                )

        # Close browser
        await context.close()


# =========================
# START PROGRAM
# =========================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print()
        print("Tracker stopped.")

        sys.exit(0)