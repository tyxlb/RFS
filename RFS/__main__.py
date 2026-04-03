if __name__ == "__main__":
    from .Node import Node
    from .AnnounceHandler import AnnounceHandler
    import RNS
    import argparse
    from pathlib import Path
    import code

    RNS.Reticulum()

    parser = argparse.ArgumentParser(description="reticulum file system")
    parser.add_argument("--identity", default="./identity")
    parser.add_argument("--directory", default="./directory")
    args = parser.parse_args()

    if Path(args.identity).is_file():
        identity = RNS.Identity.from_file(args.identity)
    else:
        identity = RNS.Identity()
        identity.to_file(args.identity)
    Path(args.directory).mkdir(parents=True, exist_ok=True)

    node = Node(identity=identity, directory=args.directory)
    announce_handler = AnnounceHandler("rfs.node")
    RNS.Transport.register_announce_handler(announce_handler)

    def ers():
        "expanding_ring_search"
        ds = [
            RNS.Destination(
                announce_handler.known_destination_hash[d],
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                "rfs",
                "node",
            )
            for d in announce_handler.known_destination_hash
        ]
        return sorted(ds, key=lambda d: RNS.Transport.hops_to(d))[:16]

    code.interact(
        banner="node: Node, ers() -> list, node.get(digest,ers())", local=locals()
    )
