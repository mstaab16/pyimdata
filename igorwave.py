import numpy as np
class IgorWave:  
    def __init__(self, name="", data=None, notes=None):
        if type(data) == None:
            data = np.array([])
        if type(notes) == None:
            notes = []
        self.name = name
        self.data = np.array(data)
        self.notes = notes
        if data.shape != [0]:
            self.rows = data.shape[0]
            self.columns = data.shape[1]
        
        self.xoffset, self.yoffset, self.xdelta, self.ydelta = 0,0,1,1
        self.xunit, self.yunit = "",""
    
    def save_itx(self, savename):
        from IgorIO import save_itx
        save_itx(self, savename)
    
    def get_edc(self, index):
        if (type(index) == int) or (type(index) == list):
            return self.data[index]
        elif type(index) == tuple:
            start, stop = index
            return self.data[start:stop]
        else:
            print("I could not get the edc(s)...")
            
    def get_mdc(self, index):
        tempdata = self.data.transpose()
        if (type(index) == int) or (type(index) == list):
            return tempdata[index]
        elif type(index) == tuple:
            start, stop = index
            return tempdata[start:stop]
        else:
            print("I could not get the mdc(s)...")
