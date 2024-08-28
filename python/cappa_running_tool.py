from logging import Logger
import sys
import time

import paramiko

from utils.cli_parser import create_parser
from utils.logger_utils import LOGGER
from utils.config_file_reader import read_config_file
from utils.ssh_conn import ssh_connect_to_host, remote_cmd, ssh_connect_to_eccd, remote_cmd_on_eccd
from utils.cappa_constants import CAPPA_IMAGE, CAPPA_REPORT_DIR
from scp import SCPClient


def cappa_run_tool(args):
    """

    :param args:
    :return:
    """
    try:
        connection_info = {"ssh": True,
            "ssh_hostname": args.hostname,
            "ssh_username": args.username,
            "ssh_use_keyfile": args.use_keyfile,
            "ssh_keyfile": args.director_node_pem_file,
            "ssh_password": args.password
        }
        cappa_namespace = args.cappa_namespace
        eccd_ssh_client = ssh_connect_to_eccd(connection_info)

        # Kubeconfig is required by the cappactl binary provided by ADP so ensure it is uploaded to eccd.
        if args.upload_kubeconfig:
            upload_kubeconfig_to_eccd(eccd_ssh_client, args.kubeconfig)

        check_cappa_binary_is_on_eccd(eccd_ssh_client)
        check_cappa_database_doesnt_exist(eccd_ssh_client, database_name="cappa_project.db")

        if "true" in args.upload_kubeconfig:
            kubeconfig = args.kubeconfig
        else:
            kubeconfig = args.kubeconfig_location

        export_kubeconfig_on_eccd(eccd_ssh_client, kubeconfig)
        # cappa_state = cappactl_status(eccd_ssh_client, args.flag)
        # if cappa_state == 0:
        #     "cappa is not running"
        #     if args.flag:
        #         cappactl_stop(eccd_ssh_client)
        #     else:
        #         ask_user_to_stop_cappa(eccd_ssh_client)
        # elif cappa_state == 1:
        #     "cappa is not running but data is available"
        #     if args.flag:
        #         cappactl_stop(eccd_ssh_client)
        #     else:
        #         ask_user_to_stop_cappa(eccd_ssh_client)
        # elif cappa_state == 2:
        #     " cappa is currently running"
        #     if args.flag:
        #         cappactl_stop(eccd_ssh_client)
        #     else:
        #         ask_user_to_stop_cappa(eccd_ssh_client)
        #filterWriter(eccd_ssh_client, args.podname)
        cappactl_init(eccd_ssh_client, kubeconfig, cappa_namespace=cappa_namespace)
        cappactl_start(eccd_ssh_client, kubeconfig, cappa_namespace=cappa_namespace, timeout=int(args.cappa_running_time))
        cappactl_stop(eccd_ssh_client)
        copy_report(eccd_ssh_client)
    except:
        LOGGER.info("Error running cappa")
        raise

def stop_cappa(args):
    """

    :param args:
    :return:
    """
    try:
        connection_info = {"ssh": True,
            "ssh_hostname": args.hostname,
            "ssh_username": args.username,
            "ssh_use_keyfile": args.use_keyfile,
            "ssh_keyfile": args.director_node_pem_file,
            "ssh_password": args.password
        }
        eccd_ssh_client = ssh_connect_to_eccd(connection_info)
        cappactl_stop(eccd_ssh_client)
        copy_report(eccd_ssh_client)
    except:
        LOGGER.info("Error running cappa")
        raise

def filterWriter(eccd_ssh_client, podname):
    remove_command = "rm podname_filter.yaml"
    remote_cmd_on_eccd(eccd_ssh_client, remove_command)
    headerText = '''# Pods matching the include filter but not the
    # exclude filter will be recorded.
    #
    # Omitting the include filter or
    # specifying a single include selection of "*"
    # will record all pods except the ones matched
    # by the exclude filter
    '''
    includeFilter = \
'''
include_filter:
- ''' + "\"" + podname + '''-*\"
- \"work*\"
'''
    exclude_filter = \
'''exclude_filter:
- \"eric-*\"
'''
    writeYaml = "echo '" + headerText + includeFilter + exclude_filter + "' > /home/eccd/podname_filter.yaml"
    remote_cmd_on_eccd(eccd_ssh_client, writeYaml)

    set_podname_filter_command = "./cappactl set --seccomp_profile myseccomp_profile --podname_filter podname_filter.yaml"
    remote_cmd_on_eccd(eccd_ssh_client, set_podname_filter_command)


