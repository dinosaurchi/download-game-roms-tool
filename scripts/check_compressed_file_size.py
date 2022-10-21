import os
import pathlib
import traceback
import zipfile
import glob
import sys
import py7zr


def get_uncompressed_size(compressed_file_path: str) -> int:
    if compressed_file_path.endswith(".zip"):
        zp = zipfile.ZipFile(compressed_file_path)
        size = sum([zinfo.file_size for zinfo in zp.filelist])
        zp.close()
        return size
    elif compressed_file_path.endswith(".7z"):
        print(compressed_file_path)
        with py7zr.SevenZipFile(compressed_file_path, 'r') as archive:
            size = sum([info.uncompressed for info in archive.list()])
            return size

    raise Exception(f"Unsupported file extension: ${compressed_file_path}")


def get_file_size(f_path:str) -> float:
    return os.path.getsize(f_path)


def bytes_to_gb(bytes_value:int) -> float:
    return round(bytes_value / (1024 ** 3), 2)


if __name__ == "__main__":
    roms_dir = sys.argv[1]

    f_paths = glob.glob(f"{roms_dir}/*.zip")
    f_paths.extend(glob.glob(f"{roms_dir}/*.7z"))

    total_size = 0
    uncompressed_total_size = 0
    for i, f_path in enumerate(f_paths):
        try:
            f_name = pathlib.Path(f_path).name
            uncompressed_size = get_uncompressed_size(compressed_file_path=f_path)
        except Exception as e:
            traceback.print_exc()
            print(e)
            continue

        uncompressed_total_size += uncompressed_size

        compressed_file_size = get_file_size(f_path=f_path)
        total_size += compressed_file_size

        uncompressed_size_gb = bytes_to_gb(uncompressed_size)
        compressed_file_size_gb = bytes_to_gb(compressed_file_size)
        print(f"[{i}/{len(f_paths)}] [{uncompressed_size_gb}GB / {compressed_file_size_gb}GB] \t {f_name}")

    print("")

    total_uncompressed_size_gb = bytes_to_gb(uncompressed_total_size)
    print(f"Uncompressed total: {total_uncompressed_size_gb} GB")

    total_size_gb = bytes_to_gb(total_size)
    print(f"Total: {total_size_gb} GB")
        