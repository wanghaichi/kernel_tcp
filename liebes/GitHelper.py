from git import Repo
import difflib


class GitHelper:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)

    def diff(self, commit, to_commit):
        commit_obj_a = self.repo.commit(commit)
        commit_obj_b = self.repo.commit(to_commit)
        diff = commit_obj_a.diff(commit_obj_b)
        print(commit)
        print(to_commit)
        for diff_obj in diff.iter_change_type('M'):
            print("Modified lines:")
            a_lines = diff_obj.a_blob.data_stream.read().decode('utf-8').split('\n')
            b_lines = diff_obj.b_blob.data_stream.read().decode('utf-8').split('\n')
            diff_lines = difflib.unified_diff(a_lines, b_lines)
            for line in diff_lines:
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
    repo = Repo(repo_path)

    pass
