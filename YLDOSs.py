import xml.etree.ElementTree as ET
from lxml import etree

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio



class YLDOS:
    __filepath = None
    __data = None
    __data_json = None
    __fig = None
    __index = None
    __Ele = None
    def __init__(self, _data=None, _index = None, _ele = None):
        self.__data_json = _data
        self.__data = pd.DataFrame(_data)
        self.__index = _index
        self.__Ele = _ele
    def getType(self):
        return self.__Ele
    def getIndex(self):
        return self.__index
    def _plot(self, fig, Orbit=None):
        _data = self.__data
        _KEYS = self.__data_json.keys()
        if 'Energy' in _KEYS:
            _ENERGY = _data['Energy']
        else:
            _ENERGY = _data['energy']

        if not Orbit:
            Orbit = _data.keys()
        for i in Orbit:
            if i == 'energy' or i == 'Energy':
                continue
            if i == 'total':
                fig.add_trace(go.Scatter(x=_ENERGY, y=_data[i],
                                    mode='lines',
                                    name=f'Atom: {self.__index}  Oribit: {i}',
                                    hovertext=f'Atom: {self.__index}  Oribit: {i}',
                                    fill='toself'
                                    ))
            else:
                fig.add_trace(go.Scatter(x=_ENERGY, y=_data[i],
                                    mode='lines',
                                    name=f'Atom: {self.__index}  Oribit: {i}',
                                    hovertext=f'Atom: {self.__index}  Oribit: {i}',
                                    fill='none'
                                    ))
    def getData(self):
        return self.__data
    def getDataJson(self):
        return self.__data_json
    def getFilePath(self):
        return self.__filepath
    
    ## Orbit  ['s','p','d','f','tot']
    def pplot(self,Orbit=None):
        if self.__data is None:
            return None

        fig = go.Figure()
        self._plot(fig, Orbit)
    
        fig.add_hline(y=0, line_dash="dash",line_width=1, line_color="red")
        fig.add_vline(x=0, line_dash="dash",line_width=1, line_color="red")

        fig.update_layout(xaxis={"showgrid": False,"range":[-5,5]}, 
                            yaxis={"showgrid": False,"range":[0,5]},
                            width=1000, height=800,
                            plot_bgcolor="rgba(255, 255, 255, 1)", 
                            paper_bgcolor="rgba(255, 255, 255, 1)",
                            font_family="Times New Roman",
                            font_color="black",
                            title_font_family="Times New Roman",
                            title_font_color="black",
                            legend_title_font_color="green",
                            yaxis_title="Density of states (states/eV)",
                            xaxis_title= 'Energy / eV',
                            font=dict(size=18,),
                            )
        return fig
    


