from argparse import ArgumentParser


def create_parser():
    """
    Function that creates an argument parser to handle command line input.
    :return: ArgumentParser.
    """
    arg_parser = ArgumentParser(description='Script to query cappa database')

    sub_parser = arg_parser.add_subparsers()

    # Generate a report from cappa CSVs
    gen_pod_report = sub_parser.add_parser('generate_cappa_report',
                                           help='Generate a report from the '
                                                'cappa output')
    gen_pod_report.add_argument('--pod_name',
                             help='Pod Name to filter on. e.g. lcmserv',
                             required=True)
    gen_pod_report.add_argument('--grouping',
                             help='Pod Name to group on. e.g. lcmserv',
                             required=True)
    gen_pod_report.set_defaults(command='generate_cappa_report')


    # Get the capabilities diff for a specific pod
    get_pod_caps_diff = sub_parser.add_parser('gen_pod_sec_context_diff',
                                              help='Generate a security '
                                                   'context difference')
    get_pod_caps_diff.set_defaults(command='gen_pod_sec_context_diff')
    get_pod_caps_diff.add_argument('--pod_name',
                                   help='Pod Name to filter on e.g. lcmserv',
                                   required=True)
    get_pod_caps_diff.add_argument('--pod_spec_file',
                                   help='Pod specification file',
                                   required=True)

    # Get cappa tool install on a worker node
    install_cappa = sub_parser.add_parser('install_cappa',
                                          help='Install cappa on a worker node')
    install_cappa.set_defaults(command='install_cappa')
    install_cappa.add_argument('--kubeconfig',
     help='The path to the kubeconfig file to use',
     required=True)
    install_cappa.add_argument('--upload_kubeconfig',
     help='Boolean true if it is required to upload kubeconfig to eccd',
     required=True)
    install_cappa.add_argument('--hostname',
     help='The hostname for eccd',
     required=True)      
    install_cappa.add_argument('--username',
     help='The username for eccd',
     required=True)
    install_cappa.add_argument('--password',
     help='The password for eccd',
     required=True)
    install_cappa.add_argument('--rpms',
     help='The rpms to install to run cappa',
     required=True)      
    install_cappa.add_argument('--kernel_rpms',
     help='The kernel rpms to install to run cappa',
     required=True)
    install_cappa.add_argument('--cappa_tgz',
     help='The helm chart tgz of cappa to install',
     required=True)
    install_cappa.add_argument('--cappa_namespace',
     help='The namespace to deploy cappa to this is not ENM please refer to ADP',
     required=True)
    install_cappa.add_argument('--use_keyfile',
     help='Boolean to use either a password or pem file to connect to eccd',
     required=True)
    install_cappa.add_argument('--director_node_pem_file',
     help='path to Pem File for your cENM environment',
     required=True)
    install_cappa.add_argument('--cappa_create_kernel_symlinks',
     help='Create symlink for inconsistent kernel version generally caused by PTF install',
     required=True)
    install_cappa.add_argument('--old_kernel_version',
     help='Old kernel version to remove',
     required=True)
    install_cappa.add_argument('--new_kernel_version',
     help='new kernel version to install',
     required=True)
    install_cappa.add_argument('--repo_path', help='Add any new repo path/paths')
    
    # Get cappa tool run on a worker node
    run_cappa = sub_parser.add_parser('run_cappa', help='Run cappa on a worker node')
    run_cappa.set_defaults(command='run_cappa')
    run_cappa.add_argument('--cappa_running_time',
     help='The minimum length of time to run cappa passed to time.sleep',
     required=True)
    run_cappa.add_argument('--kubeconfig',
     help='The path to the kubeconfig file to use',
     required=True)
    run_cappa.add_argument('--upload_kubeconfig',
     help='Boolean true if it is required to upload kubeconfig to eccd',
     required=True)
    run_cappa.add_argument('--kubeconfig_location',
     help='The default location of kubeconfig on eccd',
     required=True)
    run_cappa.add_argument('--hostname',
     help='The hostname for eccd',
     required=True)      
    run_cappa.add_argument('--username',
     help='The username for eccd',
     required=True)
    run_cappa.add_argument('--password',
     help='The password for eccd',
     required=True)
    run_cappa.add_argument('--cappa_namespace',
     help='The namespace to deploy cappa to this is not ENM please refer to ADP',
     required=True)
    run_cappa.add_argument('--use_keyfile',
     help='Boolean to use either a password or pem file to connect to eccd',
     required=True)
    run_cappa.add_argument('--director_node_pem_file',
     help='path to Pem File for your cENM environment',
     required=True)
    run_cappa.add_argument('--flag', help='Stop cappa if already running',
                           action='store_true')
    run_cappa.add_argument('--podname', help='podname for podnameFilter.yaml file',
                           required=True)

    stop_cappa = sub_parser.add_parser('stop_cappa', help='Run cappa on a worker node')
    stop_cappa.set_defaults(command='stop_cappa')
    stop_cappa.add_argument('--cappa_running_time',
     help='The minimum length of time to run cappa passed to time.sleep',
     required=True)
    stop_cappa.add_argument('--kubeconfig',
     help='The path to the kubeconfig file to use',
     required=True)
    stop_cappa.add_argument('--upload_kubeconfig',
     help='Boolean true if it is required to upload kubeconfig to eccd',
     required=True)
    stop_cappa.add_argument('--kubeconfig_location',
     help='The default location of kubeconfig on eccd',
     required=True)
    stop_cappa.add_argument('--hostname',
     help='The hostname for eccd',
     required=True)      
    stop_cappa.add_argument('--username',
     help='The username for eccd',
     required=True)
    stop_cappa.add_argument('--password',
     help='The password for eccd',
     required=True)
    stop_cappa.add_argument('--cappa_namespace',
     help='The namespace to deploy cappa to this is not ENM please refer to ADP',
     required=True)
    stop_cappa.add_argument('--use_keyfile',
     help='Boolean to use either a password or pem file to connect to eccd',
     required=True)
    stop_cappa.add_argument('--director_node_pem_file',
     help='path to Pem File for your cENM environment',
     required=True)
    stop_cappa.add_argument('--flag', help='Stop cappa if already running',
                           action='store_true')
    stop_cappa.add_argument('--podname', help='podname for podnameFilter.yaml file',
                           required=True)
    return arg_parser
