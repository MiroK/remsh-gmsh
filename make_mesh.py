import subprocess, os, itertools, time
from mpi4py import MPI as pyMPI
from fill_mesh import fill_mesh
import numpy as np

from dolfin import (Mesh, mpi_comm_world, mpi_comm_self, MeshPartitioning)


def msh_read(msh_file):
    '''Get nodes and 3-cells from msh_file'''
    assert os.path.splitext(msh_file)[1] == '.msh'

    nodes, cells = [], []
    with open(msh_file, 'r') as f:
        # Read unitl node list
        next(itertools.dropwhile(lambda l: 'Nodes' not in l, f))
        nnodes = int(next(f).strip())

        while nnodes:
            nnodes -= 1
            row, x, y, z = map(float, next(f).strip().split())
            nodes.append((x, y))
        assert next(f).strip() == '$EndNodes'

        assert next(f).strip() == '$Elements' 
        nelements = int(next(f).strip())

        while nelements:
            nelements -= 1
            line = map(int, next(f).strip().split())
            # Is this triangle?
            if line[1] == 2:
                cells.extend(line[-3:])
        assert next(f).strip() == '$EndElements'
    nodes = np.array(nodes)
    # Gmsh uses 1 based indexing
    cells = np.array(cells) - 1

    # At this point we might have more nodes than used for cell definition
    used_nodes_idx = list(set(cells))
    # Clip
    nodes = nodes[used_nodes_idx]
    # Remap cells
    mapping = dict(zip(used_nodes_idx, range(len(used_nodes_idx))))
    cells = [mapping[v] for v in cells]

    assert set(range(len(nodes))) == set(cells)
    # Finally
    cells = np.array(cells, dtype='uintp')
    cells = cells.reshape((-1, 3))

    return nodes, cells


def get_geo_file(x, y, rad):
    '''Generate unit square mesh refinde near circle@(x, y) with radius'''
    rank = pyMPI.COMM_WORLD.rank
    # Only root spaws
    if rank == 0:
        constants = [('x' , x), ('y', y), ('radius', rad)]
        constants = sum((['-setnumber', c, str(v)] for c, v in constants), [])

        msh_file = 'square_with_fine_circle_x%g_y%g_radius%g.msh' % (x, y, rad)
        not os.path.exists(msh_file) or os.remove(msh_file)
        
        args = ['-2', 'square_with_fine_circle.geo'] + constants + ['-o', msh_file]
        # NOTE: -v 0 set verbosity to shut gmsh up
        pyMPI.COMM_SELF.Spawn('gmsh', args=args, maxprocs=1)

        while not os.path.exists(msh_file):
            time.sleep(5E-1)
        
        return msh_file

    
def get_mesh(msh_file):
    '''Load dolfin mesh from mesh file'''
    comm = pyMPI.COMM_WORLD
    rank = comm.rank

    mesh = Mesh()
    # Root makes coordinates
    if rank == 0:
        root, ext = os.path.splitext(msh_file)
        assert ext == '.msh'

        coordinates, cells = msh_read(msh_file)

        fill_mesh(coordinates.flatten(),
                  np.fromiter(cells.flat, dtype='uintp'), 2, 2, mesh)
    comm.Barrier()
    MeshPartitioning.build_distributed_mesh(mesh)
    mesh.order()
    
    return mesh
