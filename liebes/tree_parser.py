from tree_sitter import Language, Parser, Node

from liebes.CallGraph import CallGraph


# Language.build_library(
#     'build/my-languages.so',
#     [
#         'parser/tree-sitter-c',
#     ]
# )

class CodeAstParser:
    def __init__(self):

        # Language.build_library(
        #     'build/my-languages.so',
        #     [
        #         'parser/tree-sitter-c',
        #     ]
        # )

        self.C_LANGUAGE = Language('build/my-languages.so', 'c')
        self.c_parser = Parser()
        self.c_parser.set_language(self.C_LANGUAGE)

    def parse_call_func_names(self, code_snippet):
        tree = self.c_parser.parse(bytes(code_snippet, "utf8"))
        root_node = tree.root_node
        fun_names = self.get_call_function_names(root_node)
        fun_names = [x.decode("utf-8", errors="ignore") for x in fun_names]
        return fun_names

    def get_call_function_names(self, node: Node):
        def _visit(node):
            res = []
            if node.type == "call_expression":
                for ch in node.children:
                    if ch.type == "identifier":
                        res.append(ch.text)
            for child in node.children:
                res.extend(_visit(child))
            return res

        return _visit(node)

    def get_functions_scope(self, node: Node):
        def _visit(node):
            res = []
            if node.type == "function_declarator":
                function_name = node.children[0].text.decode("utf-8", errors="ignore")
                fa = node
                while fa is not None and fa.type != "function_definition":
                    fa = fa.parent
                if fa is None:
                    # only definition, no declaration
                    return []
                function_scope = (fa.range.start_point[0], fa.range.end_point[0])
                res.append((function_name, function_scope))
            else:
                for ch in node.children:
                    res.extend(_visit(ch))
            return res

        return _visit(node)

    def parse(self, code_snippet):
        tree = self.c_parser.parse(bytes(code_snippet, "utf8"))
        root_node = tree.root_node
        return root_node

    def get_function_body(self, node, function_name, start_line):
        candidates = []

        def _visit(node):
            if node.type == "function_declarator":
                fn = node.children[0].text.decode("utf-8", errors="ignore")
                if fn == function_name:
                    fa = node
                    while fa is not None and fa.type != "function_definition":
                        fa = fa.parent
                    if fa is None:
                        # only definition, no declaration
                        return
                    function_scope = (fa.range.start_point[0], fa.range.end_point[0])
                    candidates.append((fa, function_scope))
            else:
                for ch in node.children:
                    _visit(ch)

        _visit(node)
        relavence = 10000000
        res = None
        for c in candidates:
            if abs(c[1][0] - start_line) < relavence:
                relavence = abs(c[1][0] - start_line)
                res = c[0]
        if res is None:
            return ""
        return res.text.decode("utf-8")


if __name__ == "__main__":
    pass
