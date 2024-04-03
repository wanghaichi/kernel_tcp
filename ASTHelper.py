import clang.cindex
from clang.cindex import Index  # 主要API
from clang.cindex import Config  # 配置
from clang.cindex import CursorKind  # 索引结点的类别
from clang.cindex import TypeKind  # 节点的语义类别
from clang.cindex import TokenKind  # 节点的语义类别
from pathlib import Path


if __name__ == "__main__":
    # can be found using ldconfig -p | grep clang
    # ubuntu 20.04:
    # add deb [arch=amd64] http://mirrors.tuna.tsinghua.edu.cn/llvm-apt/focal/ llvm-toolchain-focal-16 main
    # sudo apt update && sudo apt install -y llvm-16 clang-16
    Config.set_library_file("libclang-16.so.16.0.6")

    file_path = r"/home/wanghaichi/kernelTCP/test_cases/selftests/arm64/signal/test_signals.c"
    print(Path(file_path).read_text())

    index = Index.create()

    tu = index.parse(file_path)

    AST_root_node = tu.cursor  # cursor根节点
    # print(AST_root_node)

    # '''
    # 前序遍历严格来说是一个二叉树才有的概念。这里指的是对于每个节点，先遍历本节点，再遍历子节点的过程。
    # '''
    # node_list = []

    #
    # def preorder_travers_AST(cursor):
    #     for cur in cursor.get_children():
    #         # do something
    #         # print('Spelling:', cur.spelling)
    #         print('Kind:', cur.kind, 'Spelling:', cur.spelling)
    #         preorder_travers_AST(cur)
    #
    #
    # preorder_travers_AST(AST_root_node)
    tokens = []
    for token in AST_root_node.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        if token.kind in [TokenKind.IDENTIFIER, TokenKind.LITERAL, TokenKind.COMMENT]:
            tokens.append(token.spelling)
        # print('Kind:', token.kind, 'Spelling:', token.spelling)
    print(tokens)