import configparser


def read_config_file(config_file_name):
    """Reads the input configuration file"""
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(config_file_name)
    return config