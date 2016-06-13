# Introduction

There are vairous ways to generate unstructured grid. A very powerful method is the face-based, since for finite volume method, face list is needed. Indeed, the core part of finite volume method is in the interfaces.

Currently, this repo only supports the face-based method. Generate a mesh file in Gmsh format. Then import it and convert to the face based format.

# Face-based way

Format in 2D is as follows,

> npoints, nfaces, ncells
> x_1, y_1, z_1
> ......
> x_npoints, y_npoints, z_npoints
> no of points for face 1, p1, p2, ..., cell 1, cell 2
> ......
> no of points for face nfaces, p1, p2, ... cell 1, cell 2

Gmsh mesh file format should be referred to its [homepage](http://gmsh.info/doc/texinfo/gmsh.html).

