import urllib.request
import urllib.parse
import json
import sys
import os


def promote_user():
    print("--- Flowtab.Pro User Promotion Tool ---")
    print("This tool promotes a registered user to Superuser (Admin).")

    # Get configuration
    base_url = (
        input("Enter API URL (e.g. https://api.flowtab.pro or http://localhost:8000): ")
        .strip()
        .rstrip("/")
    )
    if not base_url:
        print("URL is required.")
        return

    admin_key = input("Enter ADMIN_KEY (from Render environment variables): ").strip()
    if not admin_key:
        print("Admin Key is required.")
        return

    email = input("Enter the email of the user to promote: ").strip()
    if not email:
        print("Email is required.")
        return

    # Prepare request
    url = f"{base_url}/v1/users/promote?email={urllib.parse.quote(email)}"
    headers = {"X-Admin-Key": admin_key, "Content-Type": "application/json"}

    try:
        # Create request (POST)
        req = urllib.request.Request(url, method="POST", headers=headers)

        # Execute
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"\nSUCCESS: User '{email}' is now a superuser.")
                print("They can now see the 'Delete' button on prompt pages.")
            else:
                print(f"\nUnexpected status: {response.status}")

    except urllib.error.HTTPError as e:
        print(f"\nError: Server returned status {e.code}")
        try:
            error_body = e.read().decode()
            print(f"Details: {error_body}")
        except:
            pass

        if e.code == 404:
            print(f"Hint: User '{email}' might not exist. Have they registered yet?")
        elif e.code == 401:
            print("Hint: Check your ADMIN_KEY.")
        elif e.code == 403:
            print("Hint: Server might not have an ADMIN_KEY configured.")

    except urllib.error.URLError as e:
        print(f"\nError connecting to server: {e.reason}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    try:
        promote_user()
    except KeyboardInterrupt:
        print("\nExiting...")
