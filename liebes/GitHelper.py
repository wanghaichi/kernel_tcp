from git import Repo
import difflib

from pathlib import Path

from git.diff import Lit_change_type


class GitHelper:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)

    def get_commit_info(self, commit_id):
        try:
            commit_obj = self.repo.commit(commit_id)
        except ValueError as e:
            return None
        return commit_obj

    def get_diff_contents(self, commit, to_commit):
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

        for diff_obj in diff.iter_change_type("A"):
            try:
                diff_content.append(diff_obj.b_blob.data_stream.read().decode('utf-8'))
            except Exception as e:
                pass
            pass

        for diff_obj in diff.iter_change_type("D"):
            try:
                diff_content.append(diff_obj.a_blob.data_stream.read().decode('utf-8'))
            except Exception as e:
                pass
            pass

        for diff_obj in diff.iter_change_type("R"):
            try:
                diff_content.append(diff_obj.b_blob.data_stream.read().decode('utf-8'))
            except Exception as e:
                pass
            pass
        # TODO 当以整个文件作为粒度的时候，例如某个文件发生了变化，前后版本分别为a_blob和b_blob，那么在
        # TODO 计算文件的时候是将两个版本的内容都加入到语料中，还是应该只加入修改后的？

        # TODO 添加参数，适配context的大小，目前的context大小为0，即没有考虑上下文。
        for diff_obj in diff.iter_change_type("M"):
            if Path(diff_obj.b_path).suffix == ".c":
                try:
                    a_lines = diff_obj.a_blob.data_stream.read().decode('utf-8').split('\n')
                    b_lines = diff_obj.b_blob.data_stream.read().decode('utf-8').split('\n')
                    diff_lines = difflib.ndiff(a_lines, b_lines)
                    temp = []
                    for line in diff_lines:
                        if line.startswith("+") or line.startswith("-"):
                            line = line.removeprefix("+").removeprefix("-").strip()
                            temp.append(line)
                    diff_content.append("\n".join(temp))
                except Exception as e:
                    print(f"{commit}, {to_commit} error happened! need check!")
            pass

        return diff_content

    def diff(self, commit, to_commit):
        commit_obj_a = self.repo.commit(commit)
        commit_obj_b = self.repo.commit(to_commit)
        diff = commit_obj_a.diff(commit_obj_b)
        print(commit)
        print(to_commit)
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
            print(t)
            for diff_obj in diff.iter_change_type(t):
                print("Modified lines:")
                a_lines = diff_obj.a_blob.data_stream.read().decode('utf-8').split('\n')
                b_lines = diff_obj.b_blob.data_stream.read().decode('utf-8').split('\n')
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
    repo_path = '/home/wanghaichi/linux'
    git_helper = GitHelper(repo_path=repo_path)

    git_helper.diff("94f6f0550c625fab1f373bb86a6669b45e9748b3", "1c8b86a3799f7e5be903c3f49fcdaee29fd385b5")

    pass
