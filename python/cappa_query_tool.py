import os
import sys
import yaml
from utils.logger_utils import LOGGER
from utils.cli_parser import create_parser
from report_generation.report_generator import generate_report
from utils.csv_reader import read_capabilities_csv
from cappa_objects.cappa_obj import CappaCapabilities

def get_pods_in_database(database="/var/tmp/report_db"):
    """
    Function that gets all podnames from the database.
    :param args: Command line arguments passed in.
    :return: None
    """
    import sqlite3
    conn = sqlite3.connect(database)
    with conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT DISTINCT r.NODE_NAME as PODNAME
            FROM CAPS_ASKED_FOR ca
            LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r ON r.NETWORK_NS = ca.NETWORK_NS AND r.PID_NS = ca.PID_NS AND r.GEN = ca.GEN AND r.NODE = ca.NODE
            LEFT JOIN CAPABILITIES c ON ca.CAP_ID = c.CAP_ID
            LEFT JOIN
                (SELECT 1 AS IA32, SYSCALL_NUM, NAME FROM SYSCALL32
                UNION
                SELECT 0 AS IA32, SYSCALL_NUM, NAME FROM SYSCALL) AS s
                ON s.SYSCALL_NUM = ca.SYSCALL_NUM AND s.IA32 = ca.IA32
            WHERE ca.CRED_OVERR_ACTIVE = 0 AND ca.RETVAL = 0 ORDER BY r.NODE_NAME, ca.EXECUTOR, ca.CAP_ID''')
        rows = cur.fetchall()
        pods = ""
        for row in rows:            
            if not "worker" in row[0]:
                pods = pods + row[0] + " "
        pods = pods[0: -1]
        pods = pods.split(" ")
        return pods


def write_distinct_capabilities(grouping, database="/var/tmp/report_db"):
    """
    Function that gets all podnames from the database.
    :param args: Command line arguments passed in.
    :return: None
    """
    import sqlite3
    conn = sqlite3.connect(database)
    with conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT DISTINCT r.NODE_NAME as PODNAME, c.NAME AS CAP
            FROM CAPS_ASKED_FOR ca
            LEFT JOIN (SELECT * FROM RUNC_HOOK_INFO GROUP BY NETWORK_NS, PID_NS, GEN, NODE) AS r ON r.NETWORK_NS = ca.NETWORK_NS AND r.PID_NS = ca.PID_NS AND r.GEN = ca.GEN AND r.NODE = ca.NODE
            LEFT JOIN CAPABILITIES c ON ca.CAP_ID = c.CAP_ID
            LEFT JOIN
                (SELECT 1 AS IA32, SYSCALL_NUM, NAME FROM SYSCALL32
                UNION
                SELECT 0 AS IA32, SYSCALL_NUM, NAME FROM SYSCALL) AS s
                ON s.SYSCALL_NUM = ca.SYSCALL_NUM AND s.IA32 = ca.IA32
            WHERE ca.CRED_OVERR_ACTIVE = 0 AND ca.RETVAL = 0 ORDER BY r.NODE_NAME, ca.EXECUTOR, ca.CAP_ID''')
        rows = cur.fetchall()
        capabilites = "---CAPABILITIES REQUIRED---"
        cursor = ""
        enm_pods = grouping.split(",")
        pod_len = len(enm_pods)
        cap_list = ""
        for row in rows:
            if cursor in enm_pods:
                if not cursor in row[0]:
                    cap_list = ""
                    cursor = row[0]
                    i = 0
                    while i < pod_len:
                        if enm_pods[i] in cursor:
                            cursor = enm_pods[i]
                            i = pod_len
                        i = i + 1
                    capabilites = capabilites + os.linesep
                    capabilites = capabilites + "---- " + cursor + " -----" + os.linesep
                    capabilites = capabilites + row[1] + os.linesep
                    cap_list = cap_list + row[1]
                else:
                    if not row[1] in cap_list:
                        capabilites = capabilites + row[1]  + os.linesep
                continue
            if row[0] != cursor:
                cursor = row[0]
                i = 0
                while i < pod_len:
                    if enm_pods[i] in cursor:
                        cursor = enm_pods[i]
                        i = pod_len
                    i = i + 1
                capabilites = capabilites + os.linesep
                capabilites = capabilites + "---- " + cursor + " -----" + os.linesep
                capabilites = capabilites + row[1] + os.linesep
            else:
                capabilites = capabilites + row[1]  + os.linesep
        LOGGER.info(capabilites)
        with open("output/just_the_capabilities.csv", "w") as csv_file:
            csv_file.write(capabilites)
                

