import shutil
import subprocess
from pathlib import Path

from liebes.ci_logger import logger
from datetime import datetime


class ReproUtil:
    def __init__(self, home_dir, fs_image_root, port, linux_dir, ltp_dir, pid_index=0, vm_mem=10):
        self.home_dir = home_dir
        self.kernel_image_path = None
        self.work_linux_dir = None
        self.fs_image_root = self.home_dir + "/" + fs_image_root
        self.fs_image_path = self.fs_image_root + "/bullseye.img"
        self.ssh_key = self.fs_image_root + "/bullseye.id_rsa"
        self.pid_index = pid_index
        self.pid_file = self.home_dir + f"/vm_{pid_index}.pid"
        self.vm_port = port
        # for copy only
        self.base_linux_dir = self.home_dir + "/" + linux_dir

        self.result_dir = None
        self.ltp_dir = self.home_dir + "/" + ltp_dir
        self.ltp_bin = None
        self.ltp_version = None
        self.vm_mem = vm_mem
        self.vm_ltp_bin = "/root/ltp_bin"
        self.vm_selftest_bin = "/root/selftest_bin"
        self.selftest_bin = None
        self.qemu_process = None
        pass

    def run_command(self, cmd, cwd=None):
        if cwd is None:
            cwd = self.home_dir
        logger.info(f"execute command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode != 0:
            logger.error(f"execute command failed: {cmd}")
            logger.error(f"error message: {result.stderr}")
        return result

    def prepare_selftest_binary(self):
        '''
        some necessary packages are required to build selftest
        sudo apt install libpopt-dev
        sudo apt install libasound2-dev
        sudo apt install libcap-ng-dev
        sudo apt install libfuse-dev
        '''

        if self.work_linux_dir is None:
            logger.error("linux image is not prepared")
            return False
        if (self.work_linux_dir / "selftest_build").exists():
            self.selftest_bin = self.work_linux_dir / "selftest_build"
            logger.info(f"selftest bin is located at {self.selftest_bin.absolute()}")
            return True

        cmd = "mkdir selftest_build"
        if self.run_command(cmd, cwd=self.work_linux_dir).returncode != 0:
            return False
        cmd = "make headers"
        if self.run_command(cmd, cwd=self.work_linux_dir).returncode != 0:
            return False
        cmd = f"make -C tools/testing/selftests install INSTALL_PATH={(self.work_linux_dir / 'selftest_build').absolute()}"
        if self.run_command(cmd, cwd=self.work_linux_dir).returncode != 0:
            return False
        self.selftest_bin = self.work_linux_dir / "selftest_build"
        logger.info(f"selftest bin is located at {self.selftest_bin.absolute()}")
        return True

    def prepare_ltp_binary(self, git_sha):
        # make sure all dependencies are installed
        # check the result of ./configure in ltp
        # if some dependencies are missing, install them

        # step0. update ltp to the latest version
        # cmd = "git pull origin master"
        # if self.run_command(cmd, self.ltp_dir).returncode != 0:
        #     return False

        # step1. checkout ltp to the specific git sha
        self.ltp_version = git_sha
        work_ltp_dir = Path(f"{self.home_dir}/repro_ltps/{git_sha}")
        if work_ltp_dir.exists() and (work_ltp_dir / "build").exists():
            self.ltp_bin = work_ltp_dir / "build"
            logger.info(f"ltp bin is located at {self.ltp_bin.absolute()}")
            return True
        # work_ltp_dir.mkdir(parents=True)
        cmd = f"cp -r {self.ltp_dir} {work_ltp_dir}"
        if self.run_command(cmd).returncode != 0:
            return False
        cmd = "git clean -df && git checkout " + git_sha + " && git clean -df"
        if self.run_command(cmd, work_ltp_dir).returncode != 0:
            return False
        # step2. make whole ltp into binary, the location of the binary is ./build
        cmd = f"make autotools && mkdir build && ./configure --prefix={work_ltp_dir / 'build'}"
        if self.run_command(cmd, work_ltp_dir).returncode != 0:
            return False
        cmd = f"make -k -j`nproc` && make -k install"
        if self.run_command(cmd, work_ltp_dir).returncode != 0:
            return False
        self.ltp_bin = work_ltp_dir / "build"
        logger.info(f"ltp bin is located at {work_ltp_dir / 'build'}")
        return True

    def copy_essential_files_to_vm(self):
        # copy kernel config
        cmd = f"scp -i {self.ssh_key} -P {self.vm_port} -o \"StrictHostKeyChecking no\" -r {self.work_linux_dir}/.config root@localhost:/root/config"
        if self.run_command(cmd).returncode != 0:
            return False

        cmd = f"gzip -f config "
        if self.execute_cmd_in_qemu(cmd).returncode != 0:
            return False

        # copy kernel modules
        cmd = f"mkdir -p /lib/modules/\$(uname -r)/"
        if self.execute_cmd_in_qemu(cmd).returncode != 0:
            return False
        cmd = f"scp -i {self.ssh_key} -P {self.vm_port} -o \"StrictHostKeyChecking no\" -r {self.work_linux_dir}/modules.builtin \"root@localhost:/lib/modules/\$(uname -r)/\""
        if self.run_command(cmd).returncode != 0:
            return False

        # need to determine the gcov path first. :(
        gcov_path = f"/sys/kernel/debug/gcov{self.work_linux_dir}"
        cmd = f"ls {gcov_path}"
        res = self.execute_cmd_in_qemu(cmd)
        if res.returncode != 0:
            if "/data" in gcov_path:
                gcov_path = gcov_path.replace("/data", "/home")
            elif "/home" in gcov_path:
                gcov_path = gcov_path.replace("/home", "/data")
            cmd = f"ls {gcov_path}"
            res = self.execute_cmd_in_qemu(cmd)
            if res.returncode != 0:
                logger.error(f"failed to determine gcov path: {self.work_linux_dir}")

        # copy coverage collecting script to vm
        shell_content = f'''#!/bin/bash -e

        DEST=$1
        GCDA={gcov_path}

        if [ -z "$DEST" ] ; then
            echo "Usage: $0 <output.tar.gz>" >&2
            exit 1
        fi

        TEMPDIR=$(mktemp -d)
        echo Collecting data..
        find $GCDA -type d -exec mkdir -p $TEMPDIR/\\{{\\}} \\;
        find $GCDA -name '*.gcda' -exec sh -c 'cat < $0 > '$TEMPDIR'/$0' {{}} \\;
        # find $GCDA -name '*.gcno' -exec sh -c 'cp -d $0 '$TEMPDIR'/$0' {{}} \\;
        tar czf $DEST -C $TEMPDIR/$GCDA .
        rm -rf $TEMPDIR

        echo "$DEST successfully created, copy to build system and unpack with:"
        echo "  tar xfz $DEST "
                '''
        script_file = Path(self.work_linux_dir) / "collect_coverage.sh"
        script_file.write_text(shell_content)
        script_file.chmod(0o755)
        cmd = f"scp -i {self.ssh_key} -P {self.vm_port} -o \"StrictHostKeyChecking no\" {script_file.absolute()} root@localhost:/root/collect_coverage.sh"
        if self.run_command(cmd).returncode != 0:
            return False

    def copy_ltp_bin_to_vm(self):
        # check if the ltp binary is already there
        cmd = "cat /root/ltp_bin/Version"
        res = self.execute_cmd_in_qemu(cmd)
        if res.returncode == 0 and res.stdout.strip() == self.ltp_version:
            logger.info(f"{res.stdout.strip()}")
            logger.info(f"ltp binary is already in the vm, tag version: {self.ltp_version}")
            return True

        cmd = f"rm -rf {self.vm_ltp_bin}"
        if self.execute_cmd_in_qemu(cmd).returncode != 0:
            return False
        cmd = f"scp -i {self.ssh_key} -P {self.vm_port} -o \"StrictHostKeyChecking no\" -r {self.ltp_bin} root@localhost:/root/ltp_bin"
        if self.run_command(cmd).returncode != 0:
            return False
        return True

    def copy_selftest_bin_to_vm(self):
        cmd = f"rm -rf {self.vm_selftest_bin}"
        if self.execute_cmd_in_qemu(cmd).returncode != 0:
            return False
        cmd = f"scp -i {self.ssh_key} -P {self.vm_port} -o \"StrictHostKeyChecking no\" -r {self.selftest_bin} root@localhost:/root/selftest_bin"
        if self.run_command(cmd).returncode != 0:
            return False
        return True

    def prepare_linux_image(self, git_sha, base_config, extra_config, renew=False):
        work_linux_dir = Path(f"{self.home_dir}/repro_linuxs/{git_sha}")

        self.work_linux_dir = work_linux_dir
        self.kernel_image_path = work_linux_dir / "arch/x86/boot/bzImage"
        self.result_dir = f"{self.home_dir}/repro_results/{git_sha}"
        if not Path(self.result_dir).exists():
            Path(self.result_dir).mkdir()
        cmd = f"ssh-keygen -R [localhost]:{self.vm_port}"
        self.run_command(cmd)
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
        cmd = "rm -rf .git"
        self.run_command(cmd, work_linux_dir)

        # TODO  INSTALL_MOD_PATH=/home/wanghaichi/linux-stable-rc-test/modules_install make modules_install
        # add module install command !!!
        # note this command will add a symbolic link to whole kernel dir, do not use scp directly
        # remove the symbolic link first which will be located at /lib/modules/$(uname -r)/build
        # make modules
        # make modules_install
        return True

    def start_qemu(self):
        # kill the previous qemu process if exists
        if Path(self.pid_file).exists():
            pid = Path(self.pid_file).read_text().strip()
            cmd = f"kill -9 {pid}"
            self.run_command(cmd)
            Path(self.pid_file).unlink()

        cmd = f'qemu-system-x86_64 \
        -m {self.vm_mem}G \
        -smp 2 \
        -kernel {self.kernel_image_path} \
        -append "console=ttyS0 root=/dev/sda earlyprintk=serial net.ifnames=0" \
        -drive file={self.fs_image_path},format=raw \
        -net user,host=10.0.2.10,hostfwd=tcp:127.0.0.1:{self.vm_port}-:22 \
        -net nic,model=e1000 \
        -enable-kvm \
        -nographic \
        -pidfile {self.pid_file} \
        2>&1 | tee vm_{self.pid_index}.log'
        logger.info(cmd)
        # vm_log_file = Path(self.result_dir) / "vm.log"
        # qemu_process = subprocess.Popen(cmd, shell=True, text=True, stdout=vm_log_file.open("w"),
        #                                 stderr=vm_log_file.open("w"))
        qemu_process = subprocess.Popen(cmd, shell=True, text=True)
        self.qemu_process = qemu_process
        return

    def execute_cmd_in_qemu(self, cmd):
        cmd = f'ssh -i {self.ssh_key} -p {self.vm_port} -o "StrictHostKeyChecking no" -t root@localhost "{cmd}"'
        res = self.run_command(cmd)
        return res

    def collect_coverage(self):
        pass

    def execute_testcase(self, testcase_name, testcase_type, timeout=30, save_result=True, collect_coverage=False):
        if collect_coverage:
            cmd = f'lcov -z'
            res = self.execute_cmd_in_qemu(cmd)
            if res.returncode != 0:
                logger.error("failed to reset lcov")
                return
        # collect time cost
        start_time = datetime.now()
        if testcase_type == "ltp":
            cmd = f'cd /root/ltp_bin && LTP_TIMEOUT_MUL=5 KCONFIG_PATH=/root/config.gz timeout {timeout}s ./runltp -s {testcase_name}'
        elif testcase_type == "selftest":
            cmd = f'cd /root/selftest_bin && timeout {timeout}s ./run_kselftest.sh -t {testcase_name}'
        else:
            logger.error(f"testcase type {testcase_type} not supported, use [ltp | selftest] instead")
            return
        res = self.execute_cmd_in_qemu(cmd)
        cost_time = datetime.now() - start_time
        logger.info(f"test case {testcase_name} cost time: {cost_time}")
        if save_result:
            if res.returncode != 0:
                if res.returncode == 124:
                    logger.error("timeout")
                    result_file = Path(self.result_dir) / f"{testcase_name}.err"
                    result_file.write_text(res.stdout + res.stderr + f"\nTime cost: {cost_time}s\n")
                    logger.error(f"save err result to {result_file}")
                else:
                    result_file = Path(self.result_dir) / f"{testcase_name}.result"
                    result_file.write_text(res.stdout + res.stderr + f"\nTime cost: {cost_time}s\n")
                    logger.info(f"save fail result to {result_file}")
            else:
                result_file = Path(self.result_dir) / f"{testcase_name}.result"
                result_file.write_text(res.stdout + f"\nTime cost: {cost_time}s\n")
                logger.info(f"save succ result to {result_file}")
        if collect_coverage:
            if Path(f"{self.work_linux_dir}/{testcase_name}_coverage.tar.gz").exists():
                logger.info(f"coverage file {testcase_name}_coverage.tar.gz already exists")
                return
            cmd = f'cd /root && ./collect_coverage.sh /root/{testcase_name}_coverage.tar.gz'
            res = self.execute_cmd_in_qemu(cmd)
            if res.returncode != 0:
                logger.error("failed to collect coverage")
                return
            cmd = (
                f'scp -i {self.ssh_key} -P {self.vm_port} -o "StrictHostKeyChecking no" root@localhost:/root/{testcase_name}_coverage.tar.gz {self.work_linux_dir}/{testcase_name}_coverage.tar.gz')
            res = self.run_command(cmd)
            if res.returncode != 0:
                logger.error("failed to copy coverage")
                return
            cmd = f"cd /root && rm -f /root/{testcase_name}_coverage.tar.gz"
            self.execute_cmd_in_qemu(cmd)

    def kill_qemu(self):
        pid_file = Path(self.pid_file)
        if pid_file.exists():
            pid = pid_file.read_text().strip()
            cmd = f"kill -9 {pid}"
            self.run_command(cmd)
            pid_file.unlink()

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
