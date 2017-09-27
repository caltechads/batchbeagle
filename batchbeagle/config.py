import yaml

class Config(object):
    """
    This class reads our ``batchbeagle.yml`` file
    """

    def __init__(self, filename='batchbeagle.yml'):
        self.__raw = self.load_config(filename)

    def load_config(self, filename):
        with open(filename) as f:
            return yaml.load(f)

    def get_queue(self, queue_name):
        """
        Get the full config for the queue name ``queue_name`` from our parsed
        YAML file.

        :param queue_name: the name of a Batch Job Queue listed in our YAML file under the
        ``queues`` section

        :return:
        """
        for queue in self.__raw['queues']:
            if queue['name'] == queue_name:
                return queue
        raise KeyError