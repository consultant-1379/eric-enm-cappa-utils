from ast import Raise
from os import symlink
import sys, time
from traceback import print_tb
from utils.logger_utils import LOGGER
from utils.ssh_conn import remote_cmd, ssh_connect_to_eccd, remote_command_on_worker_node, remote_cmd_on_eccd
from utils.cli_parser import create_parser
from utils.cappa_constants import RPMS_LIST, REPO_NAME
from utils.config_file_reader import read_config_file
import configparser
import codecs

def cappa_install(args):
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
        rpms = args.rpms.split(',')
        kernel_rpms = args.kernel_rpms.split(',')
        cappa_tgz = args.cappa_tgz
        cappa_namespace = args.cappa_namespace
        symlinks = args.cappa_create_kernel_symlinks
        old_kernel_version = args.old_kernel_version
        new_kernel_verion = args.new_kernel_version

        LOGGER.info("Testing")
        eccd_ssh_client = ssh_connect_to_eccd(connection_info)

        # Kubeconfig is required by the cappactl binary provided by ADP so ensure it is uploaded to eccd.
        if args.upload_kubeconfig:
            upload_kubeconfig_to_eccd(eccd_ssh_client, args.kubeconfig)
        # Add required repositories and Install RPMs 
        install_rpms(eccd_ssh_client, connection_info, rpms, kernel_rpms, symlinks, old_kernel_version, new_kernel_verion)
        # Install the cappa helm chart.
        install_helm_charts(eccd_ssh_client, cappa_namespace, cappa_tgz)
        # Download cappactl binary from a pod.
        cappa_pods = get_pods_in_namespace(eccd_ssh_client, cappa_namespace)
        copy_cappactl_from_pod(eccd_ssh_client, cappa_namespace)

    except:
        LOGGER.info("Error installing cappa tool")
        raise


def get_worker_nodes(eccd_ssh_client):
    LOGGER.info("Attempting to get the list of worker_nodes")
    cmd = " kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type==\"InternalIP\")].address}'"
    stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, cmd)
    if stdout:
        worker_nodes = stdout.split(" ")
        LOGGER.info(worker_nodes)
        return worker_nodes
    else:
        LOGGER.info("Couldn't list the worker nodes")
        raise


def install_rpms(eccd_ssh_client, connection_info, rpms, kernel_rpms, symlinks, old_kernel_version, new_kernel_version):
    """
        Install the required RPMS listing in the config
        :param connection_info: The SSH connection info
        :return:
    """
    worker_nodes = get_worker_nodes(eccd_ssh_client)
    repo_url = 'https://arm.sero.gic.ericsson.se/artifactory/proj-suse-repos-rpm-local/SLE15/'
   
    for worker_node in worker_nodes:
        connection_info["ssh_workernode_hostname"] = worker_node
        cmd = "echo '--- Adding ERICSSON RPM Repos ---\n'"
        for repo in REPO_NAME:
            cmd = cmd + "sudo su -c 'zypper addrepo -C -G -f {repo_url}{repo}' || true && \n".format(repo_url=repo_url, repo=repo)

        cmd = "echo '--- Adding RPM from list ---\n'"
        for rpm in rpms:
            cmd = cmd + "sudo zypper --non-interactive install --oldpackage {rpm} && \n".format(rpm=rpm, repo=repo)

        cmd = "echo '--- Adding RPM from list ---\n'"
        for kernel_rpm in kernel_rpms:
            cmd = cmd + "sudo zypper --non-interactive install --oldpackage {kernel_rpm} && \n".format(kernel_rpm=kernel_rpm, repo=repo)

        if "True" in symlinks:
            # Create required symlinks as workaround for non-consistent installed kernel (PTF)
            # https://confluence-oss.seli.wh.rnd.internal.ericsson.com/display/TCSC/Investigations+into+the+state+of+cappa+on+enm154
            cmd = cmd + "sudo zypper --non-interactive rm {old_kernel_version} && \n".format(old_kernel_version=old_kernel_version)
            cmd = cmd + "sudo rm -rf /lib/modules/{old_kernel_version} && \n".format(old_kernel_version=old_kernel_version)
            cmd = cmd + "sudo ln -s /lib/modules/{new_kernel_version} /lib/modules/{old_kernel_version} && \n".format(old_kernel_version=old_kernel_version, new_kernel_version=new_kernel_version)
        
        cmd = cmd + "echo done"
        LOGGER.info("command =" + cmd)
        try:
            stdin, stdout, stderr = remote_command_on_worker_node(connection_info, eccd_ssh_client, cmd)
            if not stdout:
                LOGGER.info(stdout)
                LOGGER.info(stderr)
                LOGGER.info("Repos added")
            else:
                LOGGER.info(stderr)
        except Exception as e:
            LOGGER.info(e)
            LOGGER.info("Error adding repos")
        
