import subprocess
from typing import Dict, NamedTuple
from json import loads

class SubprocResult(NamedTuple):
    return_code: int
    output: str
    error: str


def ffprobe(path: str) -> SubprocResult:
    cmd = ["ffprobe",
           "-v", "quiet",
           "-print_format", "json",
           "-show_format",
           "-show_streams",
           path]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    return SubprocResult(return_code=result.returncode,
                         output=result.stdout,
                         error=result.stderr)

def get_data(path: str) -> Dict:
    result: dict = loads(ffprobe(path).output).get('format', {})
    result.update(result.pop('tags', {}))
    return result
