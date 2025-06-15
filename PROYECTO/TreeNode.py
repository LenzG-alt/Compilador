class TreeNode:
    _counter = 0  # Clase global

    def __init__(self, label, children=None):
        self.label = label
        self.children = children or []
        self.id = f"n{TreeNode._counter}"
        TreeNode._counter += 1

    def add_child(self, node):
        self.children.append(node)

    def render(self, dot):
        dot.node(self.id, self.label)
        for child in self.children:
            if child:
                dot.edge(self.id, child.id)
                child.render(dot)

    def to_dot(self):
        from graphviz import Digraph
        dot = Digraph()
        self.render(dot)
        return dot
