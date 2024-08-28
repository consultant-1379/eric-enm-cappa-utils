CAPPA_CSV_DIR = '/var/tmp/cappa_out/'
CAPPA_REPORT_DIR = '/var/tmp/'
CAPABILITIES_CSV = CAPPA_CSV_DIR + 'granted-capabilities.csv'

SECURITY_CONTEXT_TEMPLATE_FILE = 'python/utils/security_context_template.yaml'
HTML_REPORT = 'output/cappa_report.html'
CSS_FILE = 'python/report_generation/css.txt'
CAPPA_IMAGE = 'armdocker.rnd.ericsson.se/proj-cappa/cappa/alpha:0.1.1'

RPMS_LIST = ['audit', 'kernel-macros', 'kernel-devel', 'bcc-tools',
             'libelf-devel', 'python3-future', 'bcc-docs',
             'kernel-default-devel']


REPO_NAME = ['SLE-15-SP1-Module-Development-Tools/ sles_module_development_tools',
             'SLE-15-SP1-Module-Basesystem/ sles_module_Basesystem',
             'SLE-15-SP1-Module-Basesystem-Updates/ sles_module_basesystem_updates',
             'SLE-15-SP1-Product-SLES_SAP-Updates/ sles_SAP_updates']
