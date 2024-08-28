import paramiko
import time
from utils.logger_utils import LOGGER

def ssh_connect_to_eccd(connection_info):
    """

    :param connection_info:
    :return:
    """
    ssh_client = paramiko.SSHClient()
    paramiko.util.log_to_file("filename.log")
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if "true" in connection_info["ssh_use_keyfile"]:
        ssh_key = paramiko.RSAKey.from_private_key_file\
            (connection_info["ssh_keyfile"])
        ssh_client.connect(hostname=connection_info["ssh_hostname"],
                           username=connection_info["ssh_username"],
                           pkey=ssh_key)
    else:
        ssh_client.connect(hostname=connection_info["ssh_hostname"],
                           username=connection_info["ssh_username"],
                           password=connection_info["ssh_password"])
    return ssh_client

def ssh_connect_to_worker_node(connection_info, ssh_client):
    """

    :param connection_info:
    :return:
    """
    sshtransport = ssh_client.get_transport()

    dest_addr = (connection_info["ssh_workernode_hostname"], 22)
    local_addr = (connection_info["ssh_hostname"], 22)
    sshchannel = sshtransport.open_channel("direct-tcpip", dest_addr, local_addr)

    ssh_client1 = paramiko.SSHClient()
    ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_key = paramiko.RSAKey.from_private_key_file\
        (connection_info["ssh_keyfile"])
    ssh_client1.connect(hostname=connection_info["ssh_workernode_hostname"],
                        username=connection_info["ssh_username"], pkey=ssh_key,
                        sock=sshchannel)

    return ssh_client1

def ssh_connect_to_host(connection_info):
    """

    :param connection_info:
    :return:
    """
    ssh_client = paramiko.SSHClient()
    paramiko.util.log_to_file("filename.log")
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if connection_info["ssh_use_keyfile"]:
        ssh_key = paramiko.RSAKey.from_private_key_file\
            (connection_info["ssh_keyfile"])
        ssh_client.connect(hostname=connection_info["ssh_hostname"],
                           username=connection_info["ssh_username"],
                           pkey=ssh_key)
    else:
        ssh_client.connect(hostname=connection_info["ssh_hostname"],
                           username=connection_info["ssh_username"],
                           password=connection_info["ssh_password"])
    sshtransport = ssh_client.get_transport()
    dest_addr = (connection_info["ssh_workernode_hostname"], 22)
    local_addr = (connection_info["ssh_hostname"], 22)
    sshchannel = sshtransport.open_channel("direct-tcpip", dest_addr, local_addr)

    ssh_client1 = paramiko.SSHClient()
    ssh_client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_key = paramiko.RSAKey.from_private_key_file\
        (connection_info["ssh_keyfile"])
    ssh_client1.connect(hostname=connection_info["ssh_workernode_hostname"],
                        username=connection_info["ssh_username"], pkey=ssh_key,
                        sock=sshchannel)

    return ssh_client1


def remote_cmd_on_eccd(eccd_ssh_client, command, send_msg=True, timeout=0, log_output=True, eccd=False):
    """

    :param connection_info:
    :param command:
    :param send_msg:
    :param timeout:
    :param log_output:
    :return:
    """
    try:
        stdin, stdout, stderr = eccd_ssh_client.exec_command(command)
        if send_msg:
            stdin.write('\n')
            stdin.flush()

        if timeout:
            endtime = time.time() + timeout
            while not stdout.channel.eof_received:
                time.sleep(0.5)
                if time.time() > endtime:
                    LOGGER.info("Command has timed out")
                    stdout.channel.close()
                    break

        out = stdout.read().decode("utf8")
        err = stderr.read().decode("utf8")
        ret_code = stdout.channel.recv_exit_status()
        print('testing')
        print(out)
    except Exception as err:
        LOGGER.exception('Exception when running command: %s', err)
        time.sleep(5)
        

    LOGGER.debug("Command exit code: %s", ret_code)
    if log_output:
        LOGGER.debug("Command output:\n%s", out)
        if err:
            LOGGER.debug("Command stderr:\n%s", err)

    return ret_code, out, err


def remote_command_on_worker_node(connection_info, ssh_client, command, send_msg=True, timeout=0, log_output=True, eccd=False):
    """

    :param connection_info:
    :param command:
    :param send_msg:
    :param timeout:
    :param log_output:
    :return:
    """
    
    ssh = ssh_connect_to_worker_node(connection_info, ssh_client)

    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        if send_msg:
            stdin.write('\n')
            stdin.flush()

        if timeout:
            endtime = time.time() + timeout
            while not stdout.channel.eof_received:
                time.sleep(0.5)
                if time.time() > endtime:
                    LOGGER.info("Command has timed out")
                    stdout.channel.close()
                    break

        stdout.channel.set_combine_stderr(True)
        out = stdout.read().decode("utf8")
        err = stderr.read().decode("utf8")
        ret_code = stdout.channel.recv_exit_status()
        print('testing')
        print(out)
    except Exception as err:
        LOGGER.exception('Exception when running command: %s', err)
        time.sleep(5)
    finally:
        ssh.close()
        

    LOGGER.debug("Command exit code: %s", ret_code)
    if log_output:
        LOGGER.debug("Command output:\n%s", out)
        if err:
            LOGGER.debug("Command stderr:\n%s", err)

    return ret_code, out, err


def remote_cmd(connection_info, command, send_msg=True, timeout=0, log_output=True, eccd=False):
    """

    :param connection_info:
    :param command:
    :param send_msg:
    :param timeout:
    :param log_output:
    :return:
    """

    ssh = ssh_connect_to_host(connection_info)

    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        if send_msg:
            stdin.write('\n')
            stdin.flush()

        if timeout:
            endtime = time.time() + timeout
            while not stdout.channel.eof_received:
                time.sleep(0.5)
                if time.time() > endtime:
                    LOGGER.info("Command has timed out")
                    stdout.channel.close()
                    break

        out = stdout.read().decode("utf8")
        err = stderr.read().decode("utf8")
        ret_code = stdout.channel.recv_exit_status()
        print('testing')
        print(out)
    except Exception as err:
        LOGGER.exception('Exception when running command: %s', err)
        time.sleep(5)
    finally:
        ssh.close()
        

    LOGGER.debug("Command exit code: %s", ret_code)
    if log_output:
        LOGGER.debug("Command output:\n%s", out)
        if err:
            LOGGER.debug("Command stderr:\n%s", err)

    return ret_code, out, err