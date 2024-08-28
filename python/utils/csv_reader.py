import os
from csv import DictReader

from utils.logger_utils import LOGGER
from utils.cappa_constants import CAPABILITIES_CSV, CAPPA_CSV_DIR


def read_capabilities_csv(podname):
    """
    Function that reads in the granted-capabilities CSV file.
    :return: Dictionary with pod name as key and pod data as values.
    """
    LOGGER.info('Reading capability data from {0}'.format(CAPPA_CSV_DIR + podname + '/granted-capabilities.csv'))

    if not os.path.exists(CAPPA_CSV_DIR + podname + '/granted-capabilities.csv'):
        LOGGER.error('Input file {0} does not exist'.format(CAPPA_CSV_DIR + podname + '/granted-capabilities.csv'))
        raise FileNotFoundError()

    capabilities_dict = {}

    with open(CAPPA_CSV_DIR + podname + '/granted-capabilities.csv', 'r') as cappa_csv:
        csv_dict_reader = DictReader(cappa_csv)
        for row in csv_dict_reader:
            pod_key = row.get('PODNAME')

            if pod_key not in capabilities_dict.keys():
                capabilities_dict.update({pod_key: []})

            temp_dict = row
            temp_dict.pop('PODNAME')
            capabilities_dict.get(pod_key).append(temp_dict)

    return capabilities_dict


def read_files_csv():
    """

    :return:
    """
    raise NotImplemented


def read_granted_stacks_csv():
    """

    :return:
    """
    raise NotImplemented


def read_interesting_sockets_csv():
    """

    :return:
    """
    raise NotImplemented


def read_root_processes_csv():
    """

    :return:
    """
    raise NotImplemented


def read_runc_hook_csv():
    """

    :return:
    """
    raise NotImplemented


def read_sockets_csv():
    """

    :return:
    """
    raise NotImplemented
