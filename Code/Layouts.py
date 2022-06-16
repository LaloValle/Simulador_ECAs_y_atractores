import pygame
import numpy as np
# User modules
import Graphics as grph
from Constants import COLORS_LIST, FONT
from GraphicalComponents import *

class Grid():
    """Class that defines a grid given a position, number of columns, rows and a padding
    Helps to locate easilly a list of elements in a grid layout

    Functions
    ---------
    optimal_grid_size( grid_sizes, num_cols, num_rows, number_elements, padding ): optimal_grid_sizes, elements_size
        Class function that returns an array with the adjusted real size of a grid given the
        number of elements to be allocated and the padding for a number of columns and rows.
        The last return is a new instance of the Grid class with the given and calculated parameters

    Methods
    -------
    get_element_size(self) : self.element_size
        Getter for the size of the elements in the grid
    
    calculate_element_size(self) :
        Method that computes the size of each element depending on the number of columns
        and padding specified when creating the grid
    
    locale_elements(self,list_elements) :
        Locates the elements provided in the grid from left to right, and top to bottom
    """

    #-----------------
    # Class functions 
    #-----------------
    def optimal_grid_size( grid_sizes:tuple, num_cols:int, num_rows:int, padding:int=5, use_min:bool=False ):
        grid_sizes = np.array(grid_sizes,np.uint32)
        # Space of the paddings for all the grid in each column and row
        paddings = np.array([padding*(num_cols+1),padding*(num_rows+1)],np.uint32)
        elements_sizes = np.around( (grid_sizes - paddings) /  # The original size of the grid gets substracted the number of paddins by row and column
                        np.array([num_cols,num_rows],np.uint32)) # The resultant array gets divided between the number of columns and rows respectively
        elements_sizes[:] = elements_sizes.min() if use_min else elements_sizes.max()
        optimal_grid_sizes = (elements_sizes*np.array([num_cols,num_rows],np.uint32) + paddings).astype('uint32')
        # Creates a new instance of the Grid class with the parameters specified
        new_grid_instance = Grid(optimal_grid_sizes,num_cols=num_cols,num_rows=num_rows,padding=padding,element_sizes=tuple(elements_sizes))
        return optimal_grid_sizes,new_grid_instance


    def __init__(self, size:np.array, coord:tuple=(0,0), num_cols:int=2, num_rows:int=2, padding:int=5, element_sizes:tuple=(-1,-1), window=None):
        self.window = window
        self.size = size
        self.coord = coord
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.padding = padding
        self.element_sizes = self.calculate_element_sizes() if element_sizes[0]+element_sizes[1] < 0 else element_sizes
    #---------------------
    # Getters and setters
    #---------------------
    def set_window(self,window):
        self.window = window

    def get_element_sizes(self):
        return self.element_sizes
    #--------------
    # Grid Methods
    #--------------
    def calculate_element_sizes(self):
        """Computes the size of each element if not given when instanciating

        Returns
        -------
        element_sizes : tuple
            Tuple with the sizes of width and height
        """
        return tuple(np.around( 
                        (self.size - np.array([self.padding*(self.num_cols+1),self.padding*(self.num_rows+1)],np.uint16)) /  # The original size of the grid gets substracted the number of paddins by row and column
                        np.array([self.num_cols,self.num_rows],np.uint16)) # The resultant array gets divided between the number of columns and rows respectively
                ) 

    def locate_elements(self,list_elements):
        """Method that assigns the coordinates of the corner-top-left of each element in the list
        so that they are arranged in the grid previously calculated
        
        Parameters
        ----------
        list_elements : list
            List with the 'rects' of each graphical element that allows the element to be moved to
            a given coordinate
        """
        y_pos = self.padding+self.coord[1] # Initial position with just the padding added to the original y
        # Loop in number of rows
        for row in range(self.num_rows):
            x_pos = self.padding+self.coord[0] # Initial position with just the padding added to the oiriginal x
            # Loop in number of columns
            for column in range(self.num_cols):
                index = row*self.num_cols+column
                if index < len(list_elements): list_elements[index].move((int(x_pos),int(y_pos)))
                x_pos += self.padding+self.element_sizes[0] # The next element must be placed in the x position with added padding and width of the previous element
            y_pos += self.padding+self.element_sizes[1] # The next row of elements must be placed in the y position with added padding and width of the previous elements




