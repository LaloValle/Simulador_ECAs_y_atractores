import time
import random
import numpy as np
import igraph as ig
import networkx as nx
from math import log10,log2
import matplotlib.pyplot as plt
# Users module
from Constants import COLOUR_ATTRACTOR, MATRIX_BIN_TO_DEC,BITS_MASKS,HEX_COLORS_LIST
from Layouts import SideBar as SB
import Graphics as Grph
import Layouts as Ly

class ECA():

    # Singleton Class
    eca = None

    def __init__(self,number_cells_1D,evolutionary_space_rows,graphical_cells):
        ECA.eca = self
        self.attractors = Attractors(self)
        # Defines the initial size of the evolving and saving spaces
        # Adds 2 columns in cells for the toroidal behavior
        self.number_cells_1D = number_cells_1D
        self.dimensions = (evolutionary_space_rows,self.number_cells_1D+2)
        # Grid of 2 dimensions for saving the evolutions in time of the ECA in 1D
        self.saving_space = np.zeros(self.dimensions,np.ubyte)
        # Defines an evolution space in which the evolutions will be computed
        # It has 2 rows, the first for the actual space combination and the second
        # for the resultant evolution
        self.evolution_space = np.zeros((2,self.dimensions[1]),np.ubyte)
        # Reference in list of the graphical cells
        self.graphical_cells = graphical_cells
        # States
        self.zeros_density = 0.5
        # Dynamic variables through the process
        self.generations = 0
        self.alive_cells = 0
        # Defines the actual row that is actually getting evolved
        self.actual_row = 0
        # Rule number
        self.rule = 110
        # Identifies the saved spaces and the showed spaces. Used for scrolling
        self.evolution_spaces_saved = 0
        self.actual_evolution_space = 1
        # Record of statistical analysis
        self.density_record = []
        self.density_logarithm_record = []
        self.shannon_entropy_record = []

    #---------------------------------------------------
    # Configuration and button pressed actioned methods
    #---------------------------------------------------
    def initial_random_configuration(self):
        updatable_rects = []; updatable_cells = []
        for i in range(self.number_cells_1D):
            if  self.zeros_density > random.random(): # Probability of an alive cell is the complement of the state 0
                # Updates the alive cell in all the evolutions spaces and graphical cells
                self.saving_space[0,i+1] = 1
                self.evolution_space[0,i+1] = 1
                self.graphical_cells[i].alive = True
                self.alive_cells += 1
                # Updates the interface
                self.graphical_cells[i].update()
                updatable_cells.append(self.graphical_cells[i])
                updatable_rects.append(self.graphical_cells[i].rect)
        return updatable_rects,updatable_cells

    def initial_center_cell(self):
        center_index = int(self.number_cells_1D/2)
        # Updates the alive cell in all the evolutions spaces and graphical cells
        self.saving_space[0,center_index+1] = 1
        self.evolution_space[0,center_index+1] = 1
        # Graphical cell
        self.graphical_cells[center_index].alive = True
        self.graphical_cells[center_index].update()
        self.alive_cells += 1
        print('<--- Center cell (x:{}) --->'.format(center_index))

    def expand_evolution_space(self,length_tail:int=5):        
        self.evolution_spaces_saved += 1
        self.save_evolution_space(True, self.evolution_spaces_saved)
        self.actual_evolution_space += 1
        # A tail rows of the las evolution space gets copied to the head of the new evolution space
        self.saving_space[0:length_tail,:] = self.saving_space[-length_tail:self.dimensions[0],:]
        # The saving space gets cleared
        self.saving_space[length_tail:,:] = 0
        # Update of the actual row
        self.actual_row = length_tail-1

        # Graphical cells
        for y in range(self.dimensions[0]):
            for x in range(1,self.number_cells_1D+1):
                aux_cell = self.graphical_cells[y*self.number_cells_1D+(x-1)]
                # Verifies the values of the graphical cells of the rows of the heads space
                if y < length_tail:
                    if not(aux_cell.alive == bool(self.saving_space[y,x])): 
                        aux_cell.alive = not(aux_cell.alive)
                else: aux_cell.alive = False
                aux_cell.update()
        
        Ly.BottomBar.bottom_bar.update_dimensions_number_space([ECA.eca.dimensions[0],ECA.eca.number_cells_1D],self.actual_evolution_space)
        Grph.Graphics.graphics.flip_screen = True

    def clean(self,also_spaces_saved:bool=True):
        # The evolutions spaces gets all the cells restart to dead
        self.saving_space[self.actual_row,:] = 0
        self.evolution_space[0,:] = 0
        for i in range(self.number_cells_1D*(self.actual_row+1)): 
            self.graphical_cells[i].alive = False
            self.graphical_cells[i].update()
        # Dinamyc changing variables
        self.actual_row = 0
        self.alive_cells = 0
        self.generations = 0
        if also_spaces_saved:
            self.evolution_spaces_saved = 0
            self.actual_evolution_space = 1
        # Statistical records
        self.density_record.clear()
        self.density_logarithm_record.clear()
        self.shannon_entropy_record.clear()
        # Graphical texts in the bottom
        Ly.BottomBar.bottom_bar.update_dimensions_number_space([ECA.eca.dimensions[0],ECA.eca.number_cells_1D],self.actual_evolution_space)
        Ly.BottomBar.bottom_bar.update_alive_cells(0)
        Ly.BottomBar.bottom_bar.update_generations(0)
        

    def restart(self):
        self.clean()
        return self.initial_random_configuration()

    def update_zeros_density(self,density):
        self.zeros_density = density

    def update_rule(self,rule):
        self.rule = rule

    def update_cell_status(self,cell_position, status:bool=True, invert:bool=True,graphical_cell:bool=False):
        # When invert active changes the state of the cell to the contrary of the current cell state
        status = (not self.evolution_space[0,cell_position+1]) if invert else status
        self.evolution_space[0,cell_position+1] = int(status)
        self.saving_space[self.actual_row,cell_position+1] = self.evolution_space[0,cell_position+1]
        # Also updates the graphical cells
        if graphical_cell:
            self.graphical_cells[self.actual_row*self.number_cells_1D + cell_position].alive = status
            self.graphical_cells[self.actual_row*self.number_cells_1D + cell_position].update()
            return self.graphical_cells[self.actual_row*self.number_cells_1D + cell_position], self.graphical_cells[self.actual_row*self.number_cells_1D + cell_position].rect

    def save_evolution_space(self,internal_space:bool=False,id_internal_saved:int=1):
        if not internal_space: filename = './saves/Rule_{}_generation_{}.csv'.format(self.rule,self.generations)
        # Used when saving an space to allow more evolutions by clearing rows
        else: filename = './.internal_spaces/{}.csv'.format(id_internal_saved)
        np.savetxt(
            filename,
            self.saving_space[:self.actual_row+1,1:-1],
            delimiter = ', ',
            fmt = '% s'
            )
        if not internal_space: print('<--- File successfully saved as \"'+filename+'\" --->')

    def upload_evolution_space(self,internal_space:bool=False,id_internal_saved:int=1):
        aux_array = np.genfromtxt("./saves/upload.csv" if not internal_space else './.internal_spaces/{}.csv'.format(id_internal_saved),delimiter=', '); aux_shape = aux_array.shape
        if (self.dimensions[0]-aux_shape[0] < 0) or (self.dimensions[1]-aux_shape[1] < 0):
            print('!!! The actual evolution space is smaller than the intended upload file !!!')
        # The upload array gets loaded in the programm
        else:
            updatable_rects = []; updatable_cells = []
            # First the space gets cleaned
            self.clean(also_spaces_saved=not internal_space)
            initial_column = int((self.dimensions[1]-aux_shape[1])/2)
            # The new array gets saved in the saving_space and the evolution_space arrays
            self.saving_space[:aux_shape[0],initial_column:initial_column+aux_shape[1]] = aux_array
            self.evolution_space[0,initial_column:initial_column+aux_shape[1]] = aux_array[-1,:] # The las row of the uploaded array gets copied to the evolution space
            # The graphical cells gets updated with the value of the new array
            for y in range(aux_shape[0]):
                for x in range(initial_column,initial_column+aux_shape[1]):
                    if self.saving_space[y,x]:
                        aux_cell = self.graphical_cells[y*self.number_cells_1D+(x-1)]
                        aux_cell.alive = True
                        aux_cell.update()
                        updatable_cells.append(aux_cell)
                        updatable_rects.append(aux_cell.rect)
            # Dynamic variables
            self.alive_cells = int(aux_array[-1].sum())
            self.generations = aux_shape[0]
            self.actual_row = self.generations-1
            if not internal_space: print('<--- New configuration successfully uploaded --->')
            return updatable_rects,updatable_cells

    def scroll_space(self,up:bool=True):
        # No evolution space before/after to be scroll
        if up and self.actual_evolution_space == 1:
            print('<!!! No previous evolutions exists to scroll upward !!!>')
            return False
        elif not up and self.evolution_spaces_saved <= self.actual_evolution_space:
            print('<!!! No more evolutions exists to scroll downward !!!>')
            return False
        
        if up:
            print('<--- Scrolling up --->')
            # It's the last evolution space
            if self.actual_evolution_space > self.evolution_spaces_saved:
                self.evolution_spaces_saved += 1 
                self.save_evolution_space(internal_space=True,id_internal_saved=self.evolution_spaces_saved)
            self.actual_evolution_space -= 1
            # The previously saved space gets loaded
            self.upload_evolution_space(internal_space=True,id_internal_saved=self.actual_evolution_space)

        
        if not up:
            print('<--- Scrolling down --->')
            # When scrolling down to the last evolution space
            self.actual_evolution_space += 1
            self.upload_evolution_space(internal_space=True,id_internal_saved=self.actual_evolution_space)
            if self.evolution_spaces_saved == self.actual_evolution_space: self.evolution_spaces_saved -= 1

        Ly.BottomBar.bottom_bar.update_dimensions_number_space([ECA.eca.dimensions[0],ECA.eca.number_cells_1D],self.actual_evolution_space)
        Grph.Graphics.graphics.flip_screen = True
    
    #------------------
    # Auxiliar Methods
    #------------------
    def toroidal_padding(self):
        self.evolution_space[0] = self.evolution_space[-2]
        self.evolution_space[-1] = self.evolution_space[1]

    def get_actual_evolution_row(self,window:tuple=(1,-1)):
        return self.evolution_space[0,window[0]:window[1]]

    def update_evolution_row(self,jump:int=1):
        self.actual_row += jump
        if self.actual_row >= self.dimensions[0]: self.expand_evolution_space()

    #---------------------------------
    # Evolution space related methods
    #---------------------------------
    def compute_next_generation(self,restrain_window=False,window_range=(0,-1)):
        # Verifies that the next evolution exceeds the actual size of the array
        if (self.actual_row == self.dimensions[0]-1):
            self.expand_evolution_space()

        window_range = (0,self.number_cells_1D) if not restrain_window else (window_range[0]-1,window_range[1])
        updatable_rects = []; updatable_cells = []
        self.toroidal_padding()
        self.alive_cells = 0
        for x in range(window_range[0],window_range[1]):
            window = np.copy(self.evolution_space[0,x:x+3])
            # Converts to decimal and sums the value to get the index of the bit mask
            index_neighbourhood = (window*MATRIX_BIN_TO_DEC).sum()
            # With the bit mask gets the value of the AND bit operation
            # when the value is greater than 0 the value of the new cell is 1
            new_cell_status = self.rule & BITS_MASKS[index_neighbourhood]
            if new_cell_status :
                new_cell_status = 1
                self.alive_cells += 1
            # The result gets loaded in the evolution space second row
            self.evolution_space[1,x+1] = new_cell_status
            # Only when the new_status cell changes to alive
            if new_cell_status:
                aux_cell = self.graphical_cells[(self.actual_row+1)*self.number_cells_1D+x]
                aux_cell.alive = True; aux_cell.update()
                updatable_rects.append(aux_cell.rect)
                updatable_cells.append(aux_cell)
        # Once the new states have been calculated, the new evolutions results get saved
        self.saving_space[self.actual_row+1,:] = self.evolution_space[1,:]
        self.evolution_space[0,:] = self.evolution_space[1,:] # The new evolutions takes the first row
        self.evolution_space[1,:] = 0 # Cleans the second row with 0's
        self.generations += 1
        self.actual_row += 1
        # Returns a list of the rects of the cells that changed value
        return list(updatable_rects),updatable_cells,True
    #
    # Statistical analysis
    #
    def density(self):
        self.density_record.append(int(self.alive_cells))

    def density_logarithm(self):
        self.density_logarithm_record.append(log10(self.alive_cells))
    
    def shannon_entropy(self):
        entropy = 0
        neighbourhood_frecuency = [ 0 for i in range(8) ]

        for x in range(self.number_cells_1D):
            window = np.copy(self.evolution_space[0,x:x+3])
            neighbourhood_number = (window*MATRIX_BIN_TO_DEC).sum()
            neighbourhood_frecuency[neighbourhood_number] += 1

        probability = 0.0
        for frecuency in neighbourhood_frecuency:
            if frecuency: # Different of 0
                probability = frecuency/self.number_cells_1D
                entropy -= probability*log2(probability)

        self.shannon_entropy_record.append(entropy)

    def plot_density(self):
        if not self.density_record:
            print('<!!! No density of cells has been recorded !!!>')
            return False

        fig = plt.figure()
        ax = plt.axes()

        ax.set( xlabel = 'Generations',
                ylabel = 'Density',
                title = 'Alive Cells Density'
            )
        ax.grid()

        data = list(self.density_record)
        data = np.array(list(enumerate(list(data))))
        ax.scatter(data[:,0],data[:,1])
        ax.plot(data[:,0],data[:,1])

        plt.show()

    def plot_density_logarithm(self):
        if not self.density_logarithm_record:
            print('<!!! No logarithm density of cells has been recorded !!!>')
            return False

        fig = plt.figure()
        ax = plt.axes()

        ax.set( xlabel = 'Generations',
                ylabel = 'Density Logarithm',
                title = 'Logarithm Alive Cells Density'
            )
        ax.grid()

        data = list(self.density_logarithm_record)
        data = np.array(list(enumerate(list(data))))
        ax.scatter(data[:,0],data[:,1])
        ax.plot(data[:,0],data[:,1])

        plt.show()

    def plot_shannons_entropy(self):
        if not self.shannon_entropy_record:
            print('<!!! No shannons entropy has been recorded !!!>')
            return False

        fig = plt.figure()
        ax = plt.axes()

        ax.set( xlabel = 'Generations',
                ylabel = 'Entropy',
                title = 'Shannons Entropy'
            )
        ax.grid()

        data = list(self.shannon_entropy_record)
        data = np.array(list(enumerate(list(data))))
        ax.scatter(data[:,0],data[:,1])
        ax.plot(data[:,0],data[:,1])

        plt.show()





