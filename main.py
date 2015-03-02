#!/usr/bin/env python

from random import sample
import sys
import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Rectangle
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty, \
                            BooleanProperty

class Blank(Button):
    
    index = ListProperty([0, 0])
    count = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(Blank, self).__init__(**kwargs)
    

class Mine(Button):
    
    index = ListProperty([0, 0])
    count = NumericProperty(0) # not really necessary
    
    def __init__(self, **kwargs):
        super(Mine, self).__init__(**kwargs)
    
            
class RootWidget(Screen):
    
    sides = ListProperty([0, 0])
    mine_count = NumericProperty(0)
    result_text = StringProperty('')
    colours = {1: 'FFFFFF', 2: '1E90FF', 3: 'FFA500', 4: '008000', 5: 'A52A2A',
                6: '932AA5', 7: 'A52C2A', 8: '2D2AA5'}
    
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
                    
    def on_enter(self):
        self.__init__()
        # get settings from Menu
        self.sides = self.manager.menu.sides
        self.mine_count = self.manager.menu.mine_count
        side_x = self.sides[1]
        side_y = self.sides[0]
        self.area = side_x * side_y
        
        self.grid = self.ids.grid
        self.grid.cols = side_x
        self.grid.rows = side_y
        
        # generate random mine indices
        mines = sample(xrange(self.area), self.mine_count)
        
        # populate grid with mines and blanks
        col, row = -1, 0
        for i in xrange(self.area):
            if col == (side_x - 1):
                col = 0
                row += 1
            else:
                col += 1
                
            if i not in mines:
                b = Blank(index=[col, row])
            else:
                b = Mine(index=[col, row])
            self.grid.add_widget(b)
            
        # record mine, blank and safe blank indices
        self.all_btns = [c.index for c in self.grid.children]
        self.mines = [c.index for c in self.grid.children if isinstance(c, Mine)]
        self.blanks = [c.index for c in self.grid.children if isinstance(c, Blank)]
        
        # give each btn an 'adjacent mines count'
        for x, y in self.all_btns:
            btn = self.get_child_by_index([x, y])
            for index in self.field(x, y):
                if index in self.mines:
                    btn.count += 1
                    
    def on_leave(self):
        self.clear_widgets()
        self.result_text = ""
        
    def field(self, x, y):
        # indices of all possible positions surrounding a button
        field = [[x-1, y], [x+1, y], [x, y+1], [x, y-1],
            [x+1, y+1], [x-1, y-1], [x+1, y-1], [x-1, y+1]]
        
        # return only indices actually existing on the grid    
        get = self.get_child_by_index        
        return [i for i in field if i in self.all_btns and get(i).disabled == False]
            
    def sweep(self, instance):
        if instance.index in self.mines: # It's a mine! You lose
            self.game_result() 
            
        instance.disabled = True
        
        pressed = sum(1 for c in self.grid.children if c.disabled == True)
        # if total buttons - buttons pressed = no. of mines ... you win!
        if self.area - pressed == self.mine_count:
            self.game_result(win=True)
            
        if instance.count > 0: # a base case
            instance.text = "[color={}]{}[/color]".format(self.colours[instance.count], str(instance.count))
            instance.disabled = True
            return
        else:
            x, y = instance.index
        
            for index in self.field(x, y):
                if index not in self.mines:
                    blank = self.get_child_by_index(index)
                    blank.disable = True
                    if blank.count > 0:
                        blank.text = "[color={}]{}[/color]".format(self.colours[blank.count], str(blank.count))
                    self.sweep(blank) # method calls itself for each surrounding
                                      # button index
                    
    def get_child_by_index(self, index):
        for child in self.grid.children:
            if child.index == index:
                return child
                    
    def back_to_menu(self, instance):
        self.manager.current = "menu_screen"
        
    def game_result(self, win=False):
        if win:
            self.result_text = "You Win!"
        else:
            self.result_text = "You Lost!"
            
        for m in self.mines:
            mine = self.get_child_by_index(m)
            mine.text = ""
            mine.disabled = True
            with mine.canvas.after:
                Rectangle(source='mine.png', size=mine.size, pos=mine.pos)
                
        for b in self.blanks:
            blank = self.get_child_by_index(b)
            if blank.disabled == False:
                blank.background_disabled_normal = 'normal.png'
                blank.disabled = True
                
    def on_size(self, instance, value):
        print instance
        print value
        print self.size
                
class Menu(Screen):
    
    sides = ListProperty([0, 0])
    mine_count = NumericProperty(0)
    x = NumericProperty(0)
    y = NumericProperty(0)
    
    def set_sides(self, a, b, res=None):
        if res:
            self.res = res
        self.sides = [a, b]
        self.mine_count = int((a*b)/6.0)
        self.manager.current = "game_screen"
        
class GetSidesPrompt(ModalView):
    pass
        
class Manager(ScreenManager):
        
    menu = ObjectProperty(None)
    game = ObjectProperty(None)
    

class MineSweeperApp(App):
    
    def build(self):
        return Manager(transition=FadeTransition())
        


if __name__ == "__main__":
    
    MineSweeperApp().run()


