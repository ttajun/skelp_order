
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from time import sleep

from common import logger, util, const
from common.queue import TaskResult, Task, TaskResultType
log = logger.make_logger(__name__)


class BoardNaverNews:

    def __init__(self):
        self.home = 'https://search.naver.com/search.naver'
        self.total_count = 0

    
    def parse(self, driver:WebDriver, info):
        ret = []
        word = info['word']
        keyword = info['keyword']
        domain = info['domain']
        start_p = info['start_p']

        start = util.date_to_str(start_p)

        con = const.Const

        try:
            url = info['url']
            parse_t = info['parse_t']
        except:
            url = (
                f'{self.home}?where=news&query=' +
                f'{word}' +
                f'&sm=tab_opt&sort=0&photo=0&field=0&pd=3' +
                f'&ds={start}' +
                f'&de={start}' +
                f'&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=' +
                f'&nso=so%3Ar%2Cp%3Afrom20220102to20220102&is_sug_officeid=0'
            )
            parse_t = 'new'
            self.total_count = 0

        ## access web
        try:
            print('*'*100)
            # print(f'word: {word}, type: {parse_t}, url: {url}')
            log.info(f'>>> {word}({parse_t}): {url}')
            driver.get(url)
            print('*'*100)
            sleep(3)
        except:
            raise

        if parse_t == 'more':
            css_section = '#main_pack > section.sc_new.sp_nnews._prs_rns > div > div.group_news > ul > li'
        else:
            css_section = '#main_pack > section.sc_new.sp_nnews._prs_nws > div > div.group_news > ul > li'

        ## parse article
        ele_sections = driver.find_elements(by=By.CSS_SELECTOR, value=css_section)
        for ele in ele_sections:

            # '관련뉴스 더 보기'가 존재하면 task 추가
            try: ele_more = ele.find_element(by=By.CSS_SELECTOR, value='a.news_more')
            except: ele_more = None

            # '뉴스 클러스터'가 존재시 parsing
            try: ele_cluster = ele.find_element(by=By.CSS_SELECTOR, value='div.news_cluster')
            except: ele_cluster = None

            if ele_more:
                # log.debug(f'{util.get_all_attr(driver, ele_more)}')
                m_info = {}
                m_info.update(info)
                m_info['url'] = ele_more.get_attribute('href')
                # print(f'>>> More: {m_info["url"]}')
                m_info['parse_t'] = 'more'
                m_task = Task(con.SITE_NAVER_NEWS, m_info)
                ret.append(TaskResult(TaskResultType.TASK, m_task))

            else:
                ele_art = ele.find_element(by=By.CSS_SELECTOR, value='a.news_tit')
                _url = ele_art.get_attribute('href')
                _title = ele_art.get_attribute('title')

                ele_press = ele.find_element(by=By.CSS_SELECTOR, value='a.info.press')
                _press = ele_press.text

                ele_content = ele.find_element(by=By.CSS_SELECTOR, value='div.news_dsc > div > a')
                _content = ele_content.text
                
                row = {}
                row['uid'] = util.hash_uid(f'{domain}_{_url}_{keyword}_{con.SITE_NAVER_NEWS}')
                row['url'] = _url
                row['title'] = _title
                row['c_cnt'] = 0
                row['source_text'] = keyword
                row['content'] = _content
                row['content2'] = ''
                row['category'] = 'news'
                row['source_site'] = con.SITE_NAVER_NEWS
                row['comment'] = ''
                row['r_cnt'] = 0
                row['i_date'] = util.today_str()
                row['bad'] = 0
                row['tag'] = _press
                row['script'] = ''
                row['c_date'] = start
                row['domain'] = domain
                ret.append(TaskResult(TaskResultType.ROW, row))

                self.total_count += 1
                log.info(f'> #{self.total_count} {start} {_press} : {_title} ')

                if ele_cluster:
                    ele_clusters = ele.find_elements(by=By.CSS_SELECTOR, value='div.news_cluster > ul > li')
                    for clu in ele_clusters:
                        ele_clu = clu.find_element(by=By.CSS_SELECTOR, value='span > a.elss.sub_tit')
                        # print(f'ele_clu: {util.get_all_attr(driver, ele_clu)}')
                        _url = ele_clu.get_attribute('href')
                        _title = ele_clu.get_attribute('title')

                        ele_clu_press = clu.find_element(by=By.CSS_SELECTOR, value='span > span > cite')
                        _press = ele_clu_press.text

                        row = {}
                        row['uid'] = util.hash_uid(f'{domain}_{_url}_{keyword}_{con.SITE_NAVER_NEWS}')
                        row['url'] = _url
                        row['title'] = _title
                        row['c_cnt'] = 0
                        row['source_text'] = keyword
                        row['content'] = ''
                        row['content2'] = ''
                        row['category'] = 'news'
                        row['source_site'] = con.SITE_NAVER_NEWS
                        row['comment'] = ''
                        row['r_cnt'] = 0
                        row['i_date'] = util.today_str()
                        row['bad'] = 0
                        row['tag'] = _press
                        row['script'] = ''
                        row['c_date'] = start
                        row['domain'] = domain
                        ret.append(TaskResult(TaskResultType.ROW, row))

                        self.total_count += 1
                        log.info(f'>> #{self.total_count} {start} {_press} : {_title} ')
            
            sleep(1)

        ## pagination
        try:
            ele_next = driver.find_element(by=By.CSS_SELECTOR, value='a.btn_next')
        except Exception as e:
            # log.info(f'다음페이지가 없습니다.')
            return ret

        if not ele_next: pass
        elif ele_next.get_attribute('aria-disabled') == 'false':
            # log.debug(f'{util.get_all_attr(driver, ele_next)}')
            n_info = {}
            n_info.update(info)
            n_info['url'] = ele_next.get_attribute('href')
            # print(f'>>> Next: {n_info["url"]}')
            if parse_t == 'more': n_info['parse_t'] = 'more'
            else: n_info['parse_t'] = 'next'
            n_task = Task(con.SITE_NAVER_NEWS, n_info)
            ret.append(TaskResult(TaskResultType.TASK, n_task))

        # input('!!! Check data. and Press Enter. <<< ')
        return ret

