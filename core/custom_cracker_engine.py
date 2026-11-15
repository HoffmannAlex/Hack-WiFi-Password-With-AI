#!/usr/bin/env python3
"""
Thin wrapper exposing the custom WPA2 cracking backend as a class
compatible with potential existing interfaces.
"""

from typing import List, Optional

# Import the parallel cracking function
from .custom_cracker_parallel import crack_with_backend_parallel

class CustomCrackEngine:
    """Engine providing a ``crack_handshake`` method.

    The method signature mirrors the typical pattern used in the original
    project (e.g., ``self.cracker.crack_handshake(capture_file, wordlist_file, ssid)``).
    It loads the wordlist, runs the parallel backend, and returns the found
    password or ``None``.
    """

    def crack_handshake(self, capture_file: str, wordlist_file: str, ssid: str) -> Optional[str]:
        """Crack a WPA/WPA2 handshake using the parallel backend.

        Parameters
        ----------
        capture_file: str
            Path to the ``.pcap``/``.cap`` file containing the handshake.
        wordlist_file: str
            Path to a text file with one candidate password per line.
        ssid: str
            SSID of the target network.
        """
        # Load the wordlist
        with open(wordlist_file, "r", encoding="utf-8") as f:
            candidates: List[str] = [line.rstrip("\n") for line in f if line.strip()]
        # Run the parallel cracker
        return crack_with_backend_parallel(ssid, capture_file, candidates)