class YLDOSs:
    __filepath = None
    __EFERMI = None
    __TOTAL_DOS = None
    __IONs_DATA = None

    def __init__(self, filepath):
        self.__filepath = filepath
        tree = etree.parse(self.__filepath)
        root = tree.getroot()

        # 查找 DOS 数据
        dos_elements = root.findall('.//calculation/dos')[0]
        efermi_element = dos_elements.find('i[@name="efermi"]')
        __EFERMI = float(efermi_element.text.strip())

        TOTAL_FIELD = dos_elements.findall('.//total//field')
        TOTAL_VALUE = dos_elements.findall('.//total//set//set//r')

        TOTAL_DOS = {}
        for ind,i in enumerate(TOTAL_FIELD):
            TOTAL_DOS[i.text.strip()] = []

            for j in TOTAL_VALUE:
                _TEXT = j.text.strip().split()
                if i.text.strip() == 'energy':
                    TOTAL_DOS[i.text.strip()].append(round(round(float(_TEXT[ind]),3)-__EFERMI,5))
                else:
                    TOTAL_DOS[i.text.strip()].append(round(float(_TEXT[ind]),5))

        PARTIAL_FIELD = dos_elements.findall('.//partial//field')
        PARTIAL_FIELD = [i.text.strip() for i in PARTIAL_FIELD]

        IONs = dos_elements.findall('.//partial//set[@comment]//set[@comment]')
        IONs_TYPES = root.findall(".//atominfo/array[@name='atoms']/set/rc")
        IONs_type_array = []
        for _ty in IONs_TYPES:
            IONs_type_array.append(_ty.getchildren()[0].text.strip())

        self.__IONs_DATA = []

        for _index,_ION in enumerate(IONs):
            # print(_ION.getparent().get('comment'))
            PARTIAL_DOS = {}
            for ind,_field in enumerate(PARTIAL_FIELD):
                PARTIAL_DOS[_field] = []
                
                for _r in _ION.findall('.//r'):
                    _TEXT = _r.text.strip().split()
                    if _field == 'energy':
                        PARTIAL_DOS[_field].append(round(round(float(_TEXT[ind]),3)-__EFERMI,5))
                    else:
                        PARTIAL_DOS[_field].append(round(float(_TEXT[ind]),5))
            PARTIAL_DOS_TOTAL = []
            for i in range(len(PARTIAL_DOS['energy'])):
                total = 0
                for j in PARTIAL_DOS.keys():
                    if j != 'energy':
                        total += PARTIAL_DOS[j][i]
                PARTIAL_DOS_TOTAL.append(total)
            PARTIAL_DOS['total'] = PARTIAL_DOS_TOTAL
            PARTIAL_DOS = YLDOS(PARTIAL_DOS, _index, _ele = IONs_type_array[_index])
            self.__IONs_DATA.append(PARTIAL_DOS)
            self.__EFERMI = 0
        
        for i in PARTIAL_FIELD:
            if i == 'energy':
                continue
            elif i == 'total':
                continue
            TOTAL_DOS[i] = []
            for j in range(len(TOTAL_DOS['energy'])):
                TT = 0
                for _ION in self.__IONs_DATA:
                    TT +=_ION.getDataJson()[i][j]
                TOTAL_DOS[i].append(TT)
        
        if 'integrated' in TOTAL_DOS.keys():
            del TOTAL_DOS['integrated']
        self.__TOTAL_DOS = YLDOS(TOTAL_DOS, _index='total', _ele = 'total')
        
    def getTotalDos(self):
        return self.__TOTAL_DOS
    
    def getDosbyIndex(self,index):
        return self.__IONs_DATA[index]
    
    def pplot(self, _atoms=None,_orbits=None):

        _ATOMS = []
        if _atoms == None:
            _ATOMS = [self.__TOTAL_DOS]
        else:
            if 'total' in _atoms:
                _atoms.remove('total')
                _ATOMS = [self.__TOTAL_DOS]
            
            list(map(lambda x:_ATOMS.append(self.__IONs_DATA[x]) ,_atoms))
        if _orbits is None:
            _orbits = [None for i in range(len(_ATOMS))]
        elif len(_orbits) != len(_ATOMS):
            raise Exception('The length of _atoms and _orbits must be the same.')

        fig = go.Figure()
        for ind,_atom in enumerate(_ATOMS):
            _atom._plot(fig, Orbit = _orbits[ind])
        
        fig.add_hline(y=0, line_dash="dash",line_width=1, line_color="red")
        fig.add_vline(x=0, line_dash="dash",line_width=1, line_color="red")


        fig.update_layout(xaxis={"showgrid": False,
                                #  "range":[-5,5]
                                 }, 
                            yaxis={"showgrid": False,
                                #    "range":[0,5]
                                   },
                            width=1000, height=800,
                            plot_bgcolor="rgba(255, 255, 255, 1)", 
                            paper_bgcolor="rgba(255, 255, 255, 1)",
                            font_family="Times New Roman",
                            font_color="black",
                            title_font_family="Times New Roman",
                            title_font_color="black",
                            legend_title_font_color="green",
                            yaxis_title="Density of states (states/eV)",
                            xaxis_title= 'Energy / eV',
                            font=dict(size=18,),
                            )
        return fig
    
    def getbyType(self, _type='total'):
        if _type == 'total':
            return self.__TOTAL_DOS
        else:   
            _TYPES = []
            for i in self.__IONs_DATA:
                if i.getType() == _type:
                    _TYPES.append(i)
            return _TYPES
    def getbyIndex(self, _index):
        return self.__IONs_DATA[_index]