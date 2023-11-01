import clang.cindex
from clang.cindex import Index  # 主要API
from clang.cindex import Config  # 配置
from clang.cindex import CursorKind  # 索引结点的类别
from clang.cindex import TypeKind  # 节点的语义类别

if __name__ == "__main__":
    # can be found using ldconfig -p | grep clang
    Config.set_library_file("libclang-16.so.16.0.6")


    file_path = r"/home/wanghaichi/kernelTCP/test_cases/selftests/arm64/signal/test_signals.c"
    index = Index.create()

    tu = index.parse(file_path)
    AST_root_node = tu.cursor  # cursor根节点
    print(AST_root_node)

    '''
    前序遍历严格来说是一个二叉树才有的概念。这里指的是对于每个节点，先遍历本节点，再遍历子节点的过程。
    '''
    node_list = []


    def preorder_travers_AST(cursor):
        for cur in cursor.get_children():
            # do something
            print('Kind:', cur.kind, 'Spelling:', cur.spelling)
            preorder_travers_AST(cur)


    preorder_travers_AST(AST_root_node)

    cursor_content = ""
    for token in AST_root_node.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        print(token.spelling)
