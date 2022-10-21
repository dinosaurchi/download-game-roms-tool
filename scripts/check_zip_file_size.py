import os
import pathlib
import traceback
import zipfile
import glob
import sys


def get_uncompressed_size(zip_file_path: str) -> int:
    zp = zipfile.ZipFile(zip_file_path)
    size = sum([zinfo.file_size for zinfo in zp.filelist])
    return size


def get_file_size(f_path:str) -> float:
    return os.path.getsize(f_path)


def bytes_to_gb(bytes_value:int) -> float:
    return round(bytes_value / (1024 ** 3), 2)


if __name__ == "__main__":
    roms_dir = sys.argv[1]

    f_paths = glob.glob(f"{roms_dir}/*.zip")

    total_size = 0
    uncompressed_total_size = 0
    for f_path in f_paths:
        try:
            f_name = pathlib.Path(f_path).name
            uncompressed_size = get_uncompressed_size(zip_file_path=f_path)
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue

        uncompressed_total_size += uncompressed_size

        zip_file_size = get_file_size(f_path=f_path)
        total_size += zip_file_size

        uncompressed_size_gb = bytes_to_gb(uncompressed_size)
        zip_file_size_gb = bytes_to_gb(zip_file_size)
        print(f"[{uncompressed_size_gb}GB / {zip_file_size_gb}GB] \t {f_name}")

    print("")

    total_uncompressed_size_gb = bytes_to_gb(uncompressed_total_size)
    print(f"Uncompressed total: {total_uncompressed_size_gb} GB")

    total_size_gb = bytes_to_gb(total_size)
    print(f"Total: {total_size_gb} GB")
        