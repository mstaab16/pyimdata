import numpy as np
from igorwave import IgorWave

def save_itx(wave, savename, overwrite = False):
    save = True
    import os
    if not overwrite and os.path.exists(savename):
        errorstr = f"Yikes partner, \"{savename}\" was already taken and you said it shouldn't be overwritten! Use save_itx(wave, {savename}, True) to overwrite."
        raise IOError(errorstr)
    with open(savename, "w") as f:
                f.write("IGOR\n")
                f.write(f"WAVES/N=({wave.rows}, {wave.columns})\t{wave.name}\n")
                f.write("BEGIN\n")
                for row in wave.data:
                    f.write("\t" + "\t".join(map(str,row))+ "\n")
                f.write(f'END\nX SetScale/P x {wave.xoffset},{wave.xdelta},{wave.xunit}, {wave.name}; SetScale/P y {wave.yoffset},{wave.ydelta},{wave.yunit}, {wave.name}; SetScale d 0,0,"", {wave.name};\n')
                for i, row in enumerate(wave.notes[2:]):
                    if i==len(wave.notes):
                        f.write("".join(row))
                    else:
                        f.write("".join(row))

def load_itx(filename):
    from ast import literal_eval
    if filename.split(".")[-1] != "itx":
        raise IOError("OUCH! That filename does not end in .itx")
    with open(filename, "r") as f:
        #Initializing some variables to help read
        saveData = False
        data = []
        
        saveNotes = False
        notes = []
            
        for i, line in enumerate(f):
            #Howdy, let's check the file starts with "IGOR"
            if i==0:
                if (line.strip() != "IGOR"):
                    raise IOError("OUCH! That wasn't a proper Igor text file! The first line should be \"IGOR\"")
                    
            #Now we need the size of the wave
            if i==1:
                saveDim, saveName = False, False
                dim, name, l = "", "", ""
                
                for char in line:
                    l += char
                    if  "N=(" in l:
                        saveDim = True
                        
                    if ")\t" in l:
                        saveDim = False
                        saveName = True
                        
                    if saveDim:
                        dim += char
                    
                    if saveName:
                        name += char
                        
                dims = literal_eval(dim)
                xdim, ydim = dims
                name = name.strip()
            
            #Saving the data of the wave
            if line.strip() == "BEGIN":
                saveData = True
            
            #The lines after #END are all the notes, so store that as well as stopping reading the data
            if line.strip() == "END":
                saveData = False
                saveNotes = True
            
            if saveData:
                data.append(line[1:-1].split("\t"))
                
                if line.strip() == "BEGIN":
                    data = []
                    
            if saveNotes:
                notes.append(line)
                #X SetScale/P x -12.3001930749416,0.0615571427345276,"slit deg", Th_m0;
                #SetScale/P y 49.775,0.001,"eV", Th_m0;
                #SetScale d 0,0,"", Th_m0
                sxo, sxd, sxu, syo, syd, syu = False, False, False, False, False, False
                
                #This weird part makes sure we dont overwrite the values on accident
                #the try checks to see if we get an error talking about xoff (which we will if it isnt defined)
                #This is probably horrible code etiquette but hey it works.
                try:
                    xoff == True
                except:
                    xoff, xdel, xunit, yoff, ydel, yunit = "","","","","",""
                
                if "SetScale/P" in line:
                    for char in line:
                        if char == "x":
                            sxo = True
                            continue
                            
                        if char == "y":
                            syo = True
                            continue
                    
                        if sxo and (char == ","):
                            sxo = False
                            sxd = True
                            continue
                            
                        if sxo:
                            xoff += char
                             
                        if sxd and (char == ","):
                            sxd = False
                            sxu = True
                            continue
                            
                        if sxd:
                            xdel += char
                            
                        if sxu and (char == ","):
                            sxu = False
                            continue
                        
                        if sxu:
                            xunit += char
                        
                        if syo and (char == ","):
                            syo = False
                            syd = True
                            continue
                            
                        if syo:
                            yoff += char
                        
                        if syd and (char == ","):
                            syd = False
                            syu = True
                            continue
                            
                        if syd:
                            ydel += char
                            
                        if syu and (char ==","):
                            syu = False
                        
                        if syu:
                            yunit += char
    
                    xoff, xdel, yoff, ydel = float(xoff.strip()),float(xdel.strip()),float(yoff.strip()),float(ydel.strip())
                    

        data = np.array(data).astype(np.float)
    
    wave = IgorWave(name, data, notes)
    wave.xoffset = xoff
    wave.xdelta = xdel
    wave.yoffset = yoff
    wave.ydelta = ydel
    wave.xunit = xunit
    wave.yunit = yunit
    

    return wave



