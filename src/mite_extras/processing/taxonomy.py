"""Retrieval of human-readable taxonomy information for NCBI Taxonomy IDs.

Copyright (c) 2024 to present Mitja Maximilian Zdouc, PhD and Adriano
Rutz (0000-0003-0443-9902) and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging

import requests

logger = logging.getLogger("mite_extras")

TIMEOUT = 2
FALLBACK = "could not retrieve"
RANKS = [
    "domain",
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "species",
    "strain",
]


def get_taxonomy(taxid: str) -> dict:
    """Translate an NCBI Taxonomy ID into its lineage via the UniProt API

    Arguments:
        taxid: an NCBI Taxonomy ID, e.g. "1883"

    Returns:
        A dict with organism name and ranks (domain to strain);
        missing ranks are omitted, all values are FALLBACK if the call fails
    """
    try:
        response = requests.get(
            f"https://rest.uniprot.org/taxonomy/{taxid}.json",
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        taxdata = response.json()
    except Exception as retrieveerror:
        logger.warning(f"Could not retrieve taxonomy for taxid {taxid}: {retrieveerror!s}")
        return {"organism": FALLBACK} | dict.fromkeys(RANKS, FALLBACK)

    found = {}

    for element in [*taxdata.get("lineage", []), taxdata]:
        rank = element.get("rank")
        if rank == "superkingdom":
            rank = "domain"
        if rank in RANKS:
            found[rank] = element.get("scientificName")

    taxonomy = {"organism": taxdata.get("scientificName", FALLBACK)}
    for rank in RANKS:
        if rank in found:
            taxonomy[rank] = found[rank]
    return taxonomy