class BottomBar():
    """Simple rectangle used as bottom bar
    As there is only 1 bottom bar in the program, a Singleton Class is implemented
    so it can be retreived in any part of the code with the configured values for
    the attributes and graphical components inside it

    Methods
    -------
    draw(self,window) :
        Draws a rectagle at the bottom with a given height and background color

    update_generations(self,generations) :
        Updates the generations string to be printed

    update_alive_cels(self,alive_cells) :
        Updates the alive cells string to be printed

    update_space_dimension_zoom(self,alive_cells) :
        Updates the dimensions string of the grid and the zoom string
    """

    # Singleton Class
    bottom_bar = None

    def __init__(self,color_background:tuple,height:int=35,number_rows:int=100,number_cells_1D:int=100):
        BottomBar.bottom_bar = self
        
        self.color_background = color_background
        self.height = height

        # The position and size gets define according to the windows size
        window_size = pygame.display.get_window_size()
        self.rectangle = pygame.Rect(
            ( 0, window_size[1]-height ),
            ( window_size[0]-250, height )
        )

        # Creation of texts
        self.texts = []
        self.generations_text = Text((10,3+self.rectangle.y),'Generations:')
        self.alive_cells_text = Text((self.rectangle.width-30-FONT.size('Alive Cells: 0')[0], 3+self.rectangle.y),'Alive Cells: 0')
        self.dimensions_number_space_text = Text((self.rectangle.width/2-int(FONT.size('100x100(space 1)')[0]/2), 3+self.rectangle.y),'{}x{}(space 1)'.format(number_cells_1D,number_rows))
        self.texts.append(self.generations_text)
        self.texts.append(self.alive_cells_text)
        self.texts.append(self.dimensions_number_space_text)

    #----------------
    # Drawing method
    #----------------
    def draw(self,window):
        pygame.draw.rect(window,self.color_background,self.rectangle)
        # Prints the texts strings
        for txt in self.texts:
            txt.print(window)
    #--------------------
    # Updates of strings
    #--------------------
    def update_generations(self,generations):
        self.generations_text.update('Generations:'+str(generations))
        return self.generations_text.rect

    def update_alive_cells(self,alive_cells):
        self.alive_cells_text.update('Alive Cells: '+str(alive_cells))
        return self.alive_cells_text.rect

    def update_dimensions_number_space(self,space_dimension,number_space):
        self.dimensions_number_space_text.update('{}x{}(space {})'.format(space_dimension[1],space_dimension[0],number_space))
        return self.dimensions_number_space_text.rect





