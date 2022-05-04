
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from time import sleep

from common import logger, util
from common.queue import TaskResult, Task, TaskResultType
log = logger.make_logger(__name__)

SITE_NAVER_NEWS = 'naverNews'


class BoardNaverNews:

    def __init__(self):
        self.home = 'https://search.naver.com/search.naver'

    
    def parse(self, driver:WebDriver, info):
        ret = []
        word = info['word']
        start_p = info['start_p']
        start = util.date_to_str(start_p)

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

        ## access web
        try:
            driver.get(url)
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

            # '관련뉴스 더 보기'가 존재하면 재귀함수 호출
            try:
                ele_more = ele.find_element(by=By.CSS_SELECTOR, value='a.news_more')
            except:
                ele_more = None

            if ele_more:
                log.debug(f'{util.get_all_attr(driver, ele_more)}')
                m_info = {}
                m_info.update(info)
                m_info['url'] = self.home + ele_more.get_attribute('href')
                m_info['parse_t'] = 'more'
                m_task = Task(SITE_NAVER_NEWS, m_info)
                ret.append(TaskResult(TaskResultType.TASK, m_task))

            else:
                ele_art = ele.find_element(by=By.CSS_SELECTOR, value='a.news_tit')
                _url = ele_art.get_attribute('href')
                print('-'*50)
                print(f'>>> url: {_url}')
                print(ele_art.text)
                print('-'*50)
            
            sleep(1)

        ## pagination
        try:
            ele_next = driver.find_element(by=By.CSS_SELECTOR, value='a.btn_next')
        except Exception as e:
            log.debug(e)
            return ret

        if not ele_next: pass
        elif ele_next.get_attribute('aria-disabled') == 'false':
            log.debug(f'{util.get_all_attr(driver, ele_next)}')
            n_info = {}
            n_info.update(info)
            n_info['url'] = self.home + ele_next.get_attribute('href')
            n_info['parse_t'] = 'next'
            n_task = Task(SITE_NAVER_NEWS, n_info)
            ret.append(TaskResult(TaskResultType.TASK, n_task))

        return ret

