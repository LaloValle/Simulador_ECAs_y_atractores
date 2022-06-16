from queue import Queue
import queue
from matplotlib.pyplot import plot
import pygame
import numpy as np
# User modules
import time
import main as mn
from ECA import ECA,Attractors
from Constants import *
from Layouts import Grid,BottomBar,SideBar
from GraphicalComponents import Control,MousePointer



class Graphics():
    """Class in charge of the interface aspects of the program
    Implemented as a Singleton class as just 1 instance will be 
    necesary to controll the graphical of the program

    Functions
    ---------
    get_graphics( grid, side_bar, bottom_bar ) : graphics
        Returns the Singleton instance of the class
    """
    #==================
    # Class properties 
    #==================
    graphics = None
    cells_colors = [WHITE,LIGHT_BLACK_2]

    #==================
    #   Class methods
    #==================
    def set_cells_colors(colors):
        Graphics.cells_colors = colors
    
    def set_alive_color(color):
        Graphics.cells_colors[1] = color

    def set_dead_color(color):
        Graphics.cells_colors[0] = color

    def __init__(self, grid:Grid, side_bar:SideBar=None, bottom_bar:BottomBar=None):
        Graphics.graphics = self

        # Interface drawable sprite elements
        # self.drawable_elements = []
        
        # Grid for the cells
        self.grid = grid

        # Array of graphical cells
        self.graphical_cells = pygame.sprite.Group()
        self.updatable_rects = [] # List of individual rects of each cells that must be updated
        self.updatable_elements = pygame.sprite.Group() # Group of sprites elements/cells that must be re-draw before update
        self.create_graphical_cells()

        # Logical ECA
        self.eca = ECA(self.grid.num_cols,self.grid.num_rows,self.graphical_cells.sprites())
        self.delay_generations = time.time()

        # Collapsable pointer
        self.pointer = MousePointer((1,1))

        # Graphical elements and sections
        self.side_bar = side_bar
        self.bottom_bar = bottom_bar
        # Graphical elements that also can be interacted with
        self.collidable_elements = pygame.sprite.Group()
        self.collidable_elements.add(self.side_bar.get_graphical_sprites())

        #
        # Global status variables
        # 
        self.play = False
        self.done = False
        self.flip_screen = False
        self.click_pressed = False
        self.internal_draw = False
        self.internal_draw_elements = []
        self.update_evolution_parameters = False # Implies the update of the number of generation and number of alive cells
        # self.last_digit_typed = ''
        # Used for changing the states of collaidable elements
        
        
        # List of functions to be executed in an independent thread just for this kind of functions
        # this way, nor the graphical or events functions, gets delayed until this finishes
        self.execute_functions = []

        self.assign_functions_to_clicked_buttons()

    #=====================
    # Setters and getters
    #=====================
    def set_delay_generations(self,delay):
        self.delay_generations = delay


    #===========================
    #     Graphical functions
    #===========================
    def create_graphical_cells(self):
        cell_size = self.grid.calculate_element_sizes()
        for rows in range(self.grid.num_rows):
            for columns in range(self.grid.num_cols):
                self.graphical_cells.add(Cell(cell_size,(columns,rows)))

    def assign_functions_to_clicked_buttons(self):
        self.side_bar.set_click_function(SideBar.PLAY_BUTTON,self.Play)
        self.side_bar.set_click_function(SideBar.STOP_BUTTON,self.stop)
        self.side_bar.set_click_function(SideBar.RESTART_BUTTON,self.restart)
        self.side_bar.set_click_function(SideBar.INITIAL_CENTER_CELL_BUTTON,self.initial_center_cell)
        self.side_bar.set_click_function(SideBar.RANDOM_INITIAL_BUTTON,self.initial_random_configuration)
        self.side_bar.set_click_function(SideBar.DENSITY_BUTTON,self.add_plot_density_functions)
        self.side_bar.set_click_function(SideBar.LOGARITHM_BUTTON,self.add_plot_density_logarithm_functions)
        self.side_bar.set_click_function(SideBar.ENTROPY_BUTTON,self.add_plot_shannons_entropy_functions)
        self.side_bar.set_click_function(SideBar.CLEAR_BUTTON,self.clean)
        self.side_bar.set_click_function(SideBar.UPLOAD_BUTTON,self.upload_evolution_space)
        self.side_bar.set_click_function(SideBar.SAVE_BUTTON,self.save_evolution_space)
        self.side_bar.set_click_function(SideBar.ATTRACTORS_BUTTON,self.compute_attractors)
    
    #=======================
    # Pygame Loop functions
    #=======================
    def look_for_events(self):
        clock = pygame.time.Clock()
        while not self.done:
            clock.tick(45)
            # Look for every possible event in the programm
            for event in pygame.event.get():
                # When pressing close button in top bar
                if event.type == pygame.QUIT:
                    self.done = True
                    return True
    
                # When mouse button pressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.click_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: # Left click
                        self.click_pressed = False
                # Looks for mouse wheel events
                elif event.type == pygame.MOUSEWHEEL:
                    # Scrolling up
                    if event.y == 1:
                        ECA.eca.scroll_space(up=True)
                    # Scrolling down
                    elif event.y == -1:
                        ECA.eca.scroll_space(up=False)

                    """
                        Key map
                        +++++++
                            Keys use for execute actions in the programm

                            p : Plays the continuous evolution process
                            n : Computes only 1 generation of the space evolution
                            s : Stops the evolution process
                            c : Cleans the evolutions grids and restart the dynamic variables for the evolution process
                            m : Sets the central cell of an evolution space in the actual row as alive

                    """

                # Looks for key press
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p: self.Play()
                    elif event.key == pygame.K_n: self.execute_functions.append(self.next_generation); self.one_execution = True; print('<--- Step next generation --->')
                    elif event.key == pygame.K_s: self.stop()
                    elif event.key == pygame.K_c: self.execute_functions.append(self.clean)
                    elif event.key == pygame.K_m: self.execute_functions.append(self.initial_center_cell)
                    elif event.key == pygame.K_BACKSPACE: self.last_digit_typed = -1
                    else: 
                        aux_digit = event.unicode
                        if ord(aux_digit) >= 48 and ord(aux_digit) <= 57:
                            self.last_digit_typed = event.unicode
                        else: print('<!!! Only digits are allowed !!!>')

    def events_actions(self):
        clicked_elements = set(); hovered_elements = set(); focused_element = []
        last_generation_time = time.time()
        clock = pygame.time.Clock()
        while not self.done:
            clock.tick(45)
            # Updates the collaidable pointer position
            self.pointer.update()

            # Verifies if a collapsible element of the UI collided
            collaided_elements = pygame.sprite.spritecollide(self.pointer,self.collidable_elements,False)
            # Verifies if a cell has colapsed when there's been a click
            if self.click_pressed: collaided_elements += pygame.sprite.spritecollide(self.pointer,self.graphical_cells,False)

            # Looks for previously focused elements so they can change the focus state
            if focused_element:
                # As the only focused element in the programm
                # when a new character gets typed is changed
                # in the input text showed
                if self.last_digit_typed != '':
                    focused_element[0].new_character(self.last_digit_typed)
                    # Only the input of the rule gets to update the actual rule
                    if focused_element[0].label_text == 'Rule':
                        self.eca.update_rule(int(focused_element[0].value) if focused_element[0].value != '' else 0)
                    # Adds the graphical element to be draw and updated
                    self.updatable_elements.add(element)
                    self.internal_draw = True; self.internal_draw_elements.append(element)
                    self.updatable_rects.append(element.rect)
                    self.last_digit_typed = ''
                if self.click_pressed:
                    if focused_element[0] not in collaided_elements:
                        element = focused_element.pop(); element.on_focus = False
                        # Adds the graphical element to be draw and updated
                        self.updatable_elements.add(element)
                        self.internal_draw = True; self.internal_draw_elements.append(element)
                        self.updatable_rects.append(element.rect)

            # Looks for previously clicked elements/cells so they can stop_click()
            if clicked_elements  and not self.click_pressed: # Stop clicking
                for clicked in clicked_elements:
                    clicked.stop_click()
                    # Adds the graphical element to be draw and updated
                    self.updatable_elements.add(clicked)
                    self.updatable_rects.append(clicked.rect)
                clicked_elements.clear()
            
            # Looks for previously hovered elements so they can exit()
            if hovered_elements:
                remove_hovered = []
                for hovered in hovered_elements:
                    # Identifies if the element no longer collides with the pointer
                    if hovered not in collaided_elements:
                        hovered.exit()
                        remove_hovered.append(hovered)
                        # Adds the graphical element to be draw and updated
                        self.updatable_elements.add(hovered)
                        self.updatable_rects.append(hovered.rect)
                # The elements get removed from the set
                if remove_hovered : 
                    for removed in remove_hovered: hovered_elements.remove(removed)

            # At least an element has collaided
            if collaided_elements:
                for element in collaided_elements:
                    if self.click_pressed: # It's been clicked
                        # It's a graphical cell
                        if hasattr(element,'index'):
                            # Only can be modified graphical cells of the actual generation row
                            if element.index[1] == self.eca.actual_row:
                                element.click()
                                clicked_elements.add(element)
                                # Adds the cell to be draw and updated
                                self.updatable_elements.add(element)
                                self.updatable_rects.append(element.rect)# At least an element has collaided
                        # Other graphical elements like buttons
                        else:
                            # Gets the click function of the element to be executed in the thread of functions
                            element.click()
                            clicked_elements.add(element)
                            # Graphical elements with focus
                            if element.has_on_focus():
                                focused_element.insert(0,element)
                                self.last_digit_typed = ''
                                # Adds the graphical element to be draw and updated
                                self.updatable_elements.add(element)
                                self.internal_draw = True; self.internal_draw_elements.append(element)
                                self.updatable_rects.append(element.rect)
                    if not self.click_pressed and not element.has_on_focus(): # There's no click pressed
                        element.hover()
                        hovered_elements.add(element)
                        # Adds the graphical element to be draw and updated
                        self.updatable_elements.add(element)
                        self.updatable_rects.append(element.rect)

            # Verifies the time elapsed since the last generation been computed
            if self.play:
                if time.time()-last_generation_time >= self.delay_generations:
                    self.execute_functions.append(self.next_generation)
                    last_generation_time = time.time()

    def draw_elements(self,window):
        if self.update_evolution_parameters:
            # Update of the evolution variables
            self.updatable_rects.append(self.bottom_bar.update_alive_cells(self.eca.alive_cells))
            self.updatable_rects.append(self.bottom_bar.update_generations(self.eca.generations))
            self.bottom_bar.draw(window)
            self.update_evolution_parameters = False
        # Only draws the elements when the display has to be flipped or when there's updatable rects
        if self.flip_screen or self.updatable_rects:
            # Draws and updates all the graphical cells
            if self.flip_screen:
                self.bottom_bar.draw(window)
                self.side_bar.draw(window)
                self.graphical_cells.draw(window)
                pygame.display.flip()
                self.flip_screen = False
            # Draws and updates only the cells that changed of color
            else:
                aux_updatable_rects = (list(self.updatable_rects)); del self.updatable_rects[:]
                self.updatable_elements.draw(window); self.updatable_elements.empty()
                # There's elements that has a defined draw function needed to be executed so that all the graphical elements get shown
                if self.internal_draw: 
                    while self.internal_draw_elements: self.internal_draw_elements.pop(0).draw(window)
                    self.internal_draw = False
                pygame.display.update(aux_updatable_rects)


    #===========================
    #     Action functions
    #===========================
    def execution_of_functions(self,queue_main:Queue):
        clock = pygame.time.Clock()
        while not self.done:
            clock.tick(30)
            if self.execute_functions:
                (self.execute_functions.pop(0))(share=queue_main)

    def next_generation(self,**kargs):
        if self.play or self.one_execution:
            aux_rects,aux_cells,proceed = self.eca.compute_next_generation()
            # Statistical analysis
            self.eca.density()
            self.eca.density_logarithm()
            self.eca.shannon_entropy()
            if proceed:
                self.update_evolution_parameters = True
                # Both the rects and sprites of cells gets added to the respective global variable
                self.updatable_rects += aux_rects; self.updatable_elements.add(aux_cells)
            else:
                self.play = False
                print('<--- Evolution process stoped for the space is to small to keep evolving --->')
            self.one_execution = False

    def upload_evolution_space(self,**kargs):
        self.clean()
        aux_updatable_rect,aux_updatable_cells = self.eca.upload_evolution_space()
        self.update_evolution_parameters = True
        self.updatable_elements.add(aux_updatable_cells); self.updatable_rects += aux_updatable_rect

    def save_evolution_space(self,**kargs):
        self.eca.save_evolution_space()

    def Play(self,**kargs):
        self.play = True
        print('<--- Running evolution process --->')

    def stop(self,**kargs):
        self.play = False
        print('<--- Pausing evolution process --->')

    def initial_center_cell(self,**kargs):
        self.eca.initial_center_cell()
        self.flip_screen = True

    def initial_random_configuration(self,**kargs):
        self.eca.initial_random_configuration()
        self.flip_screen = True

    def clean(self,**kargs):
        self.eca.clean()
        self.flip_screen = True
        print('<--- Cleaning of space --->')

    def restart(self,**kargs):
        self.clean()
        # Calls the logical ECA restart
        aux_updatable_rect,aux_updatable_cells = self.eca.restart()
        self.updatable_elements.add(aux_updatable_cells); self.updatable_rects += aux_updatable_rect

    def compute_attractors(self,**kargs):
        self.clean()
        Attractors.attractors.compute_attractors()

    #
    # Statistical analysis
    #
    # Function that adds the ploting functions into the function execution thread so that
    # it can share the matplotlib function to the main thread through the queue object
    def add_plot_density_functions(self): self.execute_functions.append(self.plot_density)
    def add_plot_density_logarithm_functions(self): self.execute_functions.append(self.plot_density_logarithm)
    def add_plot_shannons_entropy_functions(self): self.execute_functions.append(self.plot_shannons_entropy)

    def plot_density(self,share:Queue=None):
        share.put(self.eca.plot_density)

    def plot_density_logarithm(self,share:Queue=None):
        share.put(self.eca.plot_density_logarithm)

    def plot_shannons_entropy(self,share:Queue=None):
        share.put(self.eca.plot_shannons_entropy)



