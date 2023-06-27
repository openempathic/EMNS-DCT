import tarfile
import glob

def extract_files_with_extension(archive_path, target_directory, file_extension:tuple):
    with tarfile.open(archive_path, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith(file_extension):
                tar.extract(member, path=target_directory)

def main():
    for path in glob.glob("/home/knoriy/EMNS-data/**/*.tar", recursive=True):
        print(path)
        extract_files_with_extension(path, '/home/knoriy/EMNS-DCT/django_dataset_collection_tool/media', file_extension=("flac", 'json'))
        break


if __name__ == '__main__':
    main()