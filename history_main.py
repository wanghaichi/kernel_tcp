from liebes.CiObjects import DBCheckout, Checkout
from liebes.analysis import CIAnalysis
from liebes.ci_logger import logger
from liebes.sql_helper import SQLHelper
from liebes.tcp_approach.information_achieve import HistoryInformationManager

if __name__ == "__main__":
    
    sql = SQLHelper()
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).all()

    # # checkouts = sql.session.query(DBCheckout).limit(10).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    cia.filter_job("COMBINE_SAME_CONFIG")
    cia.filter_job("CHOOSE_ONE_BUILD")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.ci_objs = cia.ci_objs[1:]
    cia.statistic_data()

    # achieve history data
    logger.info("start to achieve history data")
    history_information_manager = HistoryInformationManager(cia)
    history_information_manager.extract()

    history_information_manager.save()
    exit(-1)

    ehelper = EHelper()
    # for k, v in history_information_manager.failed_count.items():
    #     print(k, v)
    # print(history_information_manager.executed_count[i])

    # for i in range(len(cia.ci_objs)):
    apfd_arr = []
    for i in range(len(cia.ci_objs)):
        if i == 0:
            continue
        ci_obj = cia.ci_objs[i]
        faults_arr = []
        his_arr = []
        all_cases = ci_obj.get_all_testcases()
        for j in range(len(all_cases)):
            tc = all_cases[j]
            if tc.is_failed():
                faults_arr.append(j)
            time_since_last_failure = 0
            if history_information_manager.last_failure_time[tc.file_path][i] is not None:
                time_since_last_failure = ci_obj.instance.git_commit_datetime - \
                                          history_information_manager.last_failure_time[tc.file_path][i]
                time_since_last_failure = time_since_last_failure.days
            time_since_last_execute = 0
            if history_information_manager.last_executed_time[tc.file_path][i] is not None:
                time_since_last_execute = ci_obj.instance.git_commit_datetime - \
                                          history_information_manager.last_executed_time[tc.file_path][i]
                time_since_last_execute = time_since_last_execute.days
            if history_information_manager.executed_count[tc.file_path][i] == 0:
                failed_rate = 0
            else:
                failed_rate = history_information_manager.failed_count[tc.file_path][i] / \
                              history_information_manager.executed_count[tc.file_path][i]
            his_arr.append([
                history_information_manager.failed_count[tc.file_path][i],
                time_since_last_failure,
                failed_rate,
                history_information_manager.exd_value[tc.file_path][i],
                history_information_manager.rocket_value[tc.file_path][i],
                time_since_last_execute
            ])
        if len(faults_arr) == 0:
            continue
        # print(his_arr)
        order_arr = np.argsort(np.array(his_arr), axis=0)[::-1]
        order_arr = np.transpose(order_arr)
        # print(order_arr.shape)
        apfd = []
        for j in range(6):
            apfd.append(ehelper.APFD(faults_arr, order_arr[j].tolist()))
        logger.info(ci_obj.instance.git_sha)
        logger.info("APFD:")
        for j in range(6):
            logger.info(apfd[j])
        apfd_arr.append(apfd)
        # print(his_arr)
        # exit(-1)
    logger.info("APFD avg:")
    for i in range(6):
        logger.info(np.average([x[i] for x in apfd_arr]))
