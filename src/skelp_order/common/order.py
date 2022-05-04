
from enum import Enum

from common import util, logger
log = logger.make_logger(__name__)


class LoopLevel(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


class Order:

    def __init__(self, opts_val):
        self.opts_val = opts_val
        self.order_file_name = f'{util.get_program_name()}.order'
        self.order_file_path = f'{util.get_program_path()}/{self.order_file_name}'

        old = self._load_order()
        if old['args'] == opts_val:
            order = old
        else:
            new = self._empty_order()
            new['args'] = opts_val
            order = new

        self.order = order
        log.info('#'*100)
        log.info(f'args: {order["args"]}')
        log.info(f'info: {order["info"]}')
        log.info(f'meta: {order["meta"]}')
        log.info('#'*100)


    def compare_order_by_list(self, level, new, _list:list):
        old = self._get_info_value(level)
        try:
            old_index = _list.index(old)
        except ValueError:
            self._update_info(level, new)
            return True
        except Exception as e:
            log.error(f'--- Unknown Exception. {e}')
            return False

        new_index = _list.index(new)

        if new_index > old_index: 
            self._update_info(level, new)
            return True
        elif new_index == old_index:
            return True
        else:
            return False

    def compare_order_by_value(self, level, new):
        old = self._get_info_value(level)
        # print(f'old: {repr(old)}, new: {repr(new)}')
        if not old or new > old:
            self._update_info(level, new)
            return True
        elif new == old:
            return True
        else:
            return False


    def meta_partno_get(self):
        meta = self.order['meta']
        return meta['part_no']

    
    def meta_partno_set(self, partno):
        meta = self.order['meta']
        meta['part_no'] = partno

    
    def meta_partcsv_get(self):
        meta = self.order['meta']
        return meta['part_csv']


    def meta_partcsv_append(self, csv):
        meta = self.order['meta']
        meta['part_csv'].append(csv)


    def meta_complete_get(self):
        meta = self.order['meta']
        return meta['is_complete']


    def meta_complete_set(self, com):
        meta = self.order['meta']
        meta['is_complete'] = com


    def args_basename_get(self):
        args:dict = self.order['args']
        name = ''
        for key, value in args.items():
            if value:
                if isinstance(value, list): name += f'{value[0]}_'
                else: name += f'{value}_'
            else:
                name += f'{key}_'
        return name


    def _get_info_value(self, level):
        try:
            info = self.order['info']
            return info[level]
        except Exception as e:
            return None


    def _update_info(self, level, value):
        info = self.order['info']
        info[level] = value
        # print(f' + update_info: {str(level.value)} => {value}')

        # 상위 level 값이 변하면 하위 level은 초기화 해야 한다.
        for l in LoopLevel:
            if l.value <= level.value: continue
            try:
                del(info[l])
            except:
                continue


    def _load_order(self):
        try:
            ret = util.load_pickle(self.order_file_path)
        except Exception as e:
            # log.error(f'{e}')
            ret = self._empty_order()
        return ret


    def _save_order(self):
        try:
            log.info(f'+++ Save Order: {self.order}')
            util.save_pickle(self.order, self.order_file_path)
        except Exception as e:
            log.error(f'{e}')


    def _get_order(self):
        return self.order


    def _empty_order(self):
        ret = {}
        ret['args'] = {}
        ret['info'] = {}
        ret['meta'] = {
            'part_no': 1,
            'is_complete': False,
            'part_csv': []
        }
        return ret