class Cell(Control):

    def __init__(self, size:tuple, index:tuple, alive:bool=False):
        super().__init__()
        # Status variable for when is clicked once
        self.already_clicked = False
        # Cells properties
        self.alive = alive
        # Index of the cell in the general grid
        self.index = index
        # The cell and the rect inside gets defined
        self.image = pygame.Surface(size)
        self.image.fill(Graphics.cells_colors[int(self.alive)])
        # The rect of the cell is asigned so in 
        # further methods can be used to move it
        self.rect = self.image.get_rect()

    #--------------------------------
    # Functions of the Control class
    #--------------------------------
    def update(self):
        # Updates the background color of the cell
        self.image.fill(Graphics.cells_colors[int(self.alive)])

    def exit(self):
        self.already_clicked = False

    def click(self):
        # Changes the alive status of the cell and reprints it's color
        if not self.already_clicked:
            self.already_clicked = True
            self.alive = not self.alive
            # Updates the logical cells
            ECA.eca.update_cell_status(self.index[0])
            self.update()

    def stop_click(self):
        self.already_clicked = False

    #--------------
    # Cell methods
    #--------------
    def move(self,coord:tuple):
        self.rect.x = coord[0]
        self.rect.y = coord[1]

    def set_status(self,status):
        self.alive = status
        self.update()