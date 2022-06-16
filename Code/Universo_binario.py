
def generate_binary_chains(power:int) -> list:
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
    chains = [ [] for _ in range(power) ]; chains[0] = ["0","1"]
    # Loop of the consecutive universe of powers
    for p in range(power-1):
        # Loop for the generation of the chains of a given universe power
        for previous_chain in chains[p]:
            chains[p+1].extend([previous_chain+str(0), previous_chain+str(1)])

    return chains




chains = generate_binary_chains(3)
print('<--- Chains --->\n >>',chains)
print('Chains(2,2,1) >>',chains[2][2][1])