
from playwright.sync_api import sync_playwright, TimeoutError
import csv


def whatsapp_automation():

    with sync_playwright() as p:

        # 1. Launch Chrome with saved session
        context = p.chromium.launch_persistent_context(
            user_data_dir="whatsapp_profile",
            channel="chrome",
            headless=False,
            viewport=None
        )

        page = context.pages[0] if context.pages else context.new_page()

        try:

            # 2. Open WhatsApp Web
            page.goto(
                "https://web.whatsapp.com/",
                wait_until="domcontentloaded"
            )

            search_box = page.locator(
                'input[placeholder="Search or start a new chat"]'
            )

            search_box.wait_for(timeout=60000)

            print("WhatsApp loaded successfully!")

            # 3. Search one contact
            contact_name = "MySoul"

            search_box.fill(contact_name)

            contact = page.get_by_text(
                contact_name,
                exact=True
            ).first

            contact.wait_for(timeout=15000)
            contact.click()

            print("Chat opened:", contact_name)

            # 4. Locate message input
            message_box = page.get_by_role(
                "textbox",
                name=f"Type a message to {contact_name}"
            )

            message_box.wait_for(timeout=15000)

            # 5. Prepare personalized message
            message = (
                f"Hi {contact_name}, "
                "how are you? Hope you are doing well!"
            )

            print("\n--- MESSAGE PREVIEW ---")
            print(message)

            confirmation = input(
                "\nSend message? (yes/no): "
            )

            if confirmation.strip().lower() == "yes":

                # Enter message
                message_box.fill(message)

                # Click Send
                send_button = page.get_by_role(
                    "button",
                    name="Send"
                )

                send_button.wait_for(timeout=10000)
                send_button.click()

                # Verify message box cleared
                page.wait_for_function("""
                    () => {
                        const box = document.querySelector(
                            '[contenteditable="true"][role="textbox"]'
                        );

                        return box && box.innerText.trim() === "";
                    }
                """, timeout=10000)

                print("\nMessage submitted successfully!")

            else:

                print("\nMessage sending skipped.")

            # 6. Extract chat information
            print("\n--- EXTRACTING CHAT INFORMATION ---")

            messages = page.locator(
                "#main .message-in, #main .message-out"
            )

            # Wait for chat messages
            messages.first.wait_for(timeout=15000)

            message_data = messages.evaluate_all("""
                elements => elements.map(el => {

                    const textElement = el.querySelector(
                        '.selectable-text'
                    );

                    const timeElement = el.querySelector(
                        '[data-pre-plain-text]'
                    );

                    return {
                        sender: el.classList.contains('message-out')
                            ? 'You'
                            : 'Contact',

                        message: textElement
                            ? textElement.innerText
                            : '',

                        timestamp: timeElement
                            ? timeElement.getAttribute(
                                'data-pre-plain-text'
                            )
                            : ''
                    };
                })
            """)

            # 7. Print extracted messages
            for item in message_data:
                print(item)

            # 8. Save extracted messages to CSV
            with open(
                "extracted_chats.csv",
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "sender",
                        "message",
                        "timestamp"
                    ]
                )

                writer.writeheader()
                writer.writerows(message_data)

            print("\nChat data saved successfully!")

            # 9. Save screenshot
            page.screenshot(
                path="whatsapp_final.png",
                full_page=True
            )

            print("Screenshot saved: whatsapp_final.png")

        except TimeoutError as error:

            print("\nAutomation timeout:", error)

            page.screenshot(
                path="whatsapp_error.png"
            )

        except Exception as error:

            print("\nUnexpected error:", error)

        finally:

            context.close()

            print("\nWhatsApp automation completed.")


if __name__ == "__main__":
    whatsapp_automation()

