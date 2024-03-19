from pathlib import Path

CC = "gcc"
AR = "ar -rc"
RANLIB = "ranlib"
OBJCOPY = "objcopy"

LLVM_CC = "clang"
LLVM_AR = "llvm-link"
LLVM_RANLIB = "llvm-ranlib"
LLVM_OBJCOPY = "llvm-objcopy"


def handle_cmd_line(line):
    if line.startswith(CC):
        return handleCC(line)
    elif line.startswith(AR):
        return handleAR(line)
    elif line.startswith(RANLIB):
        pass
        # return handleRANLIB(line)
    elif line.startswith("make"):
        pass
        # if "Entering directory" in line:
        #     return "cd " + line.split("Entering directory")[-1].strip()
        # elif "Leaving directory" in line:
        #     return "cd /home/wanghaichi/kernelTCP/test_cases/ltp"
    elif line.startswith(OBJCOPY):
        return handleOBJCOPY(line)
    elif line.startswith("echo"):
        if "CC" in line:

            temp = line.split("CC")[1].strip()
            if Path(f"/home/wanghaichi/kernelTCP/test_cases/ltp/{temp}").is_dir():
                pass
            else:
                temp = temp.split("/")[:-1]
                temp = "/".join(temp)

            return f"jump cd {temp}"
    return ""


def handleOBJCOPY(line):
    res = line.replace(OBJCOPY, LLVM_OBJCOPY + " -v -o")
    res = res.replace(".o", ".bc")
    return res


def handleCC(line):
    res = line.replace(CC, LLVM_CC + " " + "-emit-llvm ")
    res = res.replace("-O2", "-O0")
    res = res.replace("-O3", "-O0")
    res = res.replace("-Os", "-O0")
    res = res.replace(".o", ".bc")
    if not ".bc" in res:
        temp = res.split("-o")
        if len(temp) > 1:
            temp = temp[1].strip().split(" ")
            to_replace = temp[0].strip()
            temp = res.split("-o")
            res = temp[0] + "-o" + temp[1].replace(to_replace, to_replace + ".bc")
    if not "-c" in res:
        res = res.replace("-o", "-c -o")
    return res


def handleAR(line):
    res = line.replace(AR, LLVM_AR + " -v -o ")
    # res = res.replace("-rc", "")
    res = res.replace(".a", ".bc")
    res = res.replace(".o", ".bc")
    return res


def handleRANLIB(line):
    res = line.replace(RANLIB, LLVM_RANLIB)
    res = res.replace(".a", ".bc")
    res = res.replace(".o", ".bc")
    return res

if __name__ == "__main__":

    cmd_file = Path("/home/wanghaichi/ltp/ltp_make_cmd.txt")
    text = cmd_file.read_text().split("\n")

    #     text = '''
    # make -C "lib" \
    #     -f "/home/wanghaichi/kernelTCP/test_cases/ltp/lib/Makefile" \
    # 	-f "/home/wanghaichi/kernelTCP/test_cases/ltp/lib/Makefile" all
    # echo "AR libltp.a"
    # set -e; for dir in newlib_tests tests; do \
    #     make --no-print-directory -C $dir -f "/home/wanghaichi/kernelTCP/test_cases/ltp/lib/$dir/Makefile" all; \
    # done
    # set -e; for dir in newlib_tests tests; do \
    #     make --no-print-directory -C $dir -f "/home/wanghaichi/kernelTCP/test_cases/ltp/lib/$dir/Makefile" all; \
    # done
    #     '''.split("\n")

    cmd_list = []
    i = 0
    while i < len(text):
        # print(i)
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

    res = [handle_cmd_line(x) for x in cmd_list]
    res = [x for x in res if len(x) > 0]

    generated_text = ""
    debug = True
    line_number = 1
    root = "/home/wanghaichi/ltp/"
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
            if LLVM_CC in l or LLVM_AR in l or LLVM_RANLIB in l or LLVM_OBJCOPY in l:
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
            # for d in dependency:
            #     d = d.removeprefix("/home/wanghaichi/kernelTCP/test_cases/ltp/").strip()
            # if d not in dependency_bc.keys():
            # print("=========")
            # print(bc_file, cur_dir)
            # print(d)
            # dev_set.add(d)
            # print(d)
            # print("=========")
            # exit(-1)
    Path("combine_llvm_code.sh").write_text(combine_llvm_code_cmd)
    # for d in dev_set:
    #     if "lib" in d or "include" in d:
    #         print(d)

    # for l in filter_res:
    #     print(l)

    # for c in cmd_list:
    #
    #     cmd_set.add(c.split(" ")[0])
    #     # if c.startswith("done"):
    #     # #     print(c)
    # print(cmd_set)
    # print(res)