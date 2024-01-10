from pathlib import Path
from typing import List


class CallGraph:
    def __init__(self):
        self.node_map = {}

    def load_from_source(self, cg_output_path):
        cg_output = Path(cg_output_path)
        cg_source = cg_output.read_text().split("Function: ")
        cg_source = [x.strip() for x in cg_source]

        for func_meta in cg_source:
            if func_meta.strip() == "":
                continue
            func_meta = func_meta.split("\n")
            func_name = func_meta[0]
            if func_meta[1].startswith("Origin File: "):
                file_meta = func_meta[1].replace("Origin File: ", "").split(": ")
                file_name = file_meta[0]
                file_number = file_meta[1]
                callers = [x.strip() for x in func_meta[3:]]
            else:
                file_name = None
                file_number = -1
                callers = [x.strip() for x in func_meta[2:]]
            node = self.get_or_create(func_name)
            node.file_path = file_name
            node.start_line = file_number
            node.caller = [self.get_or_create(x) for x in callers]
            for caller_node in node.caller:
                caller_node.callee.append(node)

    def get_or_create(self, func_name) -> 'GraphNode' or None:
        if func_name in self.node_map.keys():
            return self.node_map[func_name]
        node = GraphNode()
        node.function_name = func_name
        self.node_map[func_name] = node
        return node

    '''
    return function name depends on func_name and file_path
    if no match, return all candidates that match func_name
    '''

    def get_node(self, func_name, file_path) -> (bool, List['GraphNode'] or 'GraphNode'):
        candidates = []
        for k, v in self.node_map.items():
            if func_name == k.split(".")[0]:
                candidates.append(v)
        for c in candidates:
            if c.file_path == file_path:
                return True, c
        return False, candidates

    def insert_or_update(self, node: 'GraphNode'):
        self.node_map[node.function_name] = node

    def get_call_list_iteratively(self, func_name):
        start_node = self.get_or_create(func_name)
        call_list = []
        self.dfs(call_list, start_node)

    def dfs(self, call_list, node):
        if len(node.caller) == 0:
            call_list.append(node)
            for n in call_list:
                print(n.function_name, end="->")
            print()
            del call_list[-1]
            return
        if node in call_list:
            r_index = -1
            for i in range(len(call_list)):
                if call_list[i] == node:
                    r_index = i
            back_len = 0
            total_len = 0
            for i in range(len(call_list)):
                print(call_list[i].function_name, end="->")

                if i < r_index:
                    back_len += len(call_list[i].function_name) + 2
                total_len += len(call_list[i].function_name) + 2
            print(node.function_name)
            print(" " * back_len, "|", "_" * (total_len - back_len), '|')
            return
        call_list.append(node)
        for caller in set(node.caller):
            self.dfs(call_list, caller)

    def print_graph(self):
        for k, v in self.node_map.items():
            print(f"Function: {k}")
            print(f"Origin File: {v.file_path}:{v.start_line}")
            print("Caller: ", len(v.caller))
            for caller in v.caller:
                print(f"\t{caller.function_name}")
            print("Callee: ", len(v.callee))
            for callee in v.callee:
                print(f"\t{callee.function_name}")
            print("")


class GraphNode:
    def __init__(self):
        self.file_path = None
        self.start_line = -1
        self.function_name = None
        self.caller = []
        self.callee = []
        pass

    def __str__(self):
        return f"{self.function_name} {self.file_path}:{self.start_line}"


if __name__ == '__main__':
    pass
