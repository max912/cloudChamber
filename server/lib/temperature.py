class Temperature:

    def __init__(self):
        self.device_file = []

        device_serial = ['28-0516945785ff', '28-041694cb67ff', '28-05169497ecff', '28-0516948f6bff']

        base_dir = '/sys/bus/w1/devices/'

        for i in range(len(device_serial)):
            self.device_file.append(base_dir+device_serial[i]+'/w1_slave')

    def read_temp_raw (self, i):
        f = open(self.device_file[i], 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self, i):
        lines = self.read_temp_raw(i)
        while lines[0].strip()[-3:] != 'YES':
            lines = read_temp_raw(i)
        temp_output = lines[1].find('t=')
        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output+2:]
            temp = float(temp_string)/1000.0
            return temp

    def getTemp(self):
        t1 = self.read_temp(1)
        t2 = self.read_temp(2)
        t3 = self.read_temp(3)
        return ("{\"plate\": \""+str(t1)+"\",\"conduct\": \""+str(t2)+"\",\"glass\": \""+str(t3)+"\"}")

    def getConductT(self):
        return self.read_temp(2)

    def getGlassT(self):
        return self.read_temp(3)
        
    def getPlateT(self):
        return self.read_temp(1)
