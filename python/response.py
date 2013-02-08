import sys
import re

def read_matrix(filename):
    """
    It's worth remembering what the matrix is, exactly.
    Each row is the coefficients for a response.
    Each column is the DVs to which they apply.
    We're assuming that we're generating the design
    vector from the DVs in a consistent way:
    constant, linear terms, interactions, squares
    """
    fp = open("coefficient_matrix.txt", 'rb')
    matrix_text = fp.read()
    fp.close()
    lines = matrix_text.split("\n")
    lines.pop(0) # header

    matrix = []
    for line in lines:
        row = line.strip().split("\t")
        row.pop(0) # response name
        matrix.append([float(xx) for xx in row])

    return matrix

def get_interactions(dvs):
    """
    Standard order for interactions:
    All interactions with the first dv, then all
    remaining interactions for the second dv, etc.
    """
    if len(dvs) == 0: return []
    interactions = get_interactions(dvs[1:])
    return [dvs[0]*dv for dv in dvs[1:]] + interactions

def scale_dvs(dvs):
    translate = [0.36, 9, 3, 5.734, 22, 97.5, 17, 3.375, 0.73]
    scale = [0.12, 2, 3, 0.234, 3, 12.5, 3, 0.375, 0.27]
    translate_and_scale = lambda xx, yy, zz: (xx-yy)/zz
    return map(translate_and_scale, dvs, translate, scale)
    

def design_vector(dvs):
    return [1] + dvs + get_interactions(dvs) + \
           [dv**2 for dv in dvs]



# determine which seats to compute
seats = [ss for ss in sys.argv if
             ss in ['2','4','6']]

if len(seats) == 0:
    message = "  usage: python response.py [2] [4] [6]"
    message += "\n  must specify a number of seats"
    message += "\n  examples:"
    message += "\n  python response.py 6"
    message += "\n  python response.py 2 4 6"
    print message
    exit(1)

# read the matrix
matrix = read_matrix("coefficient_matrix.txt")

ndvs = 9 # 9 decision variables per aircraft
totalndvs = ndvs * len(seats)

nresp = 9 # 9 responses per aircraft
respoffset = {"2":nresp*0,"4":nresp*1,"6":nresp*2}

# main loop
line = sys.stdin.readline()
while line:
    # take dvs from stdin
    variables = [float(xx) for xx in 
                   re.split("[ ,\t]", line.strip())]
    
    if(totalndvs != len(variables)):
        print "Defective inputs!  Got {}, expected {}.".format(
          len(variables), totalndvs)
        exit(1)

    outputs = []
    # for each number of seats
    for seat in seats:
        # compute design vector from decision variables
        dvs = variables[0:ndvs]
        variables[0:ndvs] = []
        design = design_vector(scale_dvs(dvs))

        # compute each response
        for jj in range(nresp):
            offset = jj + respoffset[seat]
            response = sum(map(lambda xx, yy: xx * yy, design, 
                                          matrix[offset]))
            outputs.append(response)

    # write response to stdout
    print "\t".join([unicode(xx) for xx in outputs])

    # get next line
    line = sys.stdin.readline()
# vim:ts=4:sw=4:expandtab:fdm=indent:ai