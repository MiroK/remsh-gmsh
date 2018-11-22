from dolfin import *
from make_mesh import get_geo_file, get_mesh


def solve_poisson(V, f0, dt=1E-3):
    u, v = TrialFunction(V), TestFunction(V)

    a = Constant(1./dt)*inner(u, v)*dx + inner(grad(u), grad(v))*dx

    f0 = interpolate(f0, V)
    as_backend_type(f0.vector()).update_ghost_values()
    
    L = Constant(1./dt)*inner(f0, v)*dx

    uh = Function(V)
    A, b = assemble_system(a, L)

    solver = KrylovSolver('cg', 'hypre_amg')
    solver.set_operators(A, A)
    solver.parameters['monitor_convergence'] = True

    x = uh.vector()
    solver.solve(x, b)

    as_backend_type(x).update_ghost_values()
    
    return uh

# --------------------------------------------------------------------

if __name__ == '__main__':
    import numpy as np
    
    f = Expression('x[0]+x[1]', degree=1)

    theta = np.linspace(0, 2*np.pi, 10)
    rad = 0.2
    
    x, y = iter(0.5 + rad*np.cos(theta)), iter(0.5 + rad*np.sin(theta))
    
    
    msh_file = get_geo_file(next(x), next(y), rad)
    mesh0 = get_mesh(msh_file)

    V0 = FunctionSpace(mesh0, 'CG', 1)
    f0 = interpolate(f, V0)

    out = File('f.pvd')
    for i, (xi, yi) in enumerate(zip(x, y)):
        f0.set_allow_extrapolation(True)
        
        msh_file = get_geo_file(xi, yi, rad)
        mesh1 = get_mesh(msh_file)

        V1 = FunctionSpace(mesh1, 'CG', 1)
        f1 = solve_poisson(V1, f0)

        f0 = f1
        f0.rename('f', '')
        out << (f0, float(i))
