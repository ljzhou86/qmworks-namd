__author__ = "Felipe Zapata"


# ================> Python Standard  and third-party <==========
from collections import namedtuple
# import numpy as np

# # ==================> Internal modules <==========
# from noodles import gather
# from qmworks import run
# from qmworks.parsers import parse_string_xyz
# from qmworks.utils import concatMap

# import plams

# ==================> import modules <==========
GridCube = namedtuple("GridCube", ("center", "voxels", "vectors", "grid"))

# =====================================<>======================================


# def main():
#     """
#     Initialize all the parameters required to calculate the cube files
#     containing the density of a photoElectron transfer.
#     """
#     plams.init()
#     project_name = 'CUBE_ET'

#     # create Settings for the Cp2K Jobs
#     cp2k_args = Settings()
#     cp2k_args.basis = "DZVP-MOLOPT-SR-GTH"
#     cp2k_args.potential = "GTH-PBE"
#     cp2k_args.cell_parameters = [50.0] * 3
#     cp2k_args.specific.cp2k.force_eval.dft.scf.added_mos = 100
#     cp2k_args.specific.cp2k.force_eval.dft.scf.diagonalization.jacobi_threshold = 1e-6
#     cp2k_args.specific.cp2k.force_eval.dft.PRINT.mo_cubes.nhomo   = FIXME
#     cp2k_args.specific.cp2k.force_eval.dft.PRINT.mo_cubes.nlumo   = FIXME
#     cp2k_args.specific.cp2k.force_eval.dft.PRINT.mo_cubes.write_cube  = ".true."

#     # Path to the MD geometries
#     path_traj_xyz = "./trajectory_4000-5000.xyz"

#     # all_geometries type :: [String]
#     geometries = split_file_geometries(path_traj_xyz)


# def calculateGrid(timeCoeffs, nmin=None, nmax=None):
#     """
#     """


# def read_cube_file(path_to_cube):
#     """
#     Read a cube files and return the array together with the grid
#     parameters.

#     :param path_to_cube: path to the cube file to read
#     :type path_to_cube: String
#     """
#     def read_int_list_float(xs, n):
#         line = head[n].split()
#         i = int(line[0])
#         floats = list(map(float), line[1:])

#         return i, floats

#     with open(path_to_cube, 'r') as f:
#         head = [next(f) for i in range(6)]
#     # There are 2 initial lines cotaining comments.
#     # Then one line cotaining the grid center and finally
#     # 3 lines with the number of voxels and the axis vector.
#     numat, center = read_int_list_float(head, 2)
#     xStep, xVector = read_int_list_float(head, 3)
#     yStep, yVector = read_int_list_float(head, 4)
#     zStep, zVector = read_int_list_float(head, 5)

#     voxels = (xStep, yStep, zStep)
#     vectors = (xVector, yVector, zVector)
#     # read grid using numpy
#     num_lines = numat + 6
#     arr = np.loadtxt(path_to_cube, skiprows=num_lines)

#     return GridCube(center, voxels, vectors, arr)


# def write_cube_file(center, coordinates, grid_spec, arr):
#     """
#     Write some density using the cubefile format
#     :param center: Center of the grid
#     :type center:
#     """
#     def formatCols(xs, cols=4):
#         if cols == 4:
#             string = '{} {:10.6f} {:10.6f} {:10.6f}\n'
#         elif cols == 5:
#             string = '{} {:10.6f} {:10.6f} {:10.6f} {:10.6f}\n'
#         else:
#             msg = "There is not format for that number of columns "
#             raise NotImplementedError(msg)

#         return string.format(*xs)

#     def printAtom(xs):
#         """
#         Atoms row have the following format:
#         6    0.000000  -11.020792    0.648172    0.001778
#         where the first colums specific the atomic number, the
#         second apparently does not have a clear meaning and
#         the last three are the cartesian coordinates.
#         """
#         rs = [xs[0]] + [0] + xs[1:]

#         return formatCols(rs, cols=5)

#     inp = 'density\ndensity\n'
#     inp += formatCols([numat] + center)
#     inp += formatCols([grid_spec[0, 0], grid_spec[0, 1], 0, 0])
#     inp += formatCols([grid_spec[0, 0], 0, grid_spec[1, 1], 0])
#     inp += formatCols([grid_spec[0, 0], 0, 0, grid_spec[2, 1]])
#     inp += concatMap(printAtom, coordinates)
#     inp +=

#     return inp
