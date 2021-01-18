import time
from time import sleep
import threading
import multiprocessing 

import re
import sys
import requests
from bs4 import BeautifulSoup

from collections import defaultdict
import copy


class SiteMap:
    
    def __init__(self, url):
        self._name = self.get_sitename(url)
        self.main_url = url
        self.url = None
        self.sitemap = None
        self.url_processed = []
        self.queue = []
        self.url_counter = 0
        
    @staticmethod
    def get_sitename(url):
        return re.search(r'https?://(.*?)\.\w*', url).group(1)
        
    def get_page(self, url):
        """
        Загружает страницу по ссылке url и возвращает дерево BeautifulSoup - 
        документ в виде вложенной структуры данных
        """
        response = requests.get(url)
        return BeautifulSoup(response.content)
        
    def clean_list(self, array):
        """
        Избавляет массив от пустых элементов 
        - None или пустых листов - 
        и избавляет массив от излишней вложенности
        """
        if not isinstance(array, list):
            return array
        for idx, elem in enumerate(array):
            if isinstance(elem, list) and \
            (all(map(lambda x: x is None, elem)) or len(elem) == 0):
                array[idx] = None  
        if not isinstance(array, dict):
            array = [item for item in array \
                if item is not None and item != []]
        for idx, elem in enumerate(array):
            if isinstance(elem, list):
                array[idx] = self.clean_list(elem)
        if len(array) == 1:
            array = array[0]
        if not isinstance(array, dict):
            array = [item for item in array \
                if item is not None and item != []]
        return array

    @staticmethod
    def has_children(elem):
        """Проверяет, есть ли у элемента html-страницы потомки"""
        try:
            return len(list(elem.children)) > 0
        except AttributeError:
            return False

    @staticmethod    
    def find_name(elem):
        """
        Проверяет, еcть ли среди потомков элемента 
        дочерний элемент NavigableString
        """
        elems = [elem] + list(elem.descendants)
        for elem in elems:
            try:
                name = elem.string.strip()
                if len(name) > 0:
                    return name
            except AttributeError:
                pass
        return
      
    def get_href(self, elem):
        """
        Проверяет, содержит ли элемент ссылку и возвращает найденную ссылку 
        и ее текстовое представление
        """
        try:
            name = self.find_name(elem)
            href = elem['href']
            if not href.startswith('https'):
                href = self.url + href
            return {'title': name, 'url': href} if len(name) > 0 else None
        except:
            return
      
    def _map_short(self, elem):
        """
        Строит карту сайта, содержащую ссылки и их текстовые представления
        """
        href = self.get_href(elem)
        if href:
            self.url_counter += 1
            return href
        elif self.has_children(elem):
            for el in elem.children:
                try:
                    if el.text == elem.text:
                        return self._map_short(el)
                except:
                    pass
            # На странице ссылки часто бывают объединены в группы, но они не
            # подчиняются логике parent - child, т.к. это дети одного порядка 
            # для анализируемой страницы, поэтому для обозначения группировки
            # ссылок будет использовать просто массив
            my_map = [self._map_short(el) for el in elem.children]
            my_map = [el for el in my_map if el is not None and el != []]
            if len(my_map) == 1:
                return my_map[0]
            return my_map if len(my_map) > 0 else None   
    
    def get_map(self, url=None):
        """
        Метод вызова функции для создания карты сайта
        """
        self.url = self.main_url if url is None else url
        page = self.get_page(self.url)     
        my_map = self._map_short(page)
        my_map = self.clean_list(my_map)
        
        if url is None:
            self.sitemap = {'title': self._name, 
                            'url': self.main_url,
                            'children': my_map}
        else:
            return my_map
        
    def url_number(self):
        """Показывает количество собранных ссылок"""
        return self.url_counter

    def make_node(self, node):
        """Вспомогательная функция"""
        try:
            node['children'] = self.get_map(node['url'])
        except:
            node['children'] = None

        
    def make_proc(self, x):
        """Запускает многопоточность"""
        pr1 = threading.Thread(target=self.make_node, args=(x,))
        pr1.start()
        pr1.join()
        return pr1

    def rec_help(self, node):
        """Вспомогательная функция"""
        if isinstance(node, list):
            for child in node:
                self.rec_help(child)
        elif isinstance(node, dict) and 'children' in node.keys() and \
                node['children'] is not None:
            for child in node['children']:
                self.rec_help(child)
        elif isinstance(node, dict) and 'children' not in node.keys() and \
                self._name in node['url']:
            pr = self.make_proc(node)
            self.queue.append(pr)
            self.url_processed.append(node['url'])
        
    def recursion(self, depth=1):
        """
        Идет вглубь сайта
        depth - "глубина", на которую нужно опуститься
        """
        if self.sitemap is None:
            self.get_map()
        cntr = 0
        for i in range(depth):
            if i > 0 and len(self.url_processed) == cntr:
                break
            cntr = len(self.url_processed)
            tree = copy.copy(self.sitemap)
            self.rec_help(tree)
            self.sitemap = tree
            while len(self.queue) > 0:
                self.queue = [el for el in self.queue if el.is_alive()]
