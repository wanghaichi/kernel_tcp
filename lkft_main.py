from tree_sitter import Language, Parser, Node

from liebes.CallGraph import CallGraph

import os

import json

c_code = ''
call_graph = {}
api_names = []
call_function_names = []
files = []
include_files = []

def traverse_tree(node: Node):
    if node.type == 'preproc_include':
        include_files.append(c_code[node.start_byte + 9: node.end_byte - 1])
    if node.type == 'call_expression':
        for c in node.children:
            if c.type == 'identifier':
                function_name = c_code[node.start_byte: node.end_byte]
                call_function_names.append(function_name)

    for child in node.children:
        traverse_tree(child)


def traverse_dir(directory: str):
    files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            files.append(os.path.join(root, file))
        
        for dir in dirs:
            dir_path = os.path.join(root, dir)

            traverse_dir(dir_path)

def handle_source_code(directory: str):
    C_LANGUAGE = Language('build/my-languages.so', 'c')
    C_PARSER = Parser()
    C_PARSER.set_language(C_LANGUAGE)

    traverse_dir(directory)
    source_codes = []
    c_files = []
    for f in files:
        if f.endswith('.c'):
            c_files.append(f)
    for f in c_files:
        print(f)
        with open(f, r'r', encoding='utf-8', errors='ignore') as c_file:
            c_code = c_file.read()
        tree = C_PARSER.parse(c_code.encode())
        c_file.close()
        include_files.clear()
        call_function_names.clear()
        traverse_tree(tree.root_node)
        source_code = {}
        source_code['name'] = f
        source_code['include'] = include_files
        source_code['call'] = call_function_names
        source_codes.append(source_code)


    with open(r'ltp_case_call.json', r'w', encoding='utf-8', errors='ignore') as f:
        json.dump(source_codes, f)
    f.close()

def handle_head_file(directory: str):
    C_LANGUAGE = Language('build/my-languages.so', 'c')
    C_PARSER = Parser()
    C_PARSER.set_language(C_LANGUAGE)

    traverse_dir(directory)
    h_files = []
    for f in files:
        if f.endswith('.h'):
            h_files.append(f)
    
    for f in h_files:
        with open(f, r'r', encoding='utf-8', errors='ignore') as h_file:
            c_code = h_file.read()
        tree = C_PARSER.parse(c_code.encode())
        h_file.close()
        include_files.clear()
        call_function_names.clear()
        traverse_tree(tree.root_node)
        test_case = {}
        test_case['name'] = f
        test_case['include'] = include_files
        test_case['call'] = call_function_names
        test_cases.append(test_case)


if __name__ == '__main__':
    
    # handle_source_code(r'test_cases/ltp/testcases')
    pass