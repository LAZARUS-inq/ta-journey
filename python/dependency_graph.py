"""
dependency_graph.py — DCC-agnostic asset dependency graph.

Used by asset_dependency_checker.py (UE5). No Unreal / pymxs imports, so the
same analysis can be unit-tested and the report shape stays stable.
"""

from collections import Counter, defaultdict


ROOT_CLASSES_DEFAULT = (
    "World",
    "WorldPartition",
    "Level",
    "LevelSequence",
    "MapBuildDataRegistry",
    "ExternalDataLayerAsset",
)


class DependencyGraph:
    def __init__(self, root_classes=ROOT_CLASSES_DEFAULT):
        self.root_classes = tuple(root_classes)
        self.nodes = {}
        self._out = defaultdict(list)
        self._in = defaultdict(list)

    def add_node(self, package, name="", asset_class="", path=""):
        if package in self.nodes:
            node = self.nodes[package]
            if name:
                node["name"] = name
            if asset_class:
                node["class"] = asset_class
            if path:
                node["path"] = path
            return
        self.nodes[package] = {
            "package": package,
            "name": name or package.rsplit("/", 1)[-1],
            "class": asset_class,
            "path": path or package,
        }

    def add_edge(self, src, dst, kind="hard"):
        if not src or not dst or src == dst:
            return
        edge = (dst, kind)
        if edge in self._out[src]:
            return
        self._out[src].append(edge)
        self._in[dst].append((src, kind))

    def dependencies(self, package, kinds=None):
        edges = self._out.get(package, [])
        if kinds is not None:
            allowed = set(kinds)
            edges = [(dst, kind) for dst, kind in edges if kind in allowed]
        return [{"to": dst, "kind": kind} for dst, kind in edges]

    def referencers(self, package, kinds=None):
        edges = self._in.get(package, [])
        if kinds is not None:
            allowed = set(kinds)
            edges = [(src, kind) for src, kind in edges if kind in allowed]
        return [{"from": src, "kind": kind} for src, kind in edges]

    def missing_dependencies(self, scan_prefix="/Game"):
        known = set(self.nodes)
        missing = []
        for src, edges in self._out.items():
            for dst, kind in edges:
                if dst in known:
                    continue
                if scan_prefix and not dst.startswith(scan_prefix):
                    continue
                missing.append({"from": src, "to": dst, "kind": kind})
        return missing

    def unused_assets(self):
        """Assets not reachable from a root (map / level sequence).

        Zero inbound refs is not enough: two instances that parent each other
        look 'used' but nothing in a level references them.
        """
        roots = [
            package
            for package, node in self.nodes.items()
            if node.get("class") in self.root_classes
        ]
        if not roots:
            unused = []
            for package, node in self.nodes.items():
                game_refs = [
                    src for src, _kind in self._in.get(package, []) if src in self.nodes
                ]
                if not game_refs:
                    unused.append(dict(node))
            return unused
        reachable = set()
        stack = list(roots)
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            for dest, _kind in self._out.get(current, []):
                if dest in self.nodes:
                    stack.append(dest)

        unused = []
        for package, node in self.nodes.items():
            if package not in reachable:
                unused.append(dict(node))
        return unused

    def cycles(self, kinds=("hard",)):
        allowed = set(kinds)
        adj = defaultdict(list)
        for src, edges in self._out.items():
            for dst, kind in edges:
                if kind in allowed and dst in self.nodes:
                    adj[src].append(dst)

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self.nodes}
        stack = []
        found = []

        def dfs(node):
            color[node] = GRAY
            stack.append(node)
            for nxt in adj[node]:
                if nxt not in color:
                    continue
                if color[nxt] == GRAY:
                    idx = stack.index(nxt)
                    found.append(stack[idx:] + [nxt])
                elif color[nxt] == WHITE:
                    dfs(nxt)
            stack.pop()
            color[node] = BLACK

        for node in self.nodes:
            if color[node] == WHITE:
                dfs(node)
        return found

    def most_referenced(self, limit=10):
        ranked = []
        for package, node in self.nodes.items():
            count = len([src for src, _kind in self._in.get(package, []) if src in self.nodes])
            ranked.append({**node, "referencers": count})
        ranked.sort(key=lambda item: (-item["referencers"], item["package"]))
        return ranked[:limit]

    def heaviest_assets(self, limit=10):
        ranked = []
        for package, node in self.nodes.items():
            count = len(self._out.get(package, []))
            ranked.append({**node, "dependencies": count})
        ranked.sort(key=lambda item: (-item["dependencies"], item["package"]))
        return ranked[:limit]

    def class_counts(self):
        return dict(Counter(node.get("class") or "Unknown" for node in self.nodes.values()))

    def build_report(self, scan_path="/Game", query_package="", top_n=10):
        unused = self.unused_assets()
        missing = self.missing_dependencies(scan_prefix=scan_path)
        cycles = self.cycles()
        report = {
            "scan_path": scan_path,
            "summary": {
                "assets": len(self.nodes),
                "edges": sum(len(edges) for edges in self._out.values()),
                "unused": len(unused),
                "missing": len(missing),
                "cycles": len(cycles),
            },
            "by_class": self.class_counts(),
            "unused": unused,
            "missing": missing,
            "cycles": [{"packages": cycle} for cycle in cycles],
            "most_referenced": self.most_referenced(top_n),
            "heaviest_assets": self.heaviest_assets(top_n),
        }
        if query_package:
            report["query"] = {
                "package": query_package,
                "known": query_package in self.nodes,
                "node": self.nodes.get(query_package),
                "dependencies": self.dependencies(query_package),
                "referencers": self.referencers(query_package),
            }
        return report