def generate_cappa_report(args):
    """

    :param args:
    :return:
    """
    try:
        import os
        os.system("mkdir -p /var/tmp/cappa_exempt")
        write_distinct_capabilities(args.grouping)
        if "all" in args.pod_name:
            all_pods_except_cappa = get_pods_in_database()
            LOGGER.info(all_pods_except_cappa)           
            for pod in all_pods_except_cappa:
                try:
                    LOGGER.info('Generating HTML report from cappa output for {0}'.format(pod))
                    os.system("bin/cappa_extract.bsh -d /var/tmp/report_db -c {0}".format(pod))
                    os.system("mkdir -p output/{0}".format(pod))
                    generate_report(pod)
                    generate_pod_security_context(pod)
                    os.system("mkdir -p  /var/tmp/cappa_exempt/{0}".format(pod))
                    os.system("bin/cappa_exempt.bsh -d /var/tmp/cappa_out -c {0}".format(pod))
                    os.system("mv /var/tmp/cappa_exempt/{0}/granted-capabilities_cut.csv output/{0}/granted-capabilities_cut.csv".format(pod))
                except Exception as e:
                    LOGGER.info(e)
        else:
            try:
                LOGGER.info('Generating HTML report from cappa output for {0}'.format(args.pod_name))
                os.system("bin/cappa_extract.bsh -d /var/tmp/report_db -c " + args.pod_name)
                os.system("ls -l output")
                os.system("mkdir -p output/{0}".format(args.pod_name))
                generate_report(args.pod_name)
                generate_pod_security_context(args.pod_name)
                os.system("mkdir -p  /var/tmp/cappa_exempt/{0}".format(args.pod_name))
                os.system("bin/cappa_exempt.bsh -d /var/tmp/cappa_out -c {0}".format(args.pod_name))
                os.system("mv /var/tmp/cappa_exempt/{0}/granted-capabilities_cut.csv output/granted-capabilities_cut.csv".format(args.pod_name))
            except Exception as e:
                LOGGER.info(e)
    except:
        LOGGER.info("Error installing cappa tool")
        raise
    


def generate_pod_security_context(podname):
    """
    Function that generates a securityContext for a desired pod.
    :param args: Command line arguments passed in.
    :return: None
    """
    cappa_csv_data = read_capabilities_csv(podname)
    capabilities = [CappaCapabilities(pod_name, pod_data)
                    for pod_name, pod_data in cappa_csv_data.items()]

    desired_pod = None
    LOGGER.info(cappa_csv_data)

    for pod in capabilities:
        if pod.pod_name.startswith(podname):
            desired_pod = pod

    if not desired_pod:
        LOGGER.error('No data for pod {0} found'.format(podname))
        sys.exit(1)

    LOGGER.info('Generating securityContext for pod {0}'.format(podname))
    desired_pod.update_security_context_capabilities()
    desired_pod.print_security_context()
    desired_pod.write_security_context_to_file()


def yaml_as_dict(my_file):
    """

    :param my_file:
    :return:
    """
    my_dict = {}
    with open(my_file, 'rb') as fp:
        docs = yaml.safe_load_all(fp)
        for doc in docs:
            for key, value in doc.items():
                my_dict[key] = value
    return my_dict

def search_model_for_key_value(model, search_key):
    """

    :param model:
    :param search_key:
    :return:
    """
    for key, val in model.items():
        if str(key) == search_key:
            return val
        elif isinstance(val, dict):
            ret = search_model_for_key_value(val, search_key)
            if ret:
                return ret
    return None


def generate_pod_security_context_diff(args):
    """

    :return:
    """
    LOGGER.info(args)
    cappa_csv_data_old = read_capabilities_csv()
    capabilities = [CappaCapabilities(pod_name, pod_data)
                    for pod_name, pod_data in cappa_csv_data_old.items()]

    desired_pod = None

    for pod in capabilities:
        if pod.pod_name.startswith(args.pod_name):
            desired_pod = pod

    if not desired_pod:
        LOGGER.error('No data for pod {0} found'.format(args.pod_name))
        sys.exit(1)

    new_capabilities = set(desired_pod.capabilities)
    LOGGER.info("Required capabilities: {0}".format(new_capabilities))

    if not os.path.exists(args.pod_spec_file):
        LOGGER.error('Input file {0} does not exist'.format(args.pod_spec_file))
        raise FileNotFoundError()

    current_capabilities = search_model_for_key_value\
        (yaml_as_dict(args.pod_spec_file), "capabilities")
    current_capabilities_set = set(current_capabilities.get('add'))
    LOGGER.info("Current capabilities: {0}".format(current_capabilities_set))

    cap_diff = new_capabilities.symmetric_difference(current_capabilities_set)
    print('There is a mismatch in capabilities between pod version.\n'
          'The following capabilities are different:\n'
          '{diff}'.format(diff='\n'.join(cap_diff)))


def main():
    """

    :return:
    """
    parser = create_parser()

    # Dict mapping cli command to function to handle it
    cmd_func_mapping = {'generate_cappa_report': generate_cappa_report,
                        'gen_pod_sec_context_diff': generate_pod_security_context_diff
    }

    args = parser.parse_args()

    try:
        cmd_func = cmd_func_mapping[args.command]
    except KeyError as key_err:
        LOGGER.error('Missing command mapping for %s', key_err)
        sys.exit(1)

    cmd_func(args)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        raise err