class Attractors():
    """
    Libraries
    ---------
    igraph :
        Use to describe a graph defining their vertices and relations between them

    cairocffi :
        Allows igraph to plot the graph in a 2D image
    """
    #------------------------------
    # Class's function and variable
    #------------------------------
    attractors = None
    def generate_binary_chains(power:int,previous_chains=[]) -> list:
        """Function that generates the binary chains of all the universe starting from the
        power 1 until the give power

        Parameters
        ----------
        power : int
            Finish power of the chain universe to be calculated
        
        Returns
        -------
        chains : list
            Bidimensional list of the chains generated for each power universe.
            Every element in the second dimension holds the chains of a power universe
        """
        # When power is 1 or less only the binary universe of chains in power 1 is returned
        if power <= 1: return [["0","1"]]
        # Validates if a given list with previously calculated chains has been given
        chains = previous_chains
        if not chains: chains = [["0","1"]]
        # Loop of the consecutive universe of powers
        for p in range(len(chains)-1,power):
            chains.append([]); print('p >>',p)
            # Loop for the generation of the chains of a given universe power
            for previous_chain in chains[p]:
                chains[p+1].extend([previous_chain+str(0), previous_chain+str(1)])

        return chains

    def __init__(self,eca):
        Attractors.attractors = self
        # Range of the sizes of evolutions spaces from which will be calculated its attractors
        self.sizes = (0,5)
        # List containing all the posible combinations of values of the cells in a space from a range of sizes
        self.binary_chains = []
        self.conversion_matrix = np.array([1])
        # Trees of the attractors found in each universe
        #   The first dimension of the dictionary will be the trees of each universe and the key corresponds to the number of power of the universe
        #       Inside each universe dictionary there's a dictionary with keys:
        #           relations : Relations between nodes
        self.trees = dict()
        self.actual_universe = 0
        self.list_attractors = list()
        # When using matplotlib for networkx
        """ self.sizes_graph = [
            (0,0),
            (4,4),
            (4,4),
            (4,4),
            (6,6),
            (10,10),
            (14,14),
            (34,34),
            (46,46),
            (60,60),
            (80,80),
            (115,115),
            (165,165),
        ] """
        self.sizes_igraph = [
            0,
            100,
            140,
            200,
            270,
            350,
            450,
            750,
            1700,
            1700,
            1500,
            1700,
            2300,
            3200,
            4000,
            4900,
            5700,
            6800,
            6800,
            6800,
            6800,
        ]

    #------------------
    # Auxiliar Methods
    #------------------
    def get_sizes_range(self):
        self.sizes = [
            int(SB.side_bar.get_sprite(SB.START_ATTRACTORS_INPUT).value),
            int(SB.side_bar.get_sprite(SB.END_ATTRACTORS_INPUT).value)
            ]

    def get_binary_chains(self):
        if len(self.binary_chains) < self.sizes[1]:
            self.binary_chains = Attractors.generate_binary_chains(self.sizes[1],self.binary_chains)

    def conversion_matrix_bin_decimal(self,power,previous_matrix=np.array([1])):
        """Returns a matrix with value of each power value in the conversion from binary to decimal
        
        Parameters
        ----------
        power : int
            Number of positions power to be calculated

        Retuns
        ------
        matrix : array
            Array that can be multiplied with the objective array to be converted into decimal values
        """
        matrix = np.array([],np.uint16)
        if power > previous_matrix.size:
            matrix = np.zeros((power-previous_matrix.size),np.uint16)
            actual_power_value = 1 << previous_matrix.size
            # Loops through the matrix
            for i in range(1,matrix.size+1):
                # print('actual power value >>',actual_power_value)
                matrix[-i] = int(actual_power_value)
                actual_power_value <<= 1
        # else: print('<--- The conversion matrix is bigger than the required power --->')
        return np.concatenate((matrix,previous_matrix))

    #------------
    # Attractors
    #------------
    def compute_attractors(self):
        print('<--- Preparing to start the compute --->')
        self.get_sizes_range(); self.get_binary_chains()
        # Copy of the binary list that will be removed through the appearances in the compute process
        computed_chains = list(self.binary_chains)
        # Center of the evolution row
        center_cell = int(ECA.eca.number_cells_1D/2)
        index_hex_colors = 0
        print('<--- Starting attractors compute --->')
        starting_time = time.time()

        # Loop for every chains power universe
        for universe in range(self.sizes[0]-1, self.sizes[1]):
            print('<--- Computing attractors for the universe power {} --->'.format(universe+1))
            self.conversion_matrix = self.conversion_matrix_bin_decimal(universe+1, self.conversion_matrix)
            starting_cell = center_cell - int((universe+1)/2)
            # print('index chains >>',len(self.binary_chains[universe]))
            window_range = (starting_cell+1,starting_cell+universe+2)
            # list of the relations
            relations = []

            # Loop through the available chains of the universe
            for index_chains in range(len(self.binary_chains[universe])):

                # Validates it's still a string, meaning this node hasn't been explored yet in the three
                if type(computed_chains[universe][index_chains]) == str:

                    # Loops through the characters of the binary chain
                    updatables = []; previous_node = int(computed_chains[universe][index_chains],2)
                    for index_value_chain in range(len(computed_chains[universe][index_chains])):
                        updatables = ECA.eca.update_cell_status(starting_cell+index_value_chain,True if computed_chains[universe][index_chains][index_value_chain] == '1' else False, invert=False, graphical_cell=True)
                        Grph.Graphics.graphics.updatable_elements.add(updatables[0]); Grph.Graphics.graphics.updatable_rects.append(updatables[1])
                    # As the chain has been used then it's no available anymore to be used
                    computed_chains[universe][index_chains] = False

                    # Keeps evolving until the appereance of an already used node or before appeared
                    repeated_nodes = False
                    while not repeated_nodes:
                        # Evolution of the actual chain in the window specified by the universe chains length
                        updatables = ECA.eca.compute_next_generation(restrain_window=True,window_range=window_range)
                        Grph.Graphics.graphics.updatable_elements.add(updatables[1]); Grph.Graphics.graphics.updatable_rects += updatables[0]
                        # Chain resulted of the evolution
                        window_evolution = ECA.eca.get_actual_evolution_row(window_range)
                        chain_int = (window_evolution*self.conversion_matrix).sum()
                        """ print('Resulted chain integer >>',chain_int) """
                        relations.append((previous_node, chain_int))
                        # Verifies the chain hasn't appeared yet
                        if type(computed_chains[universe][chain_int]) == bool:
                            repeated_nodes = True
                            break
                        else:
                            computed_chains[universe][chain_int] = False
                            previous_node = chain_int
                    """ print('Computed chains >>', computed_chains) """
                    # When a three or a leaf has been found there's a jump in the evolution rows leaving a blank row to identify the different trees generated
                    ECA.eca.update_evolution_row(2)
            # Generates the graph for the actual universe
            self.generate_graph(universe+1,relations,index_hex_colors=index_hex_colors)
            index_hex_colors += 1
            if index_hex_colors >= len(HEX_COLORS_LIST): index_hex_colors = 0
        print('\n<--- The compute of attractors finished in {} sec --->'.format(time.time()-starting_time))
    
    def generate_graph(self,universe,relations,index_hex_colors:int=0):
        print('<--- Generating graph --->')
        # Creates the graph
        graph_nx = nx.DiGraph()
        graph_nx.add_edges_from(relations)
        graph = ig.Graph(directed=True); colours = []; labels = []
        # Adds the number of nodes
        graph.add_vertices(1<<universe)
        # Adds the nodes relations
        graph.add_edges(relations)
        # Adds the labels of the nodes
        labels.extend(list(np.arange(1<<universe)))
        # Adds the colors of the trees in this universe
        colours.extend([ HEX_COLORS_LIST[index_hex_colors] for _ in range(1<<universe) ])
        # Recovers the cycles
        print('Number nodes >>',1<<universe)
        for cycle in nx.simple_cycles(graph_nx):
            # 1st element: Number predecessors
            # 2nd element: Number of node
            more_predecessors_node = [-1,0]
            for node in cycle:
                sum_predecessors = sum(neighbour for neighbour in graph_nx.predecessors(node))
                if more_predecessors_node[0] < sum_predecessors: more_predecessors_node = [sum_predecessors,node]
            colours[more_predecessors_node[1]] = COLOUR_ATTRACTOR
            print('Attractor >> ', more_predecessors_node[1])


        # Adds the labels and colors of each vertex
        graph.vs['label'] = labels
        graph.vs['color'] = colours
        # Plots the graph
        graph_name = "./graphs/graph1_universe_{}.eps".format(universe)
        visual_style = {}
        # Set bbox and margin
        image_size = self.sizes_igraph[universe]
        visual_style["bbox"] = (image_size,image_size)
        visual_style["margin"] = 25
        # Set vertex properties
        visual_style["vertex_size"] = 20
        visual_style["vertex_label_size"] = 8
        # Don't curve the edges
        visual_style["edge_curved"] = False
        # Layout
        """ if universe > 9:
            visual_style["layout"] = graph.layout('rt_circular') """
        # Plot the graph
        ig.plot(graph, graph_name, **visual_style)
        print('<--- Image size: {} --->'.format((image_size,image_size)))
        print('<--- Graph sucessfully created with the name {} --->\n\n'.format(graph_name))
    
    # Code intended to remove the topological alike trees of the attractors process
    # Nevertheless the second library considered(networkx) wasn't that useful to make the image of the graph
    # even though it's useful for analysing the graph, thus this code wasn't implemented due to lack of
    # knowledge of the behaviour of other rules beside 110
    """ def compute_attractors_2(self):
        print('<--- Preparing to start the compute --->')
        self.get_sizes_range(); self.get_binary_chains()
        # Copy of the binary list that will be removed through the appearances in the compute process
        computed_chains = list(self.binary_chains)
        # Center of the evolution row
        center_cell = int(ECA.eca.number_cells_1D/2)
        index_hex_colors = 0
        print('<--- Starting attractors compute --->')

        # Loop for every chains power universe
        for universe in range(self.sizes[0]-1, self.sizes[1]):
            print('<--- Computing attractors for the universe power {} --->'.format(universe+1))
            self.conversion_matrix = self.conversion_matrix_bin_decimal(universe+1, self.conversion_matrix)
            starting_cell = center_cell - int((universe+1)/2)
            # print('index chains >>',len(self.binary_chains[universe]))
            window_range = (starting_cell+1,starting_cell+universe+2)
            # list of the relations
            relations = []
            # Mask used to shorten the values of bit string into lenght of the actual universe
            bit_mask = 0; len_universe = len(computed_chains[universe])
            for _ in range(universe): 
                bit_mask += 1; bit_mask <<= 1
            print('<--- Bit mask: {} --->'.format(bit_mask))

            # Loop through the available chains of the universe
            for index_chains in range(len(self.binary_chains[universe])):

                # Validates it's still a string, meaning this node hasn't been explored yet in the three
                if type(computed_chains[universe][index_chains]) == str:

                    # print('index chain >> ', index_chains)
                    # Loops through the characters of the binary chain
                    updatables = []; previous_node = int(computed_chains[universe][index_chains],2)
                    for index_value_chain in range(len(computed_chains[universe][index_chains])):
                        updatables = ECA.eca.update_cell_status(starting_cell+index_value_chain,True if computed_chains[universe][index_chains][index_value_chain] == '1' else False, invert=False, graphical_cell=True)
                        Grph.Graphics.graphics.updatable_elements.add(updatables[0]); Grph.Graphics.graphics.updatable_rects.append(updatables[1])
                    
                    # As the chain has been used then it's no available anymore to be used
                    computed_chains[universe][index_chains] = False
                    # Verifiying the topological alike versions of the actual starting node
                    for index in self.shift_derived_nodes(index_chains,bit_mask,len_universe):
                        # Noticed that a derived node by shifting need no computing
                        if type(computed_chains[universe][index]) == str:
                            # print('Derived chain from initial node also removed from computation: ',index)
                            computed_chains[universe][index] = False

                    # Keeps evolving until the appereance of an already used node or before appeared
                    repeated_nodes = False
                    while not repeated_nodes:
                        # Evolution of the actual chain in the window specified by the universe chains length
                        updatables = ECA.eca.compute_next_generation(restrain_window=True,window_range=window_range)
                        Grph.Graphics.graphics.updatable_elements.add(updatables[1]); Grph.Graphics.graphics.updatable_rects += updatables[0]
                        # Chain resulted of the evolution
                        window_evolution = ECA.eca.get_actual_evolution_row(window_range)
                        chain_int = (window_evolution*self.conversion_matrix).sum()
                        # print('Resulted chain integer >>',chain_int)

                        # Verifiying the topological alike versions of the resultant chain
                        for index in self.shift_derived_nodes(chain_int,bit_mask,len_universe):
                            # Noticed that a derived node by shifting need no computing
                            if type(computed_chains[universe][index]) == str:
                                # print('Derived chain also removed from computation: ',index)
                                computed_chains[universe][index] = False

                        relations.append([previous_node, chain_int])

                        # Verifies the chain hasn't appeared yet
                        if type(computed_chains[universe][chain_int]) == bool:
                            repeated_nodes = True
                            break
                        else:
                            computed_chains[universe][chain_int] = False
                            previous_node = chain_int
                    # When a three or a leaf has been found there's a jump in the evolution rows leaving a blank row to identify the different trees generated
                    ECA.eca.update_evolution_row(2)
            # Generates the graph for the actual universe
            # self.generate_graph(universe+1,index_hex_colors=index_hex_colors,ending_universe=8)
            self.actual_universe = universe+1
            print('relations >> ', relations)
            shells = self.define_shell_leves(relations)
            self.graph_attractors(relations,universe+1,shells)
            # self.generate_graph(universe+1,index_hex_colors=index_hex_colors,ending_universe=8)
            index_hex_colors += 1
            if index_hex_colors >= len(HEX_COLORS_LIST): index_hex_colors = 0

    def shift_derived_nodes(self,node,bit_mask,len_universe):
        aux_node = node
        derived_nodes = []
        # Moving left
        while aux_node:
            aux_node = (aux_node >> 1) & bit_mask
            if aux_node < len_universe: derived_nodes.append(int(aux_node))
        return derived_nodes

    def define_shell_leves(self,relations):
        uniques_nodes,nodes_count = np.unique(relations,return_counts=True)
        shells, previous_level_nodes, level_nodes = [],set(),set(); aux_relations = list(relations)
        # First level only roots of threes
        for index_count in range(nodes_count.size):
            # As the node has only been referenced once means it's the root of a three
            if nodes_count[index_count] == 1: level_nodes.add(uniques_nodes[index_count])
        print('Roots >> ', len(level_nodes), level_nodes)
        
        # Loops until no more nodes get added for the shells levels
        more_levels = True
        while more_levels:
            shells.append(list(level_nodes)); previous_level_nodes = list(level_nodes)
            level_nodes.clear(); index_relations = 0
            
            while index_relations < len(aux_relations):
                if aux_relations[index_relations][0] in previous_level_nodes:
                    level_nodes.add(aux_relations[index_relations][1])
                    del aux_relations[index_relations]
                else: index_relations += 1

            more_levels = bool(level_nodes)
        
        # The left relations correspond to loops
        if aux_relations:
            for relation in aux_relations:
                shells[0].append(relation[0])
                self.list_attractors.append(relation[0])
        return shells

    def graph_attractors(self,relations,universe,shells=None):
        mpl.use('Agg')
        plt.figure(figsize=self.sizes_graph[universe])

        graph = nx.DiGraph()
        graph.add_edges_from(relations,color='red')

        for cycle in nx.simple_cycles(graph):
            print('Cycles >> ', cycle)

        #pos = nx.kamada_kawai_layout(graph)
        #pos = nx.shell_layout(graph, shells,rotate=90,scale=2.5)
        pos = nx.spring_layout(graph,1/sqrt(len(relations)/2))
        #pos = nx.circular_layout(graph)
        #pos = nx.planar_layout(graph)
        #pos = nx.spiral_layout(graph)
        nx.draw_networkx_nodes(graph, pos)
        nx.draw_networkx_edges(graph, pos)
        nx.draw_networkx_labels(graph, pos)
        plt.savefig("./graphs/graph2_universe_{}.png".format(universe)) """