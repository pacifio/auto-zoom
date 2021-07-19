import os
import time
import schedule
import pyautogui as auto
from datetime import datetime
from sys import platform as platform
import subprocess
import getpass
import shelve

DELAY = 10
LIST = "meetings.txt"


# Ask to save crendentials
def save_prompt():
    save = str(input("Save(y/n) >> "))
    if save in ["y", "n"]:
        if save == "y":
            with shelve.open("keys") as db:
                db['mid'] = mid
                db['username'] = username
                db['password'] = password
            print("Saved credentials")
    else:
        print("Please choose a valid option")
        save_prompt()


# Ask for user credentials
def prompt():
    global mid
    global username
    global password

    if os.path.exists("keys"):
        with shelve.open("keys") as db:
            mid = str(db.get("mid"))
            username = str(db.get("username"))
            password = str(db.get("password"))
    else:
        mid = str(input("Meeting ID >> "))
        username = str(input("Username >> "))
        password = str(getpass.getpass("Password >> "))

        save_prompt()

    scheduler()


# Check if zoom is running
def process_exists():
    if platform == "linux" or platform == "linux2":
        return False
    else:
        if platform == "darwin":
            command = subprocess.Popen(
                "ps -eaf | grep zoom", shell=True, stdout=subprocess.PIPE)
            progs = str(command.stdout.read())
            command.stdout.close()
            command.wait()
        elif platform == "win32":
            progs = str(subprocess.check_output("tasklist"))
        else:
            progs = ""
        if "zoom" in progs:
            return True
        else:
            return False


# Opens zoom app
# Only macOS and Windows supported
def open_app():
    if platform == "linux" or platform == "linux2":
        pass
    elif platform == "darwin":
        path = "/Applications/zoom.us.app"
        os.system(f"open {path}")
    elif platform == "win32":
        os.startfile("C:\\myprogram.exe")
    else:
        print("platform not supported")
        exit(0)


# Initiate automation
def automation():
    now = datetime.today().now()
    print(f'Loggin in at {now}')

    open_app()

    if process_exists():
        print(f"Waiting {DELAY} seconds until finalising connection")
        time.sleep(DELAY)

        join_btn = auto.locateCenterOnScreen('btn.png')

        if platform == "darwin":
            # Retina displays have twice the pixels as normal screens
            auto.moveTo(join_btn.x/2, join_btn.y/2)
        else:
            auto.moveTo(join_btn.x, join_btn.y)
        auto.click()

        auto.typewrite(mid.strip())
        if 'tab' in auto.KEY_NAMES:
            auto.press('tab')
            auto.press('tab')
            auto.typewrite(username.strip())

            auto.press('tab')
            auto.press('space')
            auto.press('tab')
            auto.press('space')

            auto.press('tab')
            auto.press('tab')
            auto.press('space')

            print(f"Waiting {DELAY} seconds until finalising connection")
            time.sleep(DELAY)

            auto.typewrite(password.strip())

            auto.press('tab')
            auto.press('tab')
            auto.press('space')

            print("Waiting for next meeting")
            print("If no meetings are left , Press Ctrl+C to quit")

    else:
        print("Could not load zoom")
        exit(0)


# Schedule
# mettings.txt file must be present to scheduler
# Or else meeting will auto start
def scheduler():
    if os.path.exists('meetings.txt'):
        with open('meetings.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                for t in lines:
                    print(f"Scheduled for {t.strip()}")
                    schedule.every().day.at(t.strip()).do(automation)
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            else:
                print(
                    "meetings.txt was empty or corrupted , starting zoom meeting anyway")
                automation()

    else:
        print("Could not find meetings.txt , starting zoom meeting anyway")
        automation()


if __name__ == "__main__":
    try:
        prompt()
    except:
        print("Execution failed")
        exit(0)
