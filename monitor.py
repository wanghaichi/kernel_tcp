from pathlib import Path
import psutil

def is_process_running(pid):
    # 检查指定进程ID是否存在
    if psutil.pid_exists(pid):
        # 获取进程信息
        process = psutil.Process(pid)
        # 判断进程是否正在运行
        if process.is_running():
            return True
    return False


if __name__ == "__main__":
    total_vm = 10

    pid_root = Path("pids")
    not_start_tasks = []
    for i in range(1, total_vm + 1):
        log_name = "Unknown"
        if (pid_root / f"{i}.log").exists():
            log_name = (pid_root / f"{i}.log").read_text()

        if not (pid_root / f"{i}.pid").exists():
            print(f"task {i} not start ! | log: {log_name}")
            not_start_tasks.append(i)
            continue
        pid = (pid_root / f"{i}.pid").read_text()
        pid = pid.strip()
        if is_process_running(int(pid)):
            print(f"task {i} is running ! Pid: {pid}  | log: {log_name}")
        else:
            print(f"task {i} is not running !  | log: {log_name}")
            not_start_tasks.append(i)
    print(not_start_tasks)
    vm_pid_root = Path("/home/wanghaichi")
    vm_need_close = []
    for i in not_start_tasks:
        vm_id_path = Path(vm_pid_root / f"vm_{i}.pid")
        if not vm_id_path.exists():
            continue
        vm_id = vm_id_path.read_text()
        if is_process_running(int(vm_id)):
            print(f"vm {i} is running ! Pid: {vm_id}! Need kill!")
            vm_need_close.append(vm_id)
    if len(vm_need_close) > 0:
        print("execute the following command to kill the vm:")
        for i in vm_need_close:
            print(f"kill -9 {i}")

    if len(not_start_tasks) > 0:
        print("execute the following command to restart the task:")
        for i in not_start_tasks:
            port = 8000 + int(i)
            print(f"python temp.py --vmport={port} --vmindex={i}  --vmnum={total_vm} --file_image=file_images/ltp-{i}  --ltp_repo=ltp_mirror --linux_repo=linux --home_dir=/data/wanghaichi")


    pass
