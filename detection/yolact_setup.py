import pathlib
import subprocess
import sys

yolact_github_uri = "https://github.com/dbolya/yolact.git"

file_dir   = pathlib.Path(__file__).parent.absolute()
yolact_dir = pathlib.Path.joinpath(file_dir, "yolact")

if not yolact_dir.exists():
    p = subprocess.Popen(["git", "clone", yolact_github_uri], cwd=file_dir)
    p.wait()

sys.exit(int(not yolact_dir.exists()))
