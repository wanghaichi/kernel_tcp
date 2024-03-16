from pathlib import Path
from typing import List
import copy


class CallGraph:
    def __init__(self, source_path):
        self.node_map = {}
        self.source_path = source_path
        self.load_from_source(source_path)
        self.top_funcs = []

    def load_from_source(self, cg_output_path):
        cg_output = Path(cg_output_path)
        cg_source = cg_output.read_text().split("\n")
        cg_source = [x.strip() for x in cg_source]

        for func_meta in cg_source:
            if func_meta.strip() == "":
                continue
            func_meta = func_meta.split(" : ")
            func_name = func_meta[0].strip()
            
            node = self.get_or_create(func_name)
            if len(func_meta) > 1:
                c_node = self.get_or_create(func_meta[1].strip())
                node.caller.append(c_node)
                c_node.callee.append(node)

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

    def get_node(self, func_name, file_path, func_scope=None) -> 'GraphNode':
        candidates = []
        for k, v in self.node_map.items():
            if func_name == k.split(".")[0] and v.file_path == file_path:
                candidates.append(v)
        if func_scope[0] is None:
            return candidates
        n = 100000000
        res = None
        for candidate in candidates:
            if abs(candidate.start_line - func_scope[0]) < n:
                n = abs(candidate.start_line - func_scope[0])
                res = candidate
        return res

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

    def get_context(self, node: 'GraphNode', depth=1):

        pre_context = self.forward_step(node, depth)
        post_context = self.backward_step(node, depth)
        return (pre_context, post_context)

    def forward_step(self, node: 'GraphNode', depth):
        if depth <= 0:
            return []
        forward_res = []
        def _dfs_step(node, res, target_depth):
            if target_depth == len(res):
                forward_res.append(copy.copy(res))
                return
            for caller in node.caller:
                if caller in res:
                    continue
                res.append(caller)
                _dfs_step(caller, res, target_depth)
                del res[-1]
        _dfs_step(node, [], depth)
        return forward_res

    def backward_step(self, node: 'GraphNode', depth):
        if depth <= 0:
            return []
        callee_res = []

        def _dfs_step(node, res, target_depth):
            if target_depth == len(res):
                callee_res.append(copy.copy(res))
                return
            for callee in node.callee:
                if callee in res:
                    continue
                res.append(callee)
                _dfs_step(callee, res, target_depth)
                del res[-1]
        _dfs_step(node, [], depth)
        return callee_res

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

    def get_syscall(self, syscall_list, root_node_name):
        root_node = self.node_map.get(root_node_name)
        if root_node is None:
            return set()
        visited_set = set()
        syscall_set = set()
        stack = [root_node]

        while stack:
            cur_node = stack.pop()
            if cur_node not in visited_set:
                visited_set.add(cur_node)
                if cur_node.function_name in syscall_list:
                    syscall_set.add(cur_node.function_name)
                stack.extend(cur_node.caller)
        
        return syscall_set


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
