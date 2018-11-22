DefineConstant[
x = {1, Name "X"}
y = {1, Name "Y"}
radius = {1, Name "rad"}
];

size = 0.1;

Point(1) = {0, 0, 0, size};
Point(2) = {1, 0, 0, size};
Point(3) = {1, 1, 0, size};
Point(4) = {0, 1, 0, size};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

Line Loop(1) = {1, 2, 3, 4};

Plane Surface(1) = {1};

Point(5) = {x, y, 0, size};
Point(6) = {x+radius, y, 0, size};
Point(7) = {x, y+radius, 0, size};
Point(8) = {x-radius, y, 0, size};
Point(9) = {x, y-radius, 0, size};

c0 = newl;
Circle(c0) = {6, 5, 7};

c1 = newl;
Circle(c1) = {7, 5, 8};

c2 = newl;
Circle(c2) = {8, 5, 9};

c3 = newl;
Circle(c3) = {9, 5, 6};


Field[1] = Distance;
Field[1].EdgesList = {c0, c1, c2, c3};

Field[2] = Threshold;
Field[2].IField = 1;
Field[2].LcMin = size/20.;
Field[2].LcMax = size;
Field[2].DistMin = 0.2*radius;
Field[2].DistMax = 0.6*radius;

Background Field = 2;