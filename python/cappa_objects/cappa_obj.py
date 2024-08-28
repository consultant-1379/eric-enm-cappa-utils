import os
import yaml

from utils.logger_utils import LOGGER
from utils.cappa_constants import SECURITY_CONTEXT_TEMPLATE_FILE


class CappaCapabilities:
    def __init__(self, pod_name, pod_data, privileged=False):
        """

        :param pod_data:
        :type pod_data: list
        """
        self._pod_name = pod_name
        self._capabilities = []
        self._security_context = {}

        self._add_capabilities(pod_data)
        self._load_template_security_context()
        self._update_security_context_privilege(privileged)

    def _add_capabilities(self, pod_info_list):
        """
        Function that iterates over a pods info list and extracts the
        capabilities
        :param pod_info_list: List of dicts containing capabilities csv info
        :return: None
        """
        # Capabilities are prefixed with 'CAP_' in cappa output
        prefix = 'CAP_'
        # pod_info_list is a list of dicts
        for cappa_info in pod_info_list:
            if cappa_info.get('CAP'):
                capability = cappa_info.get('CAP')
                # Remove prefix from capability
                if capability.startswith(prefix):
                    # Slice string to remove prefix
                    self.add_capability(capability[len(prefix):])
                else:
                    self.add_capability(capability)

    def add_capability(self, capability):
        """
        Function that adds a capability to the list of capabiltites.
        Duplicate entries will not be added.
        :param capability: The capability to add in string format.
        :return: None
        """
        if capability not in self._capabilities:
            self._capabilities.append(capability)

    def _load_template_security_context(self):
        """
        Function that loads security_context_template YAML file.
        :return:
        """
        with open(SECURITY_CONTEXT_TEMPLATE_FILE, 'r') as file:
            self._security_context = yaml.safe_load(file)

    def _update_security_context_privilege(self, privileged):
        """
        Function that updates the privileged flag of the securityContext.
        :param privileged: Boolean flag for the privileged setting.
        :return: None
        """
        if privileged:
            self._security_context['securityContext']['privileged'] = privileged

    def update_security_context_capabilities(self):
        """
        Function that updates the securityContext with the pod capabilities.
        :return: none
        """
        # If there are no capabilities remove the add field from the yaml
        if not self.capabilities:
            self._security_context['securityContext']['capabilities'].pop('add')
        else:
            self._security_context['securityContext']['capabilities']['add'] = self.capabilities

    def print_security_context(self):
        """
        Function that prints the generated pod securityContext to stdout.
        :return: None
        """
        print(yaml.dump(self._security_context))

    def write_security_context_to_file(self):
        """
        Function that writes the generated securityContext to file.
        :return: None
        """
        file_name = 'output/{0}/{0}_security_context.yaml'.format(self._pod_name)

        if os.path.exists(file_name):
            LOGGER.warning('File {0} already exists, overwriting'
                           .format(file_name))

        LOGGER.info('Writing security context to {0}'.format(file_name))

        with open(file_name, 'w') as yaml_file:
            yaml.dump(self._security_context, yaml_file)

    @property
    def capabilities(self):
        """
        Property that returns the list of capabilites.
        :return: List of pods capabilities.
        """
        return self._capabilities

    @property
    def pod_name(self):
        """
        Property that returns the pod name.
        :return: The pod name.
        """
        return self._pod_name
