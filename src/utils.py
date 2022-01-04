from pathlib import Path

def create_folders(dirs:list):
    for dir in dirs:
        Path(dir).mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    dirs = ["data/wavs", "data/other_folder"]
    create_folders(dirs)
