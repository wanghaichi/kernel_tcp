from typing import List

from clang.cindex import Index, TranslationUnit  # 主要API
from clang.cindex import Config  # 配置
from clang.cindex import CursorKind  # 索引结点的类别
from clang.cindex import TypeKind  # 节点的语义类别
from clang.cindex import TokenKind  # 节点的语义类别
from pathlib import Path
import shlex

from liebes.CiObjects import TestCaseType


class BaseTokenizer:
    def __init__(self):
        self.name = "BaseVirtualClass"
        pass

    def get_tokens(self, file_path, t):
        raise NotImplemented("BaseTokenizer.get_tokens is not implemented")


class AstTokenizer(BaseTokenizer):
    def __init__(self):
        # can be found using ldconfig -p | grep clang
        Config.set_library_file("libclang-16.so.16.0.6")
        super().__init__()
        self.name = "AstTokenizer"

    # save three kinds of tokens: comments, literal(string value), user defined identifier
    # TODO, this tokenizer doesn't consider the context of the file, like include files, invoke functions, etc.
    def get_tokens(self, contents, t) -> List[str]:
        if t == TestCaseType.C:
            return self.get_tokens_c(contents)
        if t == TestCaseType.SH:
            return self.get_tokens_sh(contents)

    def get_tokens_c(self, contents) -> List[str]:
        index = Index.create()
        try:
            tu = index.parse("temp.c", unsaved_files=[("temp.c", contents)], options=TranslationUnit.PARSE_INCOMPLETE)
            ast_root_node = tu.cursor
            tokens = []
            for token in ast_root_node.get_tokens():
                # 针对一个节点，调用get_tokens的方法。
                if token.kind in [TokenKind.IDENTIFIER, TokenKind.LITERAL, TokenKind.COMMENT]:
                    tokens.append(token.spelling.lower())
            return tokens
        except Exception as e:
            print(f"tokenizer failed, ignore")
            pass
        return []

    def get_tokens_sh(self, contents) -> List[str]:
        # Create a lexer
        lexer = shlex.shlex(contents)

        # Configure lexer options
        lexer.whitespace_split = True
        lexer.commenters = ''
        lexer.wordchars += '${}[]<>|&;'

        # Get the tokens
        tokens = list(lexer)

        return tokens
