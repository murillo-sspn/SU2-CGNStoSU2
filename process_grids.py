
import os, sys
import subprocess

def main():

    # Inputs
    N_CORES = 2
    cfg_files = ["ID_grid_converter.cfg", "R_grid_converter.cfg", "VD_grid_converter.cfg"]
    grid_files = ["grid_ID.su2", "grid_R.su2", "grid_VD.su2"]
    prefixes = ["ID", "R", "VD"]
    saving_file = "grid_Stage.su2"

    w_dir = os.getcwd()

    def convert_cngs_to_su2_grids():
        # Loop zones
        for i, cfg_file in enumerate(cfg_files):
            subprocess.run(f"mpirun -n {N_CORES} SU2_DEF {cfg_file}",
                           shell=True,
                           stderr=sys.stderr,
                           env=os.environ,
                           cwd=w_dir)

    def load_data_markers():
        
        # Markers containing the following strings in their names
        # will be merged in each zone
        markers_merge = ["HUB","SHROUD","PER1","PER2"]
        markers_remove = ["R_OUTFLOWPassage", "R_INFLOWOUTBlock", "VD_OUTFLOWINBlock", "VD_INFLOWPassage", "VD_OUTFLOWPassage", "VD_INFLOWOUTBlock"]

        data = []

        # Loop grids/ zones
        for i, grid_file in enumerate(grid_files):

            # Add current zone info
            IZONE = i+1

            data.append({})

            # Read zone mesh
            f = open("./" + grid_file)
            _txt = f.readlines()
            f.close()

            N_LINES = len(_txt)

            data[i]["MARKER_TAG"] = []
            data[i]["MARKER_TAG_INDEX"] = []
            data[i]["MARKER_ELEMS"] = []
            data[i]["MARKER_ELEMS_INDEX"] = []

            # Get markers
            prefix = prefixes[i]
            #_txt = _txt.replace("MARKER_TAG= ",f"MARKER_TAG= {prefix}_")
            for j, line in enumerate(_txt):
                if "NMARK" in line:
                    data[i]["NMARK"] = int((line.split("= ")[1]).replace('\n',''))
                    first_index = j
                elif "MARKER_TAG" in line:
                    _marker = (line.split('= ')[1]).replace('\n','')
                    data[i]["MARKER_TAG"].append(f"{prefix}_{_marker}")
                    data[i]["MARKER_TAG_INDEX"].append(j)
                elif "MARKER_ELEMS" in line:
                    data[i]["MARKER_ELEMS"].append(int(line.split("= ")[1]))
                    data[i]["MARKER_ELEMS_INDEX"].append(j)
            N_MARKERS = len(data[i]["MARKER_TAG"])

            # Content from begin until first marker
            txt = _txt[0:first_index]        
            
            # Get mesh data
            data[i]["MESH"] = []
            for i_MARKER in range(N_MARKERS-1):
                i1, i2 = data[i]["MARKER_TAG_INDEX"][i_MARKER]+2, data[i]["MARKER_TAG_INDEX"][i_MARKER+1]
                data[i]["MESH"].append(_txt[i1:i2])
                # Add prefix to regions
            i1, i2 = data[i]["MARKER_TAG_INDEX"][i_MARKER+1]+2, N_LINES
            data[i]["MESH"].append(_txt[i1:i2])

            # Indicator for markers
            indicator = [True] * N_MARKERS

            # Merge periodics, hub and shroud
            for marker_merge in markers_merge:
                N = 0
                i_MARKERS = []
                for i_MARKER in range(N_MARKERS):
                    marker = data[i]["MARKER_TAG"][i_MARKER]
                    if marker_merge in marker:
                        N += 1
                        i_MARKERS.append(i_MARKER)
                # Merge if there are multiple periodics, hub and shroud in the same zone
                if N > 1:
                    for i_MARKER in i_MARKERS[1:]:
                        indicator[i_MARKER] = False
                        data[i]["NMARK"] -= 1
                        data[i]["MESH"][i_MARKERS[0]] += (data[i]["MESH"][i_MARKER])
                        data[i]["MARKER_ELEMS"][i_MARKERS[0]] += data[i]["MARKER_ELEMS"][i_MARKER]
            
            # Remove markers
            for marker_remove in markers_remove:
                for i_MARKER in range(N_MARKERS):
                    marker = data[i]["MARKER_TAG"][i_MARKER]
                    if marker_remove in marker:
                        indicator[i_MARKER] = False
                        data[i]["NMARK"] -= 1
            
            # Print results
            for i_MARKER in range(N_MARKERS):
                print(f'i_MARKER = {i_MARKER}, marker = {data[i]["MARKER_TAG"][i_MARKER]}, indicator = {indicator[i_MARKER]}')
            print(f"")

            # Add markers to txt
            txt += [f"NMARK= {data[i]['NMARK']}\n"]
            for i_MARKER in range(N_MARKERS):
                if indicator[i_MARKER]:
                    txt_temp = [f"MARKER_TAG= {data[i]['MARKER_TAG'][i_MARKER]}\n"]
                    txt_temp += [f"MARKER_ELEMS= {data[i]['MARKER_ELEMS'][i_MARKER]}\n"]
                    txt_temp += data[i]["MESH"][i_MARKER]
                    txt += txt_temp

                    #breakpoint()

                    # Read zone mesh
                    f = open("./out_" + grid_file, "w")
                    for line in txt:
                        f.write(line)
                    f.close()
            
            #breakpoint()

    def merge_grids():
        # Add number of zones info
        NZONE = len(grid_files)
        txt = f"NZONE= {NZONE}\n"

        # Loop grids/ zones
        for i, grid_file in enumerate(grid_files):

            # Add current zone info
            IZONE = i+1
            txt = txt + f"IZONE= {IZONE}\n"

            # Read zone mesh
            f = open("./out_" + grid_file)
            _txt = f.read()
            f.close()

            # Add zone info to stage mesh
            txt = txt + _txt

        # Write final mesh
        f = open("./" + saving_file, "w")
        f.write(txt)
        f.close()

    convert_cngs_to_su2_grids()
    load_data_markers()
    merge_grids()

if __name__ == "__main__":
    main()