class SideBar():
    """Simple rectangle used as side bar
    As there is only 1 side bar in the program, a Singleton Class is implemented
    so it can be retreived in any part of the code with the configured values for
    the attributes and graphical components inside it

    Methods
    -------
    draw(self,window) :
        Draws a rectagle at the right side with a given width and background color
    """
    #
    # Singleton Class
    #
    side_bar = None

    #
    # Button constants of class
    #
    PLAY_BUTTON = 0
    STOP_BUTTON = 1
    RESTART_BUTTON = 2
    CLEAR_BUTTON = 3
    SAVE_BUTTON = 4
    UPLOAD_BUTTON = 5
    RANDOM_INITIAL_BUTTON = 6
    INITIAL_CENTER_CELL_BUTTON = 7
    DRAG_SLIDER_BUTTON = 8
    RULE_INPUT = 9
    DENSITY_BUTTON = 10
    LOGARITHM_BUTTON = 11
    ENTROPY_BUTTON = 12
    ALIVE_COLOR_INPUT = 13
    DEAD_COLOR_INPUT = 14
    ATTRACTORS_BUTTON = 15
    START_ATTRACTORS_INPUT = 16
    END_ATTRACTORS_INPUT = 17



    def __init__(self,color_background:tuple,width:int=250,bottom_margin:int=0):
        # The only instance is the first created in the main
        SideBar.side_bar = self
        
        self.color_background = color_background
        self.width = width
        self.bottom_margin = bottom_margin
        self.padding = 15

        # The position and size gets define according to the windows size
        window_size = pygame.display.get_window_size()
        self.rectangle = pygame.Rect(
            ( window_size[0]-width, 0 ),
            ( width, window_size[1]-bottom_margin )
        )

        # Graphical elements inside the bar
        self.graphical_elements = []
        # Sections
        self.configurations_section = Section(self.rectangle.x,self.padding*2+80+10,self.rectangle.width,self.padding,'RUNNING CONFIGURATIONS')
        self.plot_section = Section(self.rectangle.x,270,self.rectangle.width,self.padding,'PLOTTING')
        self.colors_section = Section(self.rectangle.x,375+self.padding,self.rectangle.width,self.padding,'COLORS')
        self.attractors_section = Section(self.rectangle.x,480+self.padding,self.rectangle.width,self.padding,'ATTRACTORS')
        self.graphical_elements.append(self.plot_section)
        self.graphical_elements.append(self.configurations_section)
        self.graphical_elements.append(self.colors_section)
        self.graphical_elements.append(self.attractors_section)
        # Slider
        self.slider = self.set_slider()
        self.graphical_elements.append(self.slider)
        # Graphical sprites inside the bar
        self.graphical_sprites = pygame.sprite.Group()
        self.graphical_sprites.add(self.set_play_button())
        self.graphical_sprites.add(self.set_stop_button())
        self.graphical_sprites.add(self.set_restart_button())
        self.graphical_sprites.add(self.set_clear_button())
        self.graphical_sprites.add(self.set_save_button())
        self.graphical_sprites.add(self.set_upload_button())
        self.graphical_sprites.add(self.set_random_initial_button())
        self.graphical_sprites.add(self.set_initial_center_cell_button())
        # Configurations elements
        self.graphical_sprites.add(self.slider.get_drag_button())
        self.graphical_sprites.add(self.set_rule_input())
        # Plotting buttons
        self.graphical_sprites.add(self.set_density_button())
        self.graphical_sprites.add(self.set_logarithm_button())
        self.graphical_sprites.add(self.set_entropy_button())
        # Colors elements
        self.graphical_sprites.add(self.set_alive_color_input())
        self.graphical_sprites.add(self.set_dead_color_input())
        # Attractors elements
        self.graphical_sprites.add(self.set_attractors_button())
        self.graphical_sprites.add(self.set_start_attractors_input())
        self.graphical_sprites.add(self.set_end_attractors_input())

    # 
    # Getters and setters
    #
    def get_graphical_sprites(self):
        return self.graphical_sprites
    
    def set_click_function(self,button,function):
        """Sets the function to be actioned when the button gets pressed

        Parameters
        ----------
        button : int
            Index of the button in the graphical_sprites Sprite Group
            Class constants are used to describe the correct index for each button
        
        function : function
            Reference to the function to be executed when the button gets clicked
        """
        self.graphical_sprites.sprites()[button].click_function = function

    def get_sprite(self,index_sprite):
        return self.graphical_sprites.sprites()[index_sprite]
    
    #
    # Configuration of buttons
    #
    def set_play_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 20
        image_size = 25
        # The position in the center horizontally and at the top
        x = window_size[0] - self.width/2 - radius
        y = self.padding + radius + 5
        return CircularButton(x,y,radius,image_size,image_path='./images/play_w.png')

    def set_stop_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 20
        image_size = 15
        x = window_size[0] - self.width/2 - 2*radius - 15*2
        y = self.padding + radius + 5

        return CircularButton(x,y,radius,image_size,image_path='./images/stop_w.png')

    def set_restart_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 20
        image_size = 20
        x = window_size[0] - self.width/2 + 1.5*radius
        y = self.padding + radius + 5

        return CircularButton(x,y,radius,image_size,image_path='./images/restart_w.png')

    def set_clear_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 13
        x = window_size[0] - 2*radius - self.padding
        y = self.rectangle.height - 2*radius - 2*self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/clear_w.png')

    def set_save_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 13
        x = window_size[0] - 4*radius - 8 - self.padding
        y = self.rectangle.height - 2*radius - 2*self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/save_w.png')

    def set_upload_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 13
        x = window_size[0] - 6*radius - 16 - self.padding
        y = self.rectangle.height - 2*radius - 2*self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/upload_w.png')

    def set_random_initial_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 18
        x = window_size[0] - 2*radius - 8
        y = self.configurations_section.header_rect.y - 2*radius - 5
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/random_2_w.png')

    def set_initial_center_cell_button(self):
        window_size = pygame.display.get_window_size()
        # Size of the button
        radius = 18
        image_size = 18
        x = window_size[0] - 2*radius - 8
        y = self.configurations_section.header_rect.y - 4*radius - 5
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/between_w.png')
    
    def set_density_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding
        y = self.plot_section.header_rect.y + 30 + self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/density_w.png')

    def set_logarithm_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding + 8 + 2*radius
        y = self.plot_section.header_rect.y + 30 + self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/logarithm_w.png')

    def set_entropy_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding + 16 + 4*radius
        y = self.plot_section.header_rect.y + 30 + self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/entropy_w.png')

    def set_slider(self):
        width = self.rectangle.width - 2*self.padding - 10
        x = self.rectangle.x + self.padding + 5
        y = self.configurations_section.header_rect.y + 30 + self.padding

        slider = Slider(x,y,width)
        slider.drag_button.click_function = self.slider_move
        return slider

    def set_rule_input(self):
        x = self.rectangle.x + self.padding + 5
        y = self.configurations_section.header_rect.y + 30 + self.padding + 60

        input = Input(x,y,30,label='Rule',value='110',allow_focus=True)
        input.set_click_function(input.set_on_focus)
        return input

    def set_alive_color_input(self):
        x = self.rectangle.x + self.padding + 5
        y = self.colors_section.header_rect.y + 30 + self.padding
        background_color = grph.Graphics.cells_colors[1]
        input = Input(x,y,45,label='Alive',width=FONT.size('Alive')[0]+50,allow_focus=False,background_color=background_color)
        input.set_click_function(self.change_alive_cell_color)
        return input

    def set_dead_color_input(self):
        x = self.rectangle.x + 2*self.padding + 5 + 95
        y = self.colors_section.header_rect.y + 30 + self.padding
        background_color = grph.Graphics.cells_colors[0]
        input = Input(x,y,45,label='Dead',width=FONT.size('Dead')[0]+50,allow_focus=False,background_color=background_color)
        input.set_click_function(self.change_dead_cell_color)
        return input

    def set_attractors_button(self):
        # Size of the button
        radius = 30
        image_size = 30
        x = self.rectangle.x + self.padding
        y = self.attractors_section.header_rect.y + 30 + self.padding
        
        return CircularButton(x,y,radius,image_size,border=False,image_path='./images/attractors_w.png')

    def set_start_attractors_input(self):
        x = self.rectangle.x + 2*self.padding + 60
        y = self.attractors_section.header_rect.y + 30 + self.padding

        input = Input(x,y,30,width=135,label='Start',value='1',allow_focus=True)
        input.set_click_function(input.set_on_focus)
        return input

    def set_end_attractors_input(self):
        x = self.rectangle.x + 2*self.padding + 60
        y = self.attractors_section.header_rect.y + 30 + self.padding + 30

        input = Input(x,y,30,width=135,label='End',value='15',allow_focus=True)
        input.set_click_function(input.set_on_focus)
        return input
    
    #
    # Functions when colors of cells clicked
    #
    def change_dead_cell_color(self):
        input = self.graphical_sprites.sprites()[SideBar.DEAD_COLOR_INPUT]
        index_color_actual = COLORS_LIST.index(input.background_color)
        new_color = COLORS_LIST[index_color_actual+1 if index_color_actual < len(COLORS_LIST)-1 else 0] 
        grph.Graphics.cells_colors[0] = new_color
        input.background_color = new_color
        grph.Graphics.graphics.graphical_cells.update()
        grph.Graphics.graphics.internal_draw_elements.append(input); grph.Graphics.graphics.internal_draw = True
        grph.Graphics.graphics.updatable_elements.add(input); grph.Graphics.graphics.updatable_rects.append(input.rect)
        grph.Graphics.graphics.flip_screen = True
    
    def change_alive_cell_color(self):
        input = self.graphical_sprites.sprites()[SideBar.ALIVE_COLOR_INPUT]
        index_color_actual = COLORS_LIST.index(input.background_color)
        new_color = COLORS_LIST[index_color_actual+1 if index_color_actual < len(COLORS_LIST)-1 else 0] 
        grph.Graphics.cells_colors[1] = new_color
        input.background_color = new_color
        grph.Graphics.graphics.graphical_cells.update()
        grph.Graphics.graphics.internal_draw_elements.append(input); grph.Graphics.graphics.internal_draw = True
        grph.Graphics.graphics.updatable_elements.add(input); grph.Graphics.graphics.updatable_rects.append(input.rect)
        grph.Graphics.graphics.flip_screen = True
    #
    # Methods for actions in graphic elements and drawing 
    #
    def move_drag_button(self,x):
        self.slider.move_drag_button(x)

    def slider_move(self):
        SideBar.side_bar.move_drag_button(pygame.mouse.get_pos()[0])
        # cellular_automaton.update_zeros_density(SideBar.side_bar.slider.value)

    def stop_button_pressed(self,button):
        self.graphical_sprites.sprites()[button].pressed_once = False

    def draw(self,window):
        pygame.draw.rect(window,self.color_background,self.rectangle)
        # All the sprite elements get draw
        for element in self.graphical_elements:
            element.draw(window)
        self.graphical_sprites.draw(window)
        # Input text value
        self.graphical_sprites.sprites()[SideBar.RULE_INPUT].draw(window)
        # Inputs cells colors
        self.graphical_sprites.sprites()[SideBar.DEAD_COLOR_INPUT].draw(window)
        self.graphical_sprites.sprites()[SideBar.ALIVE_COLOR_INPUT].draw(window)