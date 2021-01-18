import re
import graphviz
from graphviz import Digraph
from .sitemap import SiteMap

class Graph:

    def __init__(self, sitemap, name):
        self.sitemap = sitemap
        self.counter = 0
        self.subgraphs = {}
        self.edges = []
        self._name = name

    def make_edge(self, node1, node2, graph):
        '''Связывает два узла в графе'''
        node1 = self.clean_string(node1)
        node2 = self.clean_string(node2)
        if not node1 == node2 and \
        tuple(set([node1, node2])) not in self.edges:
            graph.edge(node1, node2)
            self.edges.append(tuple(set([node1, node2])))
            
    def _subgraph(self, graph, array, head):
        '''Строит под-граф'''
        if head in self.subgraphs:
            name = self.subgraphs[head]
            label = None
        else:
            name = f'cluster_{self.counter}'
            self.subgraphs[head] = name
            self.counter += 1
            label = head
        if label is not None and label.startswith('head_'):
            label = None
        with graph.subgraph(name=name) as c:
            c.attr(label=label)
            self.make_graph(c, array, head)
            
    @staticmethod
    def clean_string(line):
        """ Очищает строку от ненужных символов """
        return re.sub(r'[)(=]', '', line.strip())

    def make_graph(self, graph, elem, head):
        head = self.clean_string(head)

        if isinstance(elem, dict):
            node = elem['title']
            self.make_edge(head, node, graph)
            if 'children' in elem.keys() and elem['children'] is not None:
                for child in elem['children']:
                    self.make_graph(graph, child, node)
        elif isinstance(elem, list):
            if not head.startswith('head_'):
                head_2 = f'head_{self.counter}'
                graph.attr('node', fillcolor = 'white', fontcolor='white')
                self.make_edge(head, head_2, graph)
                graph.attr('node', style = 'filled', 
                            fillcolor='lightblue2', fontcolor='black')
                self.counter += 1
            else:
                head_2 = head
            for el in elem:
                self.make_graph(graph, el, head_2)

        
    def get_graph(self):
        """
        Метод вызова функции для построения графа
        Сохраняет граф в отдельном файле pdf
        """ 
        g = Digraph('G', filename=f'{self._name}.gv')
        g.attr(size='8',  page="8.5,11", ) 
        g.attr('node', style = 'filled', \
                fillcolor='lightblue2', fontcolor='black')
        
        self.make_graph(g, self.sitemap, '')
        g = g.unflatten(stagger=25)
        g.view()
        
    def __call__(self):
        """При вызове экземпляра класса показывает граф сайта"""
        self.get_graph()