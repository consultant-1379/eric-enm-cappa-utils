import os
from sys import platform as platform



def find_kubectl_binary_name():
    """ Get the name of the kubernetes binary to use"""
    if platform == "linux" or platform == "linux2":
        binary_name = "kubectl"
    elif platform == "darwin":
        binary_name = "kubectl"
    elif platform == "win32" or platform == "win64":
        binary_name = "kubectl.exe"
    else:
        raise Exception("Unknown Platform")
    return binary_name


def kubernetes_command_builder(command, kubernetes_config):
    """ We are using a kubectl binary that has been 'baked-into'
    the scripts this function will find the path
        to the binary stored in the the binaries folder.
        :param command: The kubernetes command
        :param kubernetes_config: The name of the kubernetes config file
        :return: The command + path to the kubetcl binary """
    parent_directory_path = os.path.abspath\
        (os.path.join(os.path.dirname(__file__), ".."))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) + \
           r"\binaries\\" + find_kubectl_binary_name() + " --kubeconfig=" + \
           parent_directory_path + "\\kubeconfig\\" + kubernetes_config + command