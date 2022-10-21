from collections import defaultdict
import glob
import os
import pathlib
import sys
import shutil
from typing import List
import zipfile
import tqdm


def get_uncompressed_size(zip_file_path: str) -> int:
    zp = zipfile.ZipFile(zip_file_path)
    size = sum([zinfo.file_size for zinfo in zp.filelist])
    return size


def get_single_zip_file_name(zip_file_path: str) -> str:
    zp = zipfile.ZipFile(zip_file_path)
    f_names = [zinfo.filename for zinfo in zp.filelist]
    if len(f_names) != 1:
        raise Exception(f"Unique zip file must has only one file name: {f_names}")


def get_file_size(f_path:str) -> int:
    return os.path.getsize(f_path)


def unzip_to_dir(zip_file_path: str, output_dir: str) -> None:
    shutil.unpack_archive(filename=str(zip_file_path), extract_dir=str(output_dir))


def log_to_done(status_path:str, f_path:str) -> None:
    with open(status_path, "a+") as f:
        f.write(str(pathlib.Path(f_path).name) + "\n")


def filter_out_done_names(status_path:str, f_paths:List[str]) -> List[str]:
    if not pathlib.Path(status_path).exists():
        return list(f_paths)

    with open(status_path, "r") as f:
        data = f.read()
        done_names = data.split("\n")
        done_names = [f_name.strip("\n\r\t ") for f_name in done_names]
        done_names = [f_name for f_name in done_names if len(f_name) > 0]

    print(f"There are {len(done_names)} done names")
    done_names = set(done_names)
    f_paths = [f_path for f_path in f_paths if not pathlib.Path(f_path).name in done_names]
    print(f"There are {len(f_paths)} pending paths")
    return f_paths


if __name__ == "__main__":
    zip_roms_dir = sys.argv[1]
    output_dir = sys.argv[2]
    zip_file_paths = glob.glob(f"{zip_roms_dir}/*.zip")

    state_dir = pathlib.Path(".", ".state")
    os.makedirs(str(state_dir), exist_ok=True)
    status_path = str(state_dir.joinpath("copy_extract_zip_done_status.txt"))

    zip_file_paths = filter_out_done_names(status_path=status_path, f_paths=zip_file_paths)

    size_map = defaultdict(lambda: {})
    for f_path in tqdm.tqdm(zip_file_paths, "Processing size"):
        size_map[f_path] = {
            "uncompressed": get_uncompressed_size(zip_file_path=f_path),
            "zip": get_file_size(f_path=f_path)
        }
    print("")

    zip_file_paths = sorted(zip_file_paths, key=lambda x: size_map[x]["uncompressed"])

    for i, f_path in enumerate(zip_file_paths):
        uncompressed_size = get_uncompressed_size(zip_file_path=f_path)
        zip_size = get_file_size(f_path=f_path)
        print(f"Processing [{i+1}/{len(zip_file_paths)}] {f_path}")
        print(f" - Extract to        :{output_dir}")
        print(f" - Uncompressed size : {round(uncompressed_size/1024**3, 2)}")
        print(f" - Zip size          : {round(zip_size/1024**3, 2)}")

        unzip_to_dir(zip_file_path=f_path, output_dir=output_dir)
        log_to_done(status_path=status_path, f_path=f_path)

        print("Done")
        print("")
