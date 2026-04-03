# RFS
reticulum file system, A minimalist decentralized file system on RNS
## Usage
RFS can be used as a library, or you can enter an interactive interpreter using `python -m RFS`.

In the interactive interpreter, you can manipulate node objects, for example
```
# f=open(r"LICENSE",'rb')
# node.put(f.read())
t=node.put(b'hello world!')
t.hex()
node.verify(t,b'hello world!')
node.ask_local(t)
node.get_local(t)
```
Additionally, `__main__.py` includes a built-in expanding ring search, and you can use `node.get(t,ers())` to try retrieving remote files.

Nodes do not announce themselves by default. You can use the following methods:
```
import time
while True:
    node.announce()
    time.sleep(60*60)
```
announce itself.

For more information, please refer to `Node.py` and `__main__.py`.
## System Design
Each node exposes only two endpoints: `/ask` and `/get`, used to verify file existence and retrieve files. There is no synchronization or DHT. You are free to implement your own search algorithms and extend node capabilities as needed.

The system is completely content-agnostic; all files are treated as raw bytes. It does not include a built-in chunking mechanism, but I strongly recommend keeping individual files under 16 MB. For larger files, please handle chunking/splitting on your own.
