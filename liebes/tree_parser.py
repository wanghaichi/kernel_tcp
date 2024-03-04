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

        Language.build_library(
            'build/my-languages.so',
            [
                'parser/tree-sitter-c',
                # 'parser/tree-sitter-bash',
            ]
        )

        C_LANGUAGE = Language('build/my-languages.so', 'c')
        # BASH_LANGUAGE = Language('build/my-languages.so', 'bash')
        self.c_parser = Parser()
        self.c_parser.set_language(C_LANGUAGE)
        # self.c_parser.set_language(BASH_LANGUAGE)

    def parse_call_func_names(self, code_snippet):
        tree = self.c_parser.parse(bytes(code_snippet, "utf8"))
        root_node = tree.root_node
        fun_names = self.get_call_function_names(root_node)
        fun_names = [x.decode("utf-8", errors="ignore") for x in fun_names]
        return fun_names

    def get_call_function_names(self, node: Node):
        stack = [node]
        res = []
        while len(stack) > 0:
            cur_node = stack.pop()
            if cur_node.type == "call_expression":
                for ch in cur_node.children:
                    if ch.type == "identifier":
                        res.append(ch.text)
            for child in cur_node.children:
                stack.append(child)
        return res

    def get_functions_scope(self, node: Node):
        stack = [node]
        res = []
        while len(stack) > 0:
            cur_node = stack.pop()
            if cur_node.type == "function_declarator":
                function_name = cur_node.children[0].text.decode("utf-8", errors="ignore")
                fa = cur_node
                while fa is not None and fa.type != "function_definition":
                    fa = fa.parent
                if fa is None:
                    # only definition, no declaration
                    return []
                function_scope = (fa.range.start_point[0], fa.range.end_point[0])
                res.append((function_name, function_scope))
            else:
                for ch in cur_node.children:
                    stack.append(ch)
        return res

    def parse(self, code_snippet):
        tree = self.c_parser.parse(bytes(code_snippet, "utf8"))
        root_node = tree.root_node
        return root_node

    def get_function_body(self, node, function_name, start_line):
        candidates = []
        stack = [node]
        while len(stack) > 0:
            cur_node = stack.pop()
            if cur_node.type == "function_declarator":
                fn = cur_node.children[0].text.decode("utf-8", errors="ignore")
                if fn == function_name:
                    fa = cur_node
                    while fa is not None and fa.type != "function_definition":
                        fa = fa.parent
                    if fa is None:
                        # only definition, no declaration
                        return
                    function_scope = (fa.range.start_point[0], fa.range.end_point[0])
                    candidates.append((fa, function_scope))
            else:
                for ch in cur_node.children:
                    stack.append(ch)
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
