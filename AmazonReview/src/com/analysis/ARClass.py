'''
Created on Nov 25, 2017

@author: prasun
'''

class Item_Info(object):
    '''
    Class for storing all the information of items.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._id = None
        self._asin = None
        self._title = None
        self._group = None
        self._similar = None
        self._categories = None
        self._review_score = None
        
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def asin(self):
        return self._asin
    
    @asin.setter
    def asin(self, value):
        self._asin = value
        
    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        self._title = value
        
    @property
    def group(self):
        return self._group
    
    @group.setter
    def group(self, value):
        self._group = value
        
    @property
    def salesrank(self):
        return self._salesrank
    
    @salesrank.setter
    def salesrank(self, value):
        self._salesrank = value
        
    @property
    def similar(self):
        return self._similar
    
    @similar.setter
    def similar(self, value):
        self._similar = value
        
    @property
    def categories(self):
        return self._categories
    
    @categories.setter
    def categories(self, value):
        self._categories = value
            
    @property
    def review_score(self):
        return self._review_score
    
    @review_score.setter
    def review_score(self, value):
        self._review_score = value