import os
import sys
# Preventing the welcome message of Python to be shown
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import *
import threading
import queue
# User modules
import Graphics as gr
from Constants import *
from Layouts import Grid,BottomBar,SideBar
from GraphicalComponents import Text


#==============================
#   Configuration parameters
#==============================
# WINDOW_MIN_WIDHT = 580
DELAY_GENERATIONS = 0.005 # Delay in seconds
# Colors of cells
ALIVE_COLOR = BLUE
DEAD_COLOR = DARK_BLACK
# Number of elements by side in the grid
# the total number of cell is NUMBER_CELLS_1D x NUMBER_EVOLUTIONS_GRID
GRID_WIDTH = 1250
GRID_PADDING = 0
NUMBER_CELLS_1D = 1000
NUMBER_EVOLUTIONS_GRID = 900
USE_MIN_SIZE = False
# Elements of the interface
SIDE_BAR_WIDTH = 250
BOTTOM_BAR_HEIGHT = 25
WINDOW_TITLE = 'Elementary Cellular Automaton'

#==============================
#  Dynamic execution variables
#==============================
window = None
graphics = None
# Graphical elements
bottom_bar = None
side_bar = None

#===========================
#  Configuration functions
#===========================
def waiting_frame(window_size):
    global window
    # window background
    window.fill(LIGHT_BLACK_2)
    window_size_center = window_size/2
    # Messages texts
    message = 'Creating the evolution space ...'
    text_message = Text(
        position=(window_size_center[0]-(BIG_FONT.size(message)[0])/2,window_size_center[1]-250),
        text=message,
        text_color=YELLOW,
        font=BIG_FONT)
    message_2 = '(Please wait a little)'
    text_message_2 = Text(
        position=(window_size_center[0]-(MEDIUM_FONT.size(message_2)[0])/2,window_size_center[1]-200),
        text=message_2,
        text_color=WHITE,
        font=MEDIUM_FONT)
    # Cell icon
    image_size = window_size_center[1]*.75
    icon = pygame.transform.scale(pygame.image.load('./images/cells_w.png'),(image_size,image_size))
    # Draws the messages and the icon cell in the screen
    text_message.print(window)
    text_message_2.print(window)
    window.blit(icon,(window_size_center[0]-image_size/2,window_size_center[1]-image_size/3))
    # Updates the whole display
    pygame.display.flip()

def first_draw_elements():
    global window,graphics
    global bottom_bar,side_bar
    # window background
    window.fill(LIGHT_BLACK_2)
    graphics.pointer.update()
    graphics.graphical_cells.draw(window)
    # Graphical elements
    bottom_bar.draw(window)
    side_bar_elements = pygame.sprite.Group(side_bar.get_graphical_sprites()); side_bar_elements.update()
    side_bar.draw(window)
    # Updates the whole display
    pygame.display.flip()

#===========================
#     Main ECA programm
#===========================
def main():
    global window
    global graphics
    global bottom_bar,side_bar
    global GRID_WIDTH,GRID_PADDING,NUMBER_CELLS_1D,NUMBER_EVOLUTIONS_GRID,USE_MIN_SIZE
    #-----------------------
    # Command Line Arguments
    #-----------------------
    if len(sys.argv) == 3:
        NUMBER_CELLS_1D,NUMBER_EVOLUTIONS_GRID = [int(sys.argv[i]) for i in range(1,len(sys.argv))]
    if len(sys.argv) == 4:
        GRID_WIDTH,NUMBER_CELLS_1D,NUMBER_EVOLUTIONS_GRID = [int(sys.argv[i]) for i in range(1,len(sys.argv))]
    if len(sys.argv) == 5:
        GRID_WIDTH,NUMBER_CELLS_1D,NUMBER_EVOLUTIONS_GRID,GRID_PADDING = [int(sys.argv[i]) for i in range(1,len(sys.argv))]
    if len(sys.argv) == 6:
        GRID_WIDTH,NUMBER_CELLS_1D,NUMBER_EVOLUTIONS_GRID,GRID_PADDING,USE_MIN_SIZE = [int(sys.argv[i]) for i in range(1,len(sys.argv))]
    #----------------------
    # Pygame configurations
    #----------------------
    pygame.init()
    clock = pygame.time.Clock()
    #------------------------
    # Getting sizes from grid
    #------------------------
    grid_size,grid = Grid.optimal_grid_size((GRID_WIDTH-SIDE_BAR_WIDTH,GRID_WIDTH-BOTTOM_BAR_HEIGHT),NUMBER_CELLS_1D,NUMBER_EVOLUTIONS_GRID,GRID_PADDING,USE_MIN_SIZE) 
    #------------------------
    # Window configuration
    #------------------------
    window_display = 0
    window_size = grid_size + array([SIDE_BAR_WIDTH,BOTTOM_BAR_HEIGHT])
    print('<--- Window size ({}) --->'.format(window_size))
    window = pygame.display.set_mode(window_size,display=window_display)
    pygame.display.set_caption(WINDOW_TITLE)
    # Setting the cells colors
    gr.Graphics.set_cells_colors([DEAD_COLOR,ALIVE_COLOR])
    #------------------------
    #   Graphical elements
    #------------------------
    bottom_bar = BottomBar(LIGHT_BLACK_1,BOTTOM_BAR_HEIGHT,number_cells_1D=NUMBER_CELLS_1D,number_rows=NUMBER_EVOLUTIONS_GRID)
    bottom_bar.update_generations(0)
    side_bar = SideBar(DARK_BLACK,SIDE_BAR_WIDTH)
    #------------------------
    #  Other Configurations
    #------------------------
    # Finishing the grid configuration
    grid.set_window(window)
    waiting_frame(window_size)
    #--------------
    #   Graphics
    #--------------
    graphics = gr.Graphics(grid,side_bar=side_bar,bottom_bar=bottom_bar)
    graphics.set_delay_generations(DELAY_GENERATIONS)
    #------------------------
    #         Cells
    #------------------------
    grid.locate_elements(graphics.graphical_cells.sprites())
    #-------------------------
    # Pygame thread functions
    #-------------------------
    queue_main = queue.Queue(); queue_refresh = queue.Queue()
    events_thread = threading.Thread(target=graphics.look_for_events)
    actions_thread = threading.Thread(target=graphics.events_actions)
    functions_thread = threading.Thread(target=graphics.execution_of_functions,args=[queue_main])
    # Threads starting
    events_thread.start()
    actions_thread.start()
    functions_thread.start()

    #------------------------
    #   Main PyGame loop
    #------------------------
    first_draw_elements()
    while not graphics.done:
        # Frames per Second
        clock.tick(45)

        graphics.draw_elements(window)

        # The queues are used to share objects to the main thread
        #   In this case is used to execute plotting functions
        #   of matplotlib from the main thread
        if not queue_main.empty():
            queue_main.get()()

    pygame.quit()



if __name__ == '__main__': main()