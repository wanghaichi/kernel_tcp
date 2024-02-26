import subprocess
import sys

from pathlib import Path

from liebes.CiObjects import DBConfig
from liebes.sql_helper import SQLHelper
import pexpect
import shutil


class ReproUtil:
    def __init__(self, home_dir, fs_image_root, port, linux_dir):
        self.home_dir = home_dir
        self.kernel_image_path = None
        self.work_linux_dir = None
        self.fs_image_root = self.home_dir + "/" + fs_image_root

        self.fs_image_path = self.fs_image_root + "/bullseye.img"
        self.ssh_key = self.fs_image_root + "/bullseye.id_rsa"

        self.vm_port = port
        # for copy only
        self.base_linux_dir = self.home_dir + "/" + linux_dir

        self.result_dir = None
        pass

    def run_command(self, cmd, cwd=None):
        if cwd is None:
            cwd = self.home_dir
        print("execute command: ", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print("execute command failed: ", cmd)
            print("error message: ", result.stderr)
        return result

    def prepare_linux_image(self, git_sha, base_config, extra_config, renew=False):
        work_linux_dir = Path(f"{self.home_dir}/repro_linuxs/{git_sha}")

        self.work_linux_dir = work_linux_dir
        self.kernel_image_path = work_linux_dir / "arch/x86/boot/bzImage"
        self.result_dir = f"{self.home_dir}/repro_results/{git_sha}"
        if not Path(self.result_dir).exists():
            Path(self.result_dir).mkdir()
        if Path(self.kernel_image_path).exists():
            if not renew:
                return True
            shutil.rmtree(work_linux_dir.absolute())
        # cp a new one
        cmd = f"cp -r {self.base_linux_dir} {work_linux_dir}"
        if self.run_command(cmd).returncode != 0:
            return False
        # checkout to the git sha
        cmd = "git checkout " + git_sha
        if self.run_command(cmd, work_linux_dir).returncode != 0:
            return False
        # clean the git repo
        cmd = "git clean -df"
        if self.run_command(cmd, work_linux_dir).returncode != 0:
            return False
        cmd = "make mrproper"
        if not self.run_command(cmd, work_linux_dir):
            return False
        # generate config
        cmd = "make " + base_config
        if self.run_command(cmd, work_linux_dir).returncode != 0:
            return False
        cmd = "make kvm_guest.config"
        if self.run_command(cmd, work_linux_dir).returncode != 0:
            return False
        Path(f"{work_linux_dir}/kernel/configs/temp.config").write_text(
            "\n".join(extra_config.split(" ")))
        cmd = "make temp.config"
        if self.run_command(cmd, work_linux_dir).returncode != 0:
            return False
        # make image
        cmd = "make -j`nproc`"
        if self.run_command(cmd, work_linux_dir).returncode != 0:
            return False

        # check the image is generated
        image_path = f"{work_linux_dir}/arch/x86/boot/bzImage"
        if not Path(image_path).exists():
            return False
        return True

    def start_qemu(self):
        cmd = f'qemu-system-x86_64 \
        -m 2G \
        -smp 2 \
        -kernel {self.kernel_image_path} \
        -append "console=ttyS0 root=/dev/sda earlyprintk=serial net.ifnames=0" \
        -drive file={self.fs_image_path},format=raw \
        -net user,host=10.0.2.10,hostfwd=tcp:127.0.0.1:{self.vm_port}-:22 \
        -net nic,model=e1000 \
        -enable-kvm \
        -nographic \
        -pidfile vm.pid \
        2>&1 | tee vm.log'
        print(cmd)
        vm_log_file = Path(self.result_dir) / "vm.log"
        # qemu_process = subprocess.Popen(cmd, shell=True, text=True, stdout=vm_log_file.open("w"),
        #                                 stderr=vm_log_file.open("w"))
        qemu_process = subprocess.Popen(cmd, shell=True, text=True)
        return qemu_process

    def execute_cmd_in_qemu(self, cmd):
        cmd = f'ssh -i {self.ssh_key} -p {self.vm_port} -o "StrictHostKeyChecking no" -t root@localhost "{cmd}"'
        res = self.run_command(cmd)
        return res

    def execute_ltp_testcase(self, testcase_name, save_result=True):
        cmd = f'cd /root/ltp_bin && ./runltp -s {testcase_name}'
        res = self.execute_cmd_in_qemu(cmd)
        if save_result:
            if res.returncode != 0:
                result_file = Path(self.result_dir) / f"{testcase_name}.err"
                result_file.write_text(res.stderr)
                print("save err result to ", result_file)
            else:
                result_file = Path(self.result_dir) / f"{testcase_name}.result"
                result_file.write_text(res.stdout)
                print("save succ result to ", result_file)

    def parse_result(self):
        pass

    def save_result(self):
        pass


if __name__ == '__main__':
    pass
    # !!! copy the following code to main.py or any python file located at the root of the project

    # sql = SQLHelper()
    # checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(11).all()
    # cia = CIAnalysis()
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # cia.reorder()
    # cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # cia.statistic_data()
    # cia.ci_objs = cia.ci_objs[1:]
    # print(len(cia.ci_objs))
    # print("start to reproduce each failed case")
    # for ci_obj in cia.ci_objs:
    #     for b in ci_obj.builds:
    #         print(b.instance.build_name, "===========")
    #         failed_testcases = [x for x in b.get_all_testcases() if x.is_failed()]
    #         if len(failed_testcases) == 0:
    #             continue
    #         config_list = re.split(r"\s+", b.instance.kconfig.replace("]", "").replace("[", ""))
    #         config_items = []
    #         for c in config_list:
    #             if c.startswith("http"):
    #                 config_detail = sql.session.query(DBConfig).filter(DBConfig.url == c).first()
    #                 for line in config_detail.content.split("\n"):
    #                     line = line.strip()
    #                     if line == "":
    #                         continue
    #                     if line.startswith("#"):
    #                         continue
    #                     config_items.append(line)
    #             if c.startswith("CONFIG_"):
    #                 config_items.append(c)
    #         config_cmd = " ".join(config_items)
    #         config_cmd += " CONFIG_KCOV=y CONFIG_DEBUG_INFO_DWARF4=y CONFIG_KASAN=y CONFIG_KASAN_INLINE=y CONFIG_CONFIGFS_FS=y CONFIG_SECURITYFS=y"
    #         base_config = "defconfig"
    #         reproutil = ReproUtil(
    #             home_dir="/home/wanghaichi",
    #             fs_image_root="kernel_images/ltp",
    #             port=8001,
    #             linux_dir="linux-1")
    #         res = reproutil.prepare_linux_image(
    #             git_sha=ci_obj.instance.git_sha,
    #             base_config=base_config,
    #             extra_config=config_cmd,
    #             # renew=True
    #         )
    #         if not res:
    #             print("failed to prepare linux image")
    #             exit(-1)
    #
    #         qemu_process = reproutil.start_qemu()
    #         print("start qemu vm")
    #         time.sleep(20)
    #         print("start to execute ltp testcases")
    #         for fc in failed_testcases:
    #             testcase_name = Path(fc.file_path).stem
    #             if (Path(reproutil.result_dir) / testcase_name / ".err").exists() or (Path(reproutil.result_dir) / testcase_name / ".result").exists():
    #                 print("skip", testcase_name)
    #                 continue
    #             reproutil.execute_ltp_testcase(testcase_name)
    #
    #         print("done")
    #         # print(output)
    #         #
    #         qemu_process.kill()
    #         # # if not res:
    #         # #     print("failed")
    #         # # else:
    #         # #     print("success")
    #         # exit(-1)
    # exit(-1)
