import YLDOSs as YLs
a = YLs.YLDOSs('vasprun.xml')

# a.pplot(_atoms=[0,1,3],_orbits=[['s'],['p'],['total']]).show()
fig = a.pplot(_orbits=[['s','p','d','total']])
# fig.update_xaxes(range=[0,5])
# fig.update_yaxes(range=[0,20])
fig.show()

# print(a.getDosbyIndex(0).getType())

# for i in a.getbyType('Y'):
#     print(i.getIndex())


# a.pplot(_atoms=[0,1,3], _orbits=[['s'],['p'],['d']]).show()





    # def toYLDosFromDat(self, filepath):
    #     self.__filepath = filepath

    #     _keys = []
    #     _data = []
    #     with open(self.__filepath,'r') as f:
    #         line = f.readline().strip()
    #         _keys = line[1:].split()

    #         while True:
    #             line = f.readline().strip()
    #             if not line:
    #                 break
    #             _data.append(line.split())

    #     CONVERT = {}
    #     for (d,j) in enumerate(_keys):
    #         CONVERT[j] = []
    #         for i in _data:
    #             CONVERT[j].append(float(i[d]))

    #     self.__data_json = CONVERT
    #     self.__data = pd.DataFrame(CONVERT)
    #     return self