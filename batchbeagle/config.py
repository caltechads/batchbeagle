import yaml
import re
import os

class Config(object):
    """
    This class reads our ``batchbeagle.yml`` file

    Allowed variable substitutions:
    * ``${env.<environment var>}```: If the environment variable
      ``<environment var>`` exists in our environment, replace this with
      the value of that environment variable.
    """

    ENVIRONMENT_RE = re.compile('\$\{env\.(\w+)\}')

    def __init__(self, filename='batchbeagle.yml', import_env=False, interpolate=True):
        self.__raw = self.load_config(filename)
        self.import_env = import_env
        self.environ = None
        if interpolate:
            self.replace()

    def get_yaml(self):
        return self.__raw

    def load_config(self, filename):
        with open(filename) as f:
            return yaml.load(f)

    def replace(self):

        """
        Do variable replacement in all strings in the YAML data for
        each listed job_definitions under the ``job_definitions:`` section.
        """

        for job in self.__raw['job_definitions']:
            self.environ = {}
            if self.import_env:
                self.__load_environ()
            self.__do_dict(job)

    def __load_environ(self):
        for key in os.environ.keys():
            self.environ[key] = os.getenv(key)

    def __replace(self, raw, key, value):
        if isinstance(value, dict):
            self.__do_dict(value)
        elif any(isinstance(value, t) for t in (list, tuple)):
            self.__do_list(value)
        elif isinstance(value, str):
            self.__do_string(raw, key, value)

    def __env_replace(self, key):
        value = self.environ.get(key, "${env.%s}" % key)
        return value

    def __do_dict(self, raw):
        for key, value in raw.items():
            self.__replace(raw, key, value)

    def __do_string(self, raw, key, value):
        m = self.ENVIRONMENT_RE.findall(value)
        if m:
            for match_key in m:
                value = value.replace("${env.%s}" % match_key, self.__env_replace(match_key))
                raw[key] = value

    def __do_list(self, raw):
        for i, value in enumerate(raw):
            self.__replace(raw, i, value)
