def create_komodo_input():
    
    komodo_input = f"""\
! Mode card
%MODE
FORWARD

! Case card
%CASE
TEST
TEST CASE

! XSEC CARD
%XSEC
FILE data/komodo/komodo_XSEC.txt

%GEOM
9 9 19         ! number of assembly in x, y, z directions
10.0 20.0 20.0 20.0 20.0 20.0 20.0 20.0 20.0    !x-direction assembly size in cm
1      8    8    8    8    8    8    8    8     !x-direction assembly divided into 2 (10 cm each)
20.0 20.0 20.0 20.0 20.0 20.0 20.0 20.0 10.0    !y-direction assembly size in cm
8      8    8    8    8    8    8    8    1     !y-direction assembly divided into 2 (10 cm each)
19*20.0                                         !z-direction assembly  in cm
19*1                                            !z-direction nodal is not divided
4                                               !np number of planar type
1  13*2  4*3  4                                 !planar assignment (from bottom to top)
! Planar_type_1 (Bottom Reflector)
  4  4  4  4  4  4  4  4  4
  4  4  4  4  4  4  4  4  4
  4  4  4  4  4  4  4  4  4
  4  4  4  4  4  4  4  4  4
  4  4  4  4  4  4  4  4  0
  4  4  4  4  4  4  4  4  0
  4  4  4  4  4  4  4  0  0
  4  4  4  4  4  4  0  0  0
  4  4  4  4  0  0  0  0  0
! Planar_type_2 (Fuel)
  3  2  2  2  3  2  2  1  4
  2  2  2  2  2  2  2  1  4
  2  2  2  2  2  2  1  1  4
  2  2  2  2  2  2  1  4  4
  3  2  2  2  3  1  1  4  0
  2  2  2  2  1  1  4  4  0
  2  2  1  1  1  4  4  0  0
  1  1  1  4  4  4  0  0  0
  4  4  4  4  0  0  0  0  0
! Planar_type_3 (Fuel+Partial Control Rods)
  3  2  2  2  3  2  2  1  4
  2  2  2  2  2  2  2  1  4
  2  2  3  2  2  2  1  1  4
  2  2  2  2  2  2  1  4  4
  3  2  2  2  3  1  1  4  0
  2  2  2  2  1  1  4  4  0
  2  2  1  1  1  4  4  0  0
  1  1  1  4  4  4  0  0  0
  4  4  4  4  0  0  0  0  0
! Planar_type_4 (Top reflectors)
  5  4  4  4  5  4  4  4  4
  4  4  4  4  4  4  4  4  4
  4  4  5  4  4  4  4  4  4
  4  4  4  4  4  4  4  4  4
  5  4  4  4  5  4  4  4  0
  4  4  4  4  4  4  4  4  0
  4  4  4  4  4  4  4  0  0
  4  4  4  4  4  4  0  0  0
  4  4  4  4  0  0  0  0  0
! Boundary conditions
! 0 = zero-flux
! 1 = zero-incoming current
! 2 = reflective
! (east), (west), (north), (south), (bottom), (top)
   1       2       2        1        1        1

%ITER
1200 5 1.e-5 1.e-5 15 40 20 80 ! 5 inner iterations per outer, and fission extrapolate every 15 outer iterations
"""
    
    with open('data/komodo/komodo_input.txt', 'w') as f:
        f.write(komodo_input)

    print(f"Done! Run komodo with input file: \nkomodo data/komodo/komodo_input.txt")

if __name__ == "__main__":
    create_komodo_input()