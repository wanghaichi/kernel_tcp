import subprocess
from pathlib import Path

from liebes.ci_logger import logger


class LLVMHelper:
    CC = "gcc"
    AR = "ar -rc"
    RANLIB = "ranlib"
    OBJCOPY = "objcopy"

    LLVM_CC = "clang"
    LLVM_AR = "llvm-link"
    LLVM_RANLIB = "llvm-ranlib"
    LLVM_OBJCOPY = "llvm-objcopy"

    def __init__(self, root_path):
        self.root_path = root_path
        pass

    def generate_bitcode(self):
        logger.info("start to generate bitcode command")
        cmd_text = self.obtain_make_cmd()
        if cmd_text is None:
            logger.error("failed to generate make command")
            return
        logger.info("start to parse make command")
        parsed_cmd, combine_llvm_code_cmd = self.parse_make_cmd(cmd_text)

        Path(f"{self.root_path}/build.sh").write_text(parsed_cmd)
        Path(f"{self.root_path}/build.sh").chmod(0o755)
        Path(f"{self.root_path}/combine.sh").write_text(combine_llvm_code_cmd)
        Path(f"{self.root_path}/combine.sh").chmod(0o755)
        logger.info("start to execute make command")
        cmd = f"bash build.sh"
        subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.root_path)
        subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.root_path)
        logger.info(f"The bitcode is generated successfully. Please check bc file starts with dep_ at {self.root_path}")
        return

    def obtain_make_cmd(self):
        logger.info("obtain ltp make command")
        cmd = f"make autotools && ./configure --prefix={self.root_path}/build && make -n > ltp_make_cmd.txt"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.root_path)
        if result.returncode != 0:
            logger.error("execute command failed: ", cmd)
            logger.error("error message: ", result.stderr)
            return None

        cmd_file = Path(f"{self.root_path}/ltp_make_cmd.txt")
        logger.info(f"ltp make command is located at {cmd_file.absolute()}")
        text = cmd_file.read_text()
        return text

    def parse_make_cmd(self, make_text):
        make_text = make_text.split("\n")
        cmd_list = []
        i = 0
        while i < len(make_text):
            line = make_text[i].strip()
            if len(line) == 0:
                i += 1
                continue
            temp = line
            continue_flag = False
            while line.endswith("\\"):
                temp = temp[:-1]
                i += 1
                line = make_text[i].strip()
                temp += line
                continue_flag = True
            if not continue_flag and ";" in temp:
                temp = temp.split(";")
                for t in temp:
                    if len(t.strip()) == 0:
                        continue
                    cmd_list.append(t.strip())
            else:
                cmd_list.append(temp)
            i += 1

        res = [self.handle_cmd_line(x) for x in cmd_list]
        res = [x for x in res if len(x) > 0]

        generated_text = ""
        debug = True
        line_number = 1
        root = f"{self.root_path}/"
        for i in range(len(res)):
            l = res[i]
            if l.startswith("jump"):
                l = l.replace("jump", "").strip()
                l = l.split(" ")
                l = l[0] + " " + root + l[1]
                temp = res[i - 1]
                res[i - 1] = l
                res[i] = temp

        visited = set()
        filter_res = []
        for l in res:
            if l not in visited:
                filter_res.append(l)
                if (LLVMHelper.LLVM_CC in l or LLVMHelper.LLVM_AR in l
                        or LLVMHelper.LLVM_RANLIB in l or LLVMHelper.LLVM_OBJCOPY in l):
                    visited.add(l)
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
        dir_prefix = f"{self.root_path}/"

        combine_llvm_code_cmd = ""

        cur_dir = None
        for line in generated_text.split("\n"):

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
                    if ".bc" in item:
                        bc_file = item.strip()

                if cur_dir.removeprefix(dir_prefix).strip() in dependency_bc.keys():
                    # lib file need not dependency
                    continue

                llvm_cmd = f"{LLVMHelper.LLVM_AR} "
                dependency = [x.removeprefix(dir_prefix).strip() for x in dependency]
                dependency = set([dependency_bc[x] for x in dependency if x in dependency_bc.keys()])
                if len(dependency) == 0:
                    continue
                for d in dependency:
                    llvm_cmd += f"{Path(dir_prefix) / d} "
                llvm_cmd += f"{bc_file} -o dep_{bc_file}"
                combine_llvm_code_cmd += f"cd {cur_dir}\n"
                combine_llvm_code_cmd += llvm_cmd + "\n"

        generated_text = f"cd {self.root_path}/include && ../lib/gen_version.sh\n" + generated_text
        return generated_text, combine_llvm_code_cmd

    def handle_cmd_line(self, line):
        if line.startswith(LLVMHelper.CC):
            return self.handleCC(line)
        elif line.startswith(LLVMHelper.AR):
            return self.handleAR(line)
        elif line.startswith(LLVMHelper.RANLIB):
            pass
        elif line.startswith("make"):
            pass
        elif line.startswith(LLVMHelper.OBJCOPY):
            return self.handleOBJCOPY(line)
        elif line.startswith("echo"):
            if "CC" in line:
                temp = line.split("CC")[1].strip()
                temp = temp.split(";")[0].strip()
                if Path(f"/home/wanghaichi/kernelTCP/test_cases/ltp/{temp}").is_dir():
                    pass
                else:
                    temp = temp.split("/")[:-1]
                    temp = "/".join(temp)

                return f"jump cd {temp}"
        return ""

    def handleOBJCOPY(self, line):
        res = line.replace(LLVMHelper.OBJCOPY, LLVMHelper.LLVM_OBJCOPY + " -v -o")
        res = res.replace(".o", ".bc")
        return res

    def handleCC(self, line):

        res = line.replace("-O2", "-O0")
        res = res.replace("-O3", "-O0")
        res = res.replace("-Os", "-O0")
        res = res.replace(".o", ".bc")
        res = res.replace('-mno-fp-ret-in-387', "")
        res = res.replace('-mpreferred-stack-boundary=3', "")
        res = res.replace('-mskip-rax-setup', "")
        res = res.replace('-mindirect-branch=thunk-extern', "")
        res = res.replace('-mindirect-branch-register', "")
        res = res.replace('-fno-allow-store-data-races', "")
        res = res.replace('-fno-var-tracking-assignments', "")
        res = res.replace('-flive-patching=inline-clone', "")
        res = res.replace('-fconserve-stack', "")
        res = res.replace('-mrecord-mcount', "")
        if ".c" in res:
            res = res.replace(LLVMHelper.CC, LLVMHelper.LLVM_CC + " " + "-emit-llvm ", 1)
        else:
            res = res.replace(LLVMHelper.CC, LLVMHelper.LLVM_CC + " ", 1)
        if not ".bc" in res:
            temp = res.split("-o ")
            if len(temp) > 1:
                temp = temp[1].strip().split(" ")
                to_replace = temp[0].strip()
                temp = res.split("-o ")
                res = temp[0] + " -o " + temp[1].replace(to_replace, to_replace + ".bc")
        # # move -o xxx.bc to the end
        # match = re.search(r'(-o\s+\w+\.bc)', res)
        # if not match:
        #     return res
        # substring = match.group(1)
        # res = res.replace(substring, '')
        # res += " " + substring
        if "-c" not in res:
            res = res.replace("-o", "-c -o")
        return res

    def handleAR(self, line):
        res = line.replace(LLVMHelper.AR, LLVMHelper.LLVM_AR + " -v -o ")
        res = res.replace(".a", ".bc")
        res = res.replace(".o", ".bc")
        return res

    def handleRANLIB(self, line):
        res = line.replace(LLVMHelper.RANLIB, LLVMHelper.LLVM_RANLIB)
        res = res.replace(".a", ".bc")
        res = res.replace(".o", ".bc")
        return res


if __name__ == "__main__":
    pass
