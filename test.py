import os

# Path to your project folder
project_path = r"D:\Documents\Personal\coding\newsletter bot"

# Output file
output_file = r"D:\Documents\Personal\coding\newsletter_bot_all_code.txt"

with open(output_file, "w", encoding="utf-8") as out_f:
    for root, dirs, files in os.walk(project_path):
        # Skip venv and __pycache__ folders
        if "venv" in root or "__pycache__" in root:
            continue

        # Sort files for consistency
        files = sorted(files)

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Write a header for each file
                out_f.write(f"\n\n# --- {file_path} ---\n\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    out_f.write(f.read())
