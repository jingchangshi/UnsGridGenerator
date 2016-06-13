LC = 0.1;
Point(1) = {0,0,0,LC};
Point(2) = {1,0,0,LC};
Point(3) = {1,1,0,LC};
Point(4) = {0,1,0,LC};
Line(1) = {1,2};
Line(2) = {2,3};
Line(3) = {3,4};
Line(4) = {4,1};

Line Loop(5) = {1,2,3,4};

Plane Surface(6) = {5};

Transfinite Surface{6} = {1,2,3,4};
Recombine Surface{6};
