class AnnounceHandler:
    def __init__(self, aspect_filter):
        self.aspect_filter = aspect_filter
        self.known_destination_hash = {}

    def received_announce(self, destination_hash, announced_identity, app_data):
        if destination_hash not in self.known_destination_hash:
            self.known_destination_hash[destination_hash] = announced_identity