def install_helm_charts(eccd_ssh_client, cappa_namespace, cappa_tgz, timeout=400):
    """
        Install cappa helm chart to the required namespace
        :param connection_info: The SSH connection info
        :return:
    """
    CAPPA_REPO = "https://arm.sero.gic.ericsson.se/artifactory/proj-eric-cbo-cappa-drop-helm/"
    cmd = "helm install eric-cbo-cappa {cappa_repo}/{cappa_tgz} --namespace {cappa_namespace}".format(cappa_repo=CAPPA_REPO, cappa_tgz=cappa_tgz, cappa_namespace=cappa_namespace)

    print("command =" + cmd)
    try:
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, cmd)
        if not stdout:
            LOGGER.info(stdout)
            LOGGER.info(stderr)
        else:
            LOGGER.info(stderr)
    except Exception as e:
        LOGGER.info(e)
    time.sleep(timeout)



def copy_cappactl_from_pod(eccd_ssh_client, cappa_namespace):
    """
        Copy the cappactl binary from the cappa pod.
        :param eccd_ssh_client: The SSH client connection to eccd
        :return:
    """
    cappa_pods = get_pods_in_namespace(eccd_ssh_client, cappa_namespace)    
    cmd = "kubectl cp {namespace}/{cappa_podname}:/cappa/cappactl cappactl && chmod +x cappactl".format(namespace=cappa_namespace, cappa_podname=cappa_pods.split(' ')[0])
    LOGGER.info("command =" + cmd)
    try:
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, cmd)
        if not stdout:
            LOGGER.info(stdout)
            LOGGER.info(stderr)
        else:
            LOGGER.info(stderr)
    except Exception as e:
        LOGGER.info(e)



def upload_kubeconfig_to_eccd(eccd_ssh_client, kubeconfig):
    try:
        ftp_client=eccd_ssh_client.open_sftp()
        ftp_client.put(kubeconfig,kubeconfig)
        ftp_client.close()
        LOGGER.info("test")
    except Exception as e:
        LOGGER.info("failed to copy kubeconfig to eccd")



def get_pods_in_namespace(eccd_ssh_client, cappa_namespace):
    """
        Returns a list of pods in the suggested namespace
        :param eccd_ssh_client:  The SSH client connection to eccd
        :return:
    """
    cmd = "kubectl get pods -n=" + cappa_namespace + " --output=jsonpath={.items..metadata.name}"
    LOGGER.info("command =" + cmd)
    try:
        stdin, stdout, stderr = remote_cmd_on_eccd(eccd_ssh_client, cmd)
        if not stdout:
            LOGGER.info(stdout)
            LOGGER.info(stderr)
        else:
            LOGGER.info(stderr)
        return stdout
    except Exception as e:
        LOGGER.info(e)


def main():
    """

    :return:
    """
    parser = create_parser()

    # Dict mapping cli command to function to handle it
    cmd_func_mapping = {'install_cappa': cappa_install}

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