def export_kubeconfig_on_eccd(eccd_ssh_client, kubeconfig_file):
    try:
        LOGGER.info("Checking if cappa is installed")
        check_cmd = 'export KUBECONFIG={kubeconfig_file}'.format(kubeconfig_file=kubeconfig_file)
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, check_cmd)
        if stdout:
            LOGGER.info("Kubeconfig evironment variable set")
            LOGGER.info(stderr)
            LOGGER.info(stdout)
        else:
            LOGGER.info("Kubeconfig evironment variable set")
            LOGGER.info(stderr)
            LOGGER.info(stdout)
            return
    except:
        LOGGER.info("Error setting kubeconfig environment variable")
        raise

def upload_kubeconfig_to_eccd(eccd_ssh_client, kubeconfig):
    try:
        ftp_client=eccd_ssh_client.open_sftp()
        ftp_client.put(kubeconfig,kubeconfig)
        ftp_client.close()
        LOGGER.info("test")
    except Exception as e:
        LOGGER.info("failed to copy kubeconfig to eccd")

def check_cappa_binary_is_on_eccd(eccd_ssh_client):
    try:
        LOGGER.info("Checking if cappa is installed")
        check_cmd = 'ls -l cappactl'
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, check_cmd)
        if stdout:
            if "cappactl" in stdout:
                LOGGER.info("Cappa is installed")
            else:
                raise("Cappa is not installed")
        else:
            raise("Failed to get response from eccd, check network connection.")
    except Exception as e:
        LOGGER.info("Error running cappa")
        Logger.info(e)
        raise


def check_cappa_database_doesnt_exist(eccd_ssh_client, database_name="cappa_project.db"):
    """
        Checks if the cappa database exists and deletes it if found
        :param eccd_ssh_client: The Paramiko SSH client connection to eccd
        :return:
    """
    try:
        LOGGER.info("Checking if cappa database doesn't exist")
        database_check_command = "ls -l {database_name}".format(database_name=database_name)
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if not stdout:
            LOGGER.info(stderr)
            LOGGER.info("Cappa database doesn't exist")
            return

        LOGGER.info("Removing the cappa database")
        remove_file_from_eccd(eccd_ssh_client, file_to_remove="cappa_project.db")
    except:
        LOGGER.info("Error running cappa")
        raise
    LOGGER.info("Checking if cappa database exists")


def remove_file_from_eccd(eccd_ssh_client, file_to_remove="cappa_project.db"):
    """
        Checks if the cappa database exists and deletes it if found
        :param eccd_ssh_client: The Paramiko SSH client connection to eccd
        :return:
    """
    try:
        LOGGER.info("Removing {file_to_remove}".format(file_to_remove=file_to_remove))
        database_check_command = "rm {file_to_remove}".format(file_to_remove=file_to_remove)
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if stdout:
            LOGGER.info(stderr)
            LOGGER.info("{file_to_remove}")
        else:
            LOGGER.info("Deleting the cappa database to clear for new run")
            LOGGER.info(stdout)
            LOGGER.info(stderr)
            return True
    except Exception as e:
        LOGGER.info(e)
        LOGGER.info("Error removing {file_to_remove} (does the user have permission to do so?) ".format(file_to_remove=file_to_remove))
    LOGGER.info("Checking if cappa database exists")


def cappactl_init(eccd_ssh_client, kubeconfig, cappa_namespace="test-deployment-namespace"):
    """
        Checks if the cappa database exists
    :param eccd_ssh_client: The Paramiko SSH client connection to eccd
    :return:
    """
    
    try:
        LOGGER.info("Running the cappa init script")
        database_check_command = './cappactl init -D "CNF X func tests" -n {namespace} --kubeconfig={kubeconfig}'.format(namespace=cappa_namespace, kubeconfig=kubeconfig)
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if stdout:
            LOGGER.info("Cappa is installed")
            LOGGER.info(stderr)
            LOGGER.info(stdout)
        else:
            LOGGER.info(stderr)
            LOGGER.info(stdout)
            if "project database file cappa_project.db already exists" in stderr:
                remove_file_from_eccd(eccd_ssh_client, file_to_remove="cappa_project.db")
                cappactl_init(eccd_ssh_client, kubeconfig)
                cappactl_reset(eccd_ssh_client)
                
    except:
        LOGGER.info("Error running cappa")
        raise


def cappactl_status(eccd_ssh_client, flag=True):
    try:
        LOGGER.info("Checking the initial state of cappa.")
        database_check_command = './cappactl status'
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if stdout:
            LOGGER.info(stdout)
            if "cappa operational state: running" in stdout:
                return 2
            elif "Project state: DataAvailable" in stdout:
                return 1
            return 0
        else:
            LOGGER.info(stderr)
            if "ERROR:cappa:Pod list has changed" in stderr:
                return 3
            LOGGER.info("Error")
            return
    except:
        LOGGER.info("Error running cappa")
        raise


def cappactl_start(eccd_ssh_client, kubeconfig, database_name="cappa_project.db", cappa_namespace="test-deployment-namespace", timeout=450, flag=False):
    """
        Checks if the cappa database exists
    :param eccd_ssh_client: The Paramiko SSH client connection to eccd
    :return:
    """
    time.sleep(30)
    try:
        LOGGER.info("Running the cappa start script")
        database_check_command = './cappactl start'
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if stdout:
            LOGGER.info("Cappa init script executed succesfully")
            LOGGER.info(stderr)
            LOGGER.info(stdout)
        else:
            LOGGER.info("Failed to init cappa")
            LOGGER.info(stderr)
            if "State transition Started->Starting not allowed" in stderr:
                if flag:
                    cappactl_stop(eccd_ssh_client)
                else:
                    ask_user_to_stop_cappa(eccd_ssh_client)
            LOGGER.info(stdout)
            return
    except:
        LOGGER.info("Error running cappa")
        raise
    time.sleep(timeout)


def cappactl_reset(eccd_ssh_client):
    """
        Resets the state of cappa.
    :param eccd_ssh_client: The Paramiko SSH client connection to eccd
    :return:
    """
    
    try:
        LOGGER.info("Stopping cappa and generating the sqlite database output")
        database_check_command = './cappactl reset'
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if stdout:
            LOGGER.info("Cappa has been reset")
            LOGGER.info(stderr)
            LOGGER.info(stdout)
        else:
            LOGGER.info("Failed to reset cappa!")
            LOGGER.info(stderr)
            LOGGER.info(stdout)
            if "State transition DataAvailable->Resetting not allowed" in stderr:
                remove_file_from_eccd(eccd_ssh_client, file_to_remove="cappa_project.db")
                cappactl_reset(eccd_ssh_client)
            return
    except:
        LOGGER.info("Error stopping cappa")
        raise



def cappactl_stop(eccd_ssh_client):
    """
        Checks if the cappa database exists
    :param eccd_ssh_client: The Paramiko SSH client connection to eccd
    :return:
    """
    
    try:
        LOGGER.info("Stopping cappa and generating the sqlite database output")
        database_check_command = './cappactl stop'
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, database_check_command)
        if stdout:
            LOGGER.info("Cappa is stopped")
        else:
            LOGGER.info("Cappa has not been stop")
            return
    except:
        LOGGER.info("Error stopping cappa")
        raise


def ask_user_to_stop_cappa(eccd_ssh_client):
    message = "DO you want to stop cappa: yes/no?  "
    answer = str(input(message))
    if len(answer) == 0 or answer == "yes":
        cappactl_stop(eccd_ssh_client)
    elif answer == "no":
        return
    else:
        LOGGER.info("Invalid input")
        return

def copy_report(eccd_ssh_client, database_name="cappa_project.db"):
    """

    :param connection_info:
    :return:
    """
    time.sleep(10)
    with SCPClient(eccd_ssh_client.get_transport()) as scp:
        scp.get(database_name, CAPPA_REPORT_DIR + "report_db")
    time.sleep(10)
    LOGGER.info("Report has been copied to /var/tmp/report_db")

def main():
    """

    :return:
    """
    parser = create_parser()

    # Dict mapping cli command to function to handle it
    cmd_func_mapping = {'run_cappa': cappa_run_tool,
                        'stop_cappa': stop_cappa
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
