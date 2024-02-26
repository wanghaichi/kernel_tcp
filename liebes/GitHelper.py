from git import Repo
import difflib

from pathlib import Path

from liebes.CallGraph import CallGraph
from liebes.tree_parser import CodeAstParser
from liebes.ci_logger import logger


class DiffBlock:
    def __init__(self):
        self.origin_line_scope = (-1, -1)
        self.modified_line_scope = (-1, -1)
        self.file_path = ""
        self.content = ""
        self.belonged_function = ""
        self.called_functions = None

    def __str__(self):
        return f"{self.file_path}: {self.origin_line_scope} -> {self.modified_line_scope}, belongs to {self.belonged_function}, calls {self.called_functions}" \
               f"\n{self.content}"


class GitHelper:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
        self.ast_parser = CodeAstParser()
        self.cg = CallGraph()
        self.cg.load_from_source("/home/wanghaichi/llvm_kernel/output-cg.txt")

    def get_commit_info(self, commit_id):
        try:
            commit_obj = self.repo.commit(commit_id)
        except ValueError as e:
            return None
        return commit_obj

    def get_file_content_by_commit(self, commit_id, file_path):
        commit_obj = self.repo.commit(commit_id)
        try:
            return commit_obj.tree[file_path].data_stream.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return None

    def get_diff_blocks(self, commit, to_commit):
        commit_obj_a = self.repo.commit(commit)
        commit_obj_b = self.repo.commit(to_commit)
        diff = commit_obj_a.diff(commit_obj_b)
        # TODO not only consider modified type, but also ADD type, etc.
        '''
                # change type invariant identifying possible ways a blob can have changed
                # A = Added (All contents from the new file should be considered)
                # D = Deleted (The contents from the deleted file should be considered)
                # R = Renamed (All contents from the file should be considered)
                # M = Modified (Only difference should be taken into consideration)
                # T = Changed in the type (Do not need to be considered)
                '''
        captured_type = [
            "A",
            "D",
            "R",
            "M",
        ]
        diff_content = []
        file_list = []

        # for diff_obj in diff.iter_change_type("A"):
        #     try:
        #         diff_content.append(diff_obj.b_blob.data_stream.read().decode('utf-8'))
        #         file_list.append(diff_obj.b_path)
        #     except Exception as e:
        #         pass
        #     pass
        #
        # for diff_obj in diff.iter_change_type("D"):
        #     try:
        #         diff_content.append(diff_obj.a_blob.data_stream.read().decode('utf-8'))
        #         file_list.append(diff_obj.a_path)
        #     except Exception as e:
        #         pass
        #     pass

        # for diff_obj in diff.iter_change_type("R"):
        #     try:
        #         diff_content.append(diff_obj.b_blob.data_stream.read().decode('utf-8'))
        #         file_list.append(diff_obj.b_path)
        #     except Exception as e:
        #         pass
        #     pass
        # TODO 当以整个文件作为粒度的时候，例如某个文件发生了变化，前后版本分别为a_blob和b_blob，那么在
        # TODO 计算文件的时候是将两个版本的内容都加入到语料中，还是应该只加入修改后的？

        # TODO 添加参数，适配context的大小，目前的context大小为0，即没有考虑上下文。
        for diff_obj in diff.iter_change_type("M"):
            if Path(diff_obj.b_path).suffix == ".c":
                try:
                    a_lines = diff_obj.a_blob.data_stream.read().decode('utf-8', errors="ignore").split('\n')
                    b_lines = diff_obj.b_blob.data_stream.read().decode('utf-8', errors="ignore").split('\n')
                    diff_lines = difflib.ndiff(a_lines, b_lines)
                    temp = []
                    original_line_number = 0
                    modified_line_number = 0

                    for line in diff_lines:
                        if line.startswith("-"):
                            # line = line.removeprefix("-").strip()
                            # print(line)
                            original_line_number += 1
                            temp.append((original_line_number, modified_line_number, line))
                        elif line.startswith("+"):
                            # print(line)
                            # line = line.removeprefix("+").strip()
                            modified_line_number += 1
                            temp.append((original_line_number, modified_line_number, line))
                        else:
                            original_line_number += 1
                            modified_line_number += 1
                    # print(temp)
                    diff_content.append(temp)
                    file_list.append(diff_obj.b_path)
                except Exception as e:
                    logger.error(f"{commit}, {to_commit} error happened! need check!")
            pass
        res = []
        for diff, file_path in zip(diff_content, file_list):
            c_code_snippet = self.get_file_content_by_commit(to_commit, file_path)
            root_node = self.ast_parser.parse(c_code_snippet)
            scopes = self.ast_parser.get_functions_scope(root_node)
            scopes.sort(key=lambda x: x[1][0])
            diff_list = []
            prev_idx = 0
            for idx in range(1, len(diff)):
                # origin index
                if diff[idx][0] == diff[idx - 1][0] or diff[idx][0] == diff[idx - 1][0] + 1:
                    continue
                if diff[idx][1] == diff[idx - 1][1] or diff[idx][1] == diff[idx - 1][1] + 1:
                    continue
                diff_block = DiffBlock()
                diff_block.file_path = file_path
                diff_block.origin_line_scope = (diff[prev_idx][0], diff[idx - 1][0])
                diff_block.modified_line_scope = (diff[prev_idx][1], diff[idx - 1][1])
                diff_block.content = "\n".join(
                    [x[2] for x in diff[prev_idx:idx]])

                for s in scopes:
                    if s[1][0] <= diff_block.origin_line_scope[0] <= s[1][1]:
                        diff_block.belonged_function = s[0]
                        break
                diff_list.append(diff_block)
                prev_idx = idx
            idx = len(diff)
            diff_block = DiffBlock()
            diff_block.file_path = file_path
            diff_block.origin_line_scope = (diff[prev_idx][0], diff[idx - 1][0])
            diff_block.modified_line_scope = (diff[prev_idx][1], diff[idx - 1][1])
            diff_block.content = "\n".join([x[2] for x in diff[prev_idx:idx]])

            for s in scopes:
                if s[1][0] <= diff_block.origin_line_scope[0] <= s[1][1]:
                    diff_block.belonged_function = s[0]
                    break
            diff_list.append(diff_block)

            for db in diff_list:
                call_func = self.ast_parser.parse_call_func_names(db.content)
                db.called_functions = [x for x in call_func]
            res.extend(diff_list)
        # print("start to print!!")
        # for t in res:
        #     print(t)
        return res

    def get_diff_contents(self, commit, to_commit, strategy="default"):
        """
        :param commit: previous commit sha
        :param to_commit: current commit sha
        :param strategy:
            default, only consider code changes.
            context, consider context functions, based on call graph
        :return:
        """
        # TODO 针对diff内容，需要考虑 + ，-，的行（删除和新增）分别需要对应上一版本和当前版本
        diff_list = self.get_diff_blocks(commit, to_commit)
        res = []
        if strategy == "default":
            res = [x.content for x in diff_list]
        elif strategy == "context":
            for db in diff_list:
                call_func = self.ast_parser.parse_call_func_names(db.content)
                db.called_functions = [x for x in call_func]
                cg_node = self.cg.get_node(db.belonged_function, db.file_path, db.modified_line_scope)
                callee_body_contents = []
                caller_body_contents = []
                if cg_node is not None:
                    # callee:
                    for ce in cg_node.callee:
                        c_code_snippet = self.get_file_content_by_commit(to_commit, ce.file_path)
                        # c_code_snippet = (Path("/home/wanghaichi/linux-1") / ce.file_path).read_text()
                        if c_code_snippet is None:
                            continue
                        root_node = self.ast_parser.parse(c_code_snippet)
                        callee_body = self.ast_parser.get_function_body(root_node, ce.function_name, ce.start_line)
                        callee_body_contents.append(callee_body)
                    # caller
                    for ce in cg_node.caller:
                        c_code_snippet = self.get_file_content_by_commit(to_commit, ce.file_path)
                        if c_code_snippet is None:
                            continue
                        root_node = self.ast_parser.parse(c_code_snippet)
                        callee_body = self.ast_parser.get_function_body(root_node, ce.function_name, ce.start_line)
                        caller_body_contents.append(callee_body)
                # add code change, callee and caller
                res.append(db.content)
                res.extend(callee_body_contents)
                res.extend(caller_body_contents)
        else:
            logger.error("strategy not supported!")
        return res

    def diff(self, commit, to_commit):
        commit_obj_a = self.repo.commit(commit)
        commit_obj_b = self.repo.commit(to_commit)
        diff = commit_obj_a.diff(commit_obj_b)
        # print(commit)
        # print(to_commit)
        '''
        # change type invariant identifying possible ways a blob can have changed
        # A = Added
        # D = Deleted
        # R = Renamed
        # M = Modified
        # T = Changed in the type
        '''
        captured_type = [
            "A",
            "C",
            "D",
            "R",
            "M",
            "T"
        ]
        for t in captured_type:
            for diff_obj in diff.iter_change_type(t):
                print("Modified lines:")
                a_lines = diff_obj.a_blob.data_stream.read().decode('utf-8', errors="ignore").split('\n')
                b_lines = diff_obj.b_blob.data_stream.read().decode('utf-8', errors="ignore").split('\n')
                diff_lines = difflib.unified_diff(a_lines, b_lines)
                for line in diff_lines:
                    if line.startswith("+") or line.startswith("-"):
                        line = line.removeprefix("+").removeprefix("-").strip()
                        print(line)
                print("----------------------------------------")
                #
                # # Process modified files
                # print("=" * 20)
                # print(changed_file.)
                # print(diff_obj.a_blob.data_stream.read().decode("utf-8"))
                # print(diff_obj.b_blob.data_stream.read().decode("utf-8"))
                # # print(diff_obj.a_path)
                # # print(diff_obj.b_path)
                # # print(diff_obj.a_mode)
                # # print(diff_obj.b_mode)
                # print(diff_obj.diff)
                # print("=" * 20)


if __name__ == '__main__':
    pass
