from liebes import llvm_process
from liebes.GitHelper import GitHelper
import subprocess
from pathlib import Path


class LTPHelper():
    def __init__(self) -> None:
        self.cmd_file_path = r'/home/wanghaichi/ltp/ltp_make_cmd.txt'
        self.ltp_project_path = r'/home/wanghaichi/ltp/'
        self.githelper = GitHelper(self.ltp_project_path)
        
    def change_version(self, git_sha):
        result = subprocess.run(f'cd {self.ltp_project_path} ; git checkout {git_sha}')


    def generate_bc(self, git_sha):
        self.change_version(git_sha)
        cmd_file = Path(self.cmd_file_path)
        text = cmd_file.read_text().split("\n")

        cmd_list = []
        i = 0
        while i < len(text):
            line = text[i].strip()
            if len(line) == 0:
                i += 1
                continue
            temp = line
            while line.endswith("\\"):
                temp = temp[:-1]
                i += 1
                line = text[i].strip()
                temp += line
            if temp == "done":
                print(text[i - 2:i + 1])
            cmd_list.append(temp)
            i += 1

        cmd_set = set()
        res = []

        res = [llvm_process.handle_cmd_line(x) for x in cmd_list]
        res = [x for x in res if len(x) > 0]

        generated_text = ""
        debug = True
        line_number = 1
        for i in range(len(res)):
            l = res[i]
            if l.startswith("jump"):
                l = l.replace("jump", "").strip()
                l = l.split(" ")
                l = l[0] + " " + self.ltp_project_path + l[1]
                temp = res[i - 1]
                res[i - 1] = l
                res[i] = temp

        visited = set()
        filter_res = []
        for l in res:
            if l not in visited:
                filter_res.append(l)
                if llvm_process.LLVM_CC in l or llvm_process.LLVM_AR in l or llvm_process.LLVM_RANLIB in l or llvm_process.LLVM_OBJCOPY in l:
                    visited.add(l)
                # visited.add(l)
            # else:
            #     print(l)
        #
        for i in range(len(filter_res)):
            l = filter_res[i]
            if l.startswith("cd") and i + 1 < len(filter_res) and filter_res[i + 1].startswith("cd"):
                continue
            generated_text += l + "\n"
            if debug:
                l = l.replace("\"", "\'")
                generated_text += f"echo \"{line_number} {l}\"\n"
                line_number += 2
            # print(l)
        Path("build.sh").write_text(generated_text)
        # analyze dependency
        dependency_bc = {
            "include": "lib/libltp.bc",
            "include/old": "lib/libltp.bc",
            "lib": "lib/libltp.bc",
            "testcases/kernel/mem/include": "testcases/kernel/mem/lib/mem.bc",
            "testcases/kernel/include": "testcases/kernel/lib/libkerntest.bc",
            "testcases/kernel/mem/hugetlb/lib": "testcases/kernel/mem/hugetlb/lib/hugetlb.bc",
            "utils/sctp/include": "utils/sctp/lib/libsctp.bc",
            "utils/sctp/testlib": "utils/sctp/testlib/libsctputil.bc",
            "testcases/network/rpc/rpc-tirpc/tests_pack/lib": "testcases/network/rpc/rpc-tirpc/tests_pack/lib/librpc-tirpc.bc",
            "testcases/network/rpc/rpc-tirpc/tests_pack/include": "testcases/network/rpc/rpc-tirpc/tests_pack/lib/librpc-tirpc.bc",
            "testcases/network/rpc/basic_tests/rpc01/lib": "testcases/network/rpc/basic_tests/rpc01/lib/librpc01.bc",
        }
        dir_prefix = "/home/wanghaichi/ltp/"

        combine_llvm_code_cmd = ""

        cur_dir = None
        dev_set = set()
        for line in generated_text.split("\n"):
            # if line.startswith("llvm-link"):
            #     print(cur_dir)
            #     print(line)

            if line.startswith("cd"):
                cur_dir = line.removeprefix("cd").strip()
            if line.startswith("clang"):
                temp = line.split(" ")
                dependency = []
                bc_file = ""
                for item in temp:
                    if item.startswith("-I"):
                        dep_path = Path(item.removeprefix("-I").strip())
                        if dep_path.is_absolute():
                            dependency.append(str(dep_path.resolve().absolute()))
                        else:
                            dependency.append(str((Path(cur_dir) / dep_path).resolve().absolute()))
                        # dependency.append(cur_dir + "/" + item.removeprefix("-I").strip())
                    if ".bc" in item:
                        bc_file = item.strip()

                if cur_dir.removeprefix(dir_prefix).strip() in dependency_bc.keys():
                    # lib file need not dependency
                    continue

                llvm_cmd = "llvm-link "
                dependency = [x.removeprefix(dir_prefix).strip() for x in dependency]
                dependency = set([dependency_bc[x] for x in dependency if x in dependency_bc.keys()])
                if len(dependency) == 0:
                    continue
                for d in dependency:
                    llvm_cmd += f"{Path(dir_prefix) / d} "
                llvm_cmd += f"{bc_file} -o dep_{bc_file}"
                combine_llvm_code_cmd += f"cd {cur_dir}\n"
                combine_llvm_code_cmd += llvm_cmd + "\n"

        Path("combine_llvm_code.sh").write_text(combine_llvm_code_cmd)

    def adjust_version(self):
        pass
    