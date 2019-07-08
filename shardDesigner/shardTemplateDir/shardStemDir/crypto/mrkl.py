from hashlib import blake2b

class VncTree:
    @staticmethod
    def hash(data) -> str:
        h = blake2b(digest_size = 32)
        if isinstance(data, str):
            h.update(data.encode('utf-8'))
        if isinstance(data, bytes):
            h.update(data)
        if isinstance(data, dict):
            h.update(str(data).encode('utf-8'))

        return h.hexdigest()

    @staticmethod
    def hash_each(data: list):
        return [VncTree.hash(x) for x in data]

    @staticmethod
    def hash_list(data: tuple) -> str:
        return VncTree.hash(''.join((str(x) for x in data)))

    @staticmethod
    def __concat_pairs(data: list) -> list:
        result = list()
        if not data:
            return list()
        it = iter(data)
        while True:
            x = str()
            y = str()
            try:
                x = next(it)
            except StopIteration:
                pass
            try:
                y = next(it)
            except StopIteration:
                pass
            if not x:
                break
            if not y:
                y = x
                result.append(VncTree.hash(x + y))
                break
            result.append(VncTree.hash(x + y))
        return result

    @staticmethod
    def create_tree(data: list) -> list:
        result = list()
        if not data:
            return []
        while True:
            tmp = VncTree.__concat_pairs(data)
            result.append(tmp)
            data = tmp
            if len(tmp) == 1:
                break
        return result

    @staticmethod
    def create(data: list) -> tuple:
        hashes = VncTree.hash_each(data)
        hashes.sort()
        tree = VncTree.create_tree(hashes)
        root = str()
        if tree:
            root = tree.pop()
        return tree, root
