import RNS
import time
from pathlib import Path
from hashlib import sha256


class Node:
    def __init__(self, identity, directory):
        self.identity = identity
        self.directory = Path(directory)
        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            "rfs",
            "node",
        )
        self.destination.register_request_handler(
            "/ask",
            response_generator=self._ask_generator,
            allow=RNS.Destination.ALLOW_ALL,
        )
        self.destination.register_request_handler(
            "/get",
            response_generator=self._get_generator,
            allow=RNS.Destination.ALLOW_ALL,
        )

    def _ask_generator(
        self, path, data, request_id, link_id, remote_identity, requested_at
    ):
        return self.ask_local(data)

    def _get_generator(
        self, path, data, request_id, link_id, remote_identity, requested_at
    ):
        if self.ask_local(data):
            return self.get_local(data)
        return b""

    def put(self, data: bytes):
        digest = sha256(data).digest()
        self.directory.joinpath(digest.hex()).write_bytes(data)
        return digest

    def ask_local(self, digest: bytes):
        return self.directory.joinpath(digest.hex()).exists()

    def get_local(self, digest: bytes):
        return self.directory.joinpath(digest.hex()).read_bytes()

    def get(self, digest: bytes, destinations: list[RNS.Destination] = []):
        # local
        if self.ask_local(digest):
            return self.get_local(digest)
        # remote
        for d in destinations:
            link = RNS.Link(d)
            while link.status != RNS.Link.ACTIVE:
                time.sleep(0.1)
            if self.ask_remote(digest, link):
                try:
                    return self.get_remote(digest, link)
                except FileNotFoundError:
                    pass
        raise FileNotFoundError()

    def ask_remote(self, digest, link: RNS.Link):
        data = link.request("/ask", digest)
        while not data.concluded():
            time.sleep(0.1)
        if data.get_status() == RNS.RequestReceipt.READY:
            return data.get_response()
        return False

    def get_remote(self, digest, link: RNS.Link):
        data = link.request("/get", digest)
        while not data.concluded():
            time.sleep(0.1)
        if data.get_status() == RNS.RequestReceipt.READY:
            data = data.get_response()
            if self.verify(digest, data):
                self.put(data)
                return data
        raise FileNotFoundError()

    @staticmethod
    def verify(digest: bytes, data: bytes):
        if digest == sha256(data).digest():
            return True
        return False

    def announce(self):
        self.destination.announce()
