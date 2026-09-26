"""
dns_tracer.packet
=================
Builds raw DNS query packets in wire format (RFC 1035).

No external dependencies — pure struct.pack and byte manipulation.

Wire format:
  ┌─────────────────────────┐
  │  Header  (12 bytes)     │
  ├─────────────────────────┤
  │  Question section       │
  └─────────────────────────┘

Header (12 bytes):
  ID       (2 bytes)  - transaction identifier
  FLAGS    (2 bytes)  - QR|OPCODE|AA|TC|RD|RA|Z|RCODE
  QDCOUNT  (2 bytes)  - number of questions
  ANCOUNT  (2 bytes)  - number of answers (0 in query)
  NSCOUNT  (2 bytes)  - number of authority RRs (0 in query)
  ARCOUNT  (2 bytes)  - number of additional RRs (0 in query)

Question section:
  QNAME    (variable) - domain encoded as length-prefixed labels
  QTYPE    (2 bytes)  - record type
  QCLASS   (2 bytes)  - IN = 1
"""

import os
import struct

# ─── Record type codes ────────────────────────────────────────────────────────

QTYPES: dict[str, int] = {
    "A":     1,
    "NS":    2,
    "CNAME": 5,
    "SOA":   6,
    "MX":    15,
    "AAAA":  28,
    "ANY":   255,
}

QTYPE_NAMES: dict[int, str] = {v: k for k, v in QTYPES.items()}

QCLASS_IN = 1  # Internet


# ─── Header flags ─────────────────────────────────────────────────────────────

def _build_flags(recursion_desired: bool = True) -> int:
    """
    Build the 16-bit flags word for a standard query.

    Bit layout (MSB → LSB):
      QR(1) OPCODE(4) AA(1) TC(1) RD(1) | RA(1) Z(3) RCODE(4)

    For a query: QR=0, OPCODE=0 (standard), AA=0, TC=0, RD=<arg>,
                 RA=0, Z=0, RCODE=0
    """
    rd_bit = 1 if recursion_desired else 0
    return rd_bit << 8  # only RD bit set in low byte


# ─── QNAME encoding ───────────────────────────────────────────────────────────

def encode_qname(domain: str) -> bytes:
    """
    Encode a domain name as DNS wire-format labels.

    "google.com" → b'\x06google\x03com\x00'

    Each label is prefixed with its length as a single byte.
    Terminated by a zero-length octet (root label).
    """
    parts = domain.rstrip(".").split(".")
    encoded = b""
    for label in parts:
        label_bytes = label.encode("ascii")
        if len(label_bytes) > 63:
            raise ValueError(f"DNS label too long (max 63): '{label}'")
        encoded += bytes([len(label_bytes)]) + label_bytes
    encoded += b"\x00"  # root label
    return encoded


# ─── Full packet builder ───────────────────────────────────────────────────────

def build_query(
    domain: str,
    qtype: str = "A",
    transaction_id: int | None = None,
    recursion_desired: bool = True,
) -> tuple[bytes, int]:
    """
    Build a complete DNS query packet.

    Returns:
        (packet_bytes, transaction_id)

    Args:
        domain:            Domain name to query (e.g. "google.com")
        qtype:             Record type string (A, AAAA, NS, MX, CNAME)
        transaction_id:    16-bit ID; random if None
        recursion_desired: Whether to set the RD bit (default True)
    """
    if transaction_id is None:
        transaction_id = int.from_bytes(os.urandom(2), "big")

    qtype_code = QTYPES.get(qtype.upper())
    if qtype_code is None:
        raise ValueError(f"Unknown query type: '{qtype}'. Valid: {list(QTYPES)}")

    flags = _build_flags(recursion_desired)

    # Header: ID FLAGS QDCOUNT ANCOUNT NSCOUNT ARCOUNT
    header = struct.pack(
        "!HHHHHH",
        transaction_id & 0xFFFF,
        flags,
        1,  # QDCOUNT = 1 question
        0,  # ANCOUNT
        0,  # NSCOUNT
        0,  # ARCOUNT
    )

    question = encode_qname(domain) + struct.pack("!HH", qtype_code, QCLASS_IN)

    return header + question, transaction_id
