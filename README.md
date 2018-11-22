# ReMSH-Gmsh

To the best of my knowledge adaptivity (coarsening in particular) is not a
strength of FEniCS. If adaptivity is necessary one alternative is to remesh
during computations. This is the approach implemented here;

1. your application provides a new Gmsh template file or flags modifying the existing one
2. `ReMSH-Gmsh` asks Gmsh for the mesh file and then loads the mesh in memory

It seems we can do the above reliably and __in parallel__.

## TODO
- How to await termination of spawned process with Gmsh (currently `sleep`)
- Awoid msh file (using Gmsh Python [API](http://gmsh.info/doc/texinfo/gmsh.html#Gmsh-API))