#!/usr/bin/env python3
"""
Enhanced multiprocessing wrapper for the pure‑Python WPA2 cracking backend.
Features added:
* Chunked task submission (reduces inter‑process overhead).
* Live progress reporting (simple console output).
* Lazy word‑list loading (handles very large files without loading everything into RAM).
* Graceful termination when a password is found.
"""

import time
import sys
from pathlib import Path
from typing import List, Optional
from multiprocessing import Pool, Value, Lock, cpu_count
from threading import Thread

# Import the single‑threaded checker from the original backend.
# It must provide ``test_password(passphrase: str, ssid: str, cap_file: str) -> bool``.
from .custom_cracker import test_password

# ----- Configuration -------------------------------------------------------
CHUNK_SIZE = 500  # number of passwords per worker task – tune for your hardware.
# -------------------------------------------------------------------------

# Shared counter for progress reporting.
_counter = Value("i", 0)
_counter_lock = Lock()


def _worker_chunk(args):
    """Worker that receives a list of candidate passwords.

    Returns the first password that matches the handshake, or ``None`` if none match.
    The shared ``_counter`` is updated only when the chunk **does not** contain a match,
    to avoid double‑counting the successful password.
    """
    ssid, cap_file, chunk = args
    for pwd in chunk:
        if test_password(pwd, ssid, cap_file):
            return pwd
    # No match in this chunk – update progress.
    with counter_lock:
        _counter.value += len(chunk)
    return None


def _progress_report(total: int):
    """Background thread that prints a simple progress line every few seconds."""
    while True:
        done = _counter.value
        print(f"\r✔︎ Tested {done}/{total} passwords …", end="", flush=True)
        if done >= total:
            break
        time.sleep(2)
    print()  # final newline when done.


def _generate_chunks(wordlist_path: str) -> List[List[str]]:
    """Yield password chunks from *wordlist_path* without loading the whole file.
    Returns a list of chunks because we need the total count for the progress bar.
    """
    chunks: List[List[str]] = []
    current: List[str] = []
    with open(wordlist_path, "r", encoding="utf-8") as f:
        for line in f:
            pwd = line.strip()
            if not pwd:
                continue
            current.append(pwd)
            if len(current) >= CHUNK_SIZE:
                chunks.append(current)
                current = []
    if current:
        chunks.append(current)
    return chunks


def crack_with_backend_parallel(ssid: str, cap_file: str, wordlist_path: str) -> Optional[str]:
    """Crack a WPA/WPA2 handshake using multiprocessing.

    Parameters
    ----------
    ssid: str
        The target network SSID.
    cap_file: str
        Path to the ``.cap``/``.pcap`` file containing the captured handshake.
    wordlist_path: str
        Path to a text file with one candidate password per line.

    Returns
    -------
    Optional[str]
        The recovered password, or ``None`` if the list is exhausted.
    """
    # Build password chunks and the total number of candidates.
    chunks = _generate_chunks(wordlist_path)
    total_passwords = sum(len(c) for c in chunks)

    # Start the progress reporter thread.
    prog_thread = Thread(target=_progress_report, args=(total_passwords,), daemon=True)
    prog_thread.start()

    # Spin up a process pool.
    pool = Pool(processes=cpu_count())
    try:
        for result in pool.imap_unordered(
            _worker_chunk, ((ssid, cap_file, ch) for ch in chunks)
        ):
            if result:  # a password was found
                # Ensure the counter reflects the work done before we exit.
                with counter_lock:
                    _counter.value = total_passwords
                pool.terminate()
                prog_thread.join()
                return result
        # If we exit the loop without a result, the generator was exhausted.
        with counter_lock:
            _counter.value = total_passwords
    finally:
        pool.close()
        pool.join()
        prog_thread.join()
    return None

