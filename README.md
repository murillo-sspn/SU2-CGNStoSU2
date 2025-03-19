# SU2-CGNStoSU2
Repository to convert multi-zone CGNS turbomachinery grids into a single SU2 grid

1) For each zone, SU2_DEF converts the CGNS grid into an SU2 grid.
2) Multiple Periodic1 markers of a zone are merged into a single Periodic1 marker. The same is done for Periodic2, Hub, and Shroud.
      https://www.cfd-online.com/Forums/su2/258309-su2-compressor-turbomachinery-case.html
3) Markers that correspond to internal boundary conditions are removed.
4) Grids of multiple zones are merged into a single multi-zone SU2 grid.
