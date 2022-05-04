
from enum import Enum
from queue import Queue

from common import util, logger, selenium
log = logger.make_logger(__name__)


class TaskResultType(Enum):
    TASK = 'task'
    ROW = 'row'


class Task:
    def __init__(self, site, info:dict):
        self.site = site
        self.info = info


class TaskResult:
    def __init__(self, type:TaskResultType, result):
        self.type = type
        self.result = result


class TaskQueue:
    def __init__(self):
        self._q = Queue()
        pass


    def push(self, tasks):
        for t in tasks:
            self._q.put(t)


    def run(self, sele:selenium.Selenium, reg):
        rows = []
        queue:Queue = self._q
        driver = sele.get_driver()

        while not queue.empty():

            task:Task = queue.get_nowait()
            site_class = reg[task.site]()
            info = task.info

            ret = site_class.parse(driver, info)
            for i in ret:
                i:TaskResult
                if i.type == TaskResultType.TASK:
                    queue.put(i.result)
                elif i.type == TaskResultType.ROW:
                    rows.append(i.result)
                else:
                    log.warn(f'Unknown task result type. {i.type}')

        return rows


    def get_tasks(self, task_result_list):
        ret = []
        for i in task_result_list:
            i:TaskResult
            if i.type == TaskResultType.TASK:
                ret.append(i.result)
        return ret


