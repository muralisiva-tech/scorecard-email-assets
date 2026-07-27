import shutil
import subprocess
from pathlib import Path
from datetime import date, timedelta
import tkinter as tk
from tkinter import filedialog

# =====================================================
# CONFIGURATION
# =====================================================

BRANCH_NAME = "main"

# Script must be placed in the Git repository root
REPO_ROOT = Path(__file__).parent

SOURCE_ROOT = None

# =====================================================
# SELECT SOURCE FOLDER
# =====================================================

def select_source_folder():

    root = tk.Tk()
    root.withdraw()

    folder = filedialog.askdirectory(
        title="Select Folder Containing SL GIF Folders"
    )

    if not folder:
        raise Exception("No source folder selected.")

    return Path(folder)

# =====================================================
# PREVIOUS MONTH CALCULATION
# =====================================================

def get_previous_month_folder():

    today = date.today()

    first_day_current_month = today.replace(day=1)

    previous_month_date = (
        first_day_current_month -
        timedelta(days=1)
    )

    year_folder = str(
        previous_month_date.year
    )

    month_folder = previous_month_date.strftime(
        "%b"
    )

    return year_folder, month_folder

# =====================================================
# VALIDATION
# =====================================================

def validate_paths():

    if not SOURCE_ROOT.exists():
        raise Exception(
            f"Source folder not found:\n{SOURCE_ROOT}"
        )

    if not (REPO_ROOT / ".git").exists():
        raise Exception(
            f"\nThe script must be placed in the "
            f"scorecard-email-assets repository root.\n\n"
            f"Current location:\n{REPO_ROOT}"
        )

# =====================================================
# GIT
# =====================================================

def run_git(command):

    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        shell=True,
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise Exception(
            f"\nGit command failed:\n{command}"
        )

# =====================================================
# COPY GIF FILES
# =====================================================

def upload_gifs():

    year_folder, month_folder = (
        get_previous_month_folder()
    )

    uploaded_count = 0

    print("\n====================================")
    print("UPLOAD INFORMATION")
    print("====================================")
    print(f"Year  : {year_folder}")
    print(f"Month : {month_folder}")
    print("====================================")

    for sl_folder in SOURCE_ROOT.iterdir():

        if not sl_folder.is_dir():
            continue

        sl_name = sl_folder.name

        print(f"\nProcessing: {sl_name}")

        repo_sl_folder = (
            REPO_ROOT /
            year_folder /
            sl_name
        )

        if not repo_sl_folder.exists():

            print(
                f"Repository folder missing. Skipping: {sl_name}"
            )

            continue

        target_folder = (
            REPO_ROOT /
            year_folder /
            sl_name /
            month_folder
        )

        target_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        gif_files = list(
            sl_folder.glob("*.gif")
        )

        if not gif_files:

            print("No GIF files found")
            continue

        for gif_file in gif_files:

            destination = (
                target_folder /
                gif_file.name
            )

            # Always overwrite
            shutil.copy2(
                gif_file,
                destination
            )

            uploaded_count += 1

            print(
                f"Uploaded/Updated: {gif_file.name}"
            )

    return uploaded_count, year_folder, month_folder

# =====================================================
# GIT PUSH
# =====================================================

def commit_and_push(
    uploaded_count,
    year_folder,
    month_folder
):

    if uploaded_count == 0:

        print(
            "\nNo GIF files found to upload."
        )

        return

    run_git(
        f"git checkout {BRANCH_NAME}"
    )

    run_git(
        f"git pull origin {BRANCH_NAME}"
    )

    run_git(
        "git add ."
    )

    commit_message = (
        f"Upload GIF assets "
        f"{month_folder} {year_folder}"
    )

    result = subprocess.run(
        f'git commit -m "{commit_message}"',
        cwd=REPO_ROOT,
        shell=True,
        text=True,
        capture_output=True
    )

    print(result.stdout)

    if "nothing to commit" in result.stdout.lower():

        print(
            "\nFiles already match repository."
        )

        return

    run_git(
        f"git push origin {BRANCH_NAME}"
    )

    print("\n====================================")
    print("SUCCESS")
    print("====================================")
    print(
        f"{uploaded_count} GIF file(s) uploaded."
    )

# =====================================================
# MAIN
# =====================================================

def main():

    global SOURCE_ROOT

    try:

        print(
            "\nSelect GIF Upload Folder..."
        )

        SOURCE_ROOT = (
            select_source_folder()
        )

        print(
            f"\nSelected Folder:\n{SOURCE_ROOT}"
        )

        print(
            f"\nRepository:\n{REPO_ROOT}"
        )

        validate_paths()

        uploaded_count, year_folder, month_folder = (
            upload_gifs()
        )

        commit_and_push(
            uploaded_count,
            year_folder,
            month_folder
        )

    except Exception as ex:

        print("\nERROR")
        print(str(ex))

    input(
        "\nPress Enter to exit..."
    )

if __name__ == "__main__":
    main()