import llvmlite.binding as llvm
from pathlib import Path

if __name__ == "__main__":

    # Load the LLVM bitcode file
    bitcode_file = Path("/home/wanghaichi/linux/built-in.bc")
    llvm.initialize()
    module = llvm.parse_bitcode(bitcode_file.read_bytes())
    for f in module.functions:
        if "native_make_pmd" in f.name:
            print("================")
            print(f.name)
            print(f.is_function)
            print(f.is_instruction)
            print(f.is_block)
            for ins in f.instructions:
                print(ins.name)
            print("==========")


    # Load the LLVM bitcode file
