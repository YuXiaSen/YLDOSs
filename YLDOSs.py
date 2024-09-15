import xml.etree.ElementTree as ET
from lxml import etree

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio



class YLDOS:
    # 文件路径
    __filepath = None
    # pandas.DataFrame格式数据
    __data = None
    # json数据
    __data_json = None
    # 图框对象
    __fig = None
    # 原子序号
    __index = None
    # 元素类型
    __Ele = None
    #  1 ---> up , 2 ---> down
    __spin = None  
    def __init__(self, _data=None, _index = None, _ele = None, _spin = 1, _filepath=None):
        self.__data_json = _data
        self.__data = pd.DataFrame(_data)
        self.__index = _index
        self.__Ele = _ele
        self.__spin = _spin
        self.__filepath = _filepath
    def getType(self):
        return self.__Ele
    def getSpin(self):
        return self.__spin
    def getIndex(self):
        return self.__index
    def _plot(self, fig, Orbit=None, _spinNo = False):
        
        if _spinNo:
            if self.__spin == 1:
                _spinNo = 'up'
            else:
                _spinNo = 'down'
        else:
            _spinNo = ''

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
                                    name=f'Atom: {self.__index}  Oribit: {i}  {_spinNo}',
                                    hovertext=f'Atom: {self.__index}  Oribit: {i}  {_spinNo}',
                                    fill='toself'
                                    ))
            else:
                fig.add_trace(go.Scatter(x=_ENERGY, y=_data[i],
                                    mode='lines',
                                    name=f'Atom: {self.__index}  Oribit: {i}  {_spinNo}',
                                    hovertext=f'Atom: {self.__index}  Oribit: {i}  {_spinNo}',
                                    fill='none'
                                    ))
    def getData(self):
        return self.__data
    def getDataJson(self):
        return self.__data_json
    def getFilePath(self):
        return self.__filepath
    def toString(self):
        return f'Ele: {self.__Ele} /\ Spin: {"up" if self.__spin == 1 else "down"} /\ Index: {self.__index} /\ filepath: {self.__filepath}'
    
    ## Orbit  ['s','p','d','f','tot']
    def pplot(self,Orbit=None, _spinNo = False):


        fig = go.Figure()
        self._plot(fig, Orbit,_spinNo = _spinNo)
    
        fig.add_hline(y=0, line_dash="dash",line_width=1, line_color="red")
        fig.add_vline(x=0, line_dash="dash",line_width=1, line_color="red")

        fig.update_layout(xaxis={"showgrid": False,}, 
                            yaxis={"showgrid": False,},
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

        _LORBIT = int(root.findall(".//separator[@name='dos']//i[@name='LORBIT']")[0].text.strip())
        if _LORBIT != 11 and _LORBIT != 10:
            raise Exception("LORBIT != 11 or 10")
        
        # 查找 DOS 数据
        dos_elements = root.findall('.//calculation/dos')[0]
        efermi_element = dos_elements.find('i[@name="efermi"]')
        __EFERMI = float(efermi_element.text.strip())

        TOTAL_FIELD = dos_elements.findall('.//total//field')
        TOTAL_VALUE_SPIN1 = dos_elements.findall('.//total//set//set[@comment="spin 1"]//r')
        TOTAL_VALUE_SPIN2 = dos_elements.findall('.//total//set//set[@comment="spin 2"]//r')
        # TOTAL_VALUE = dos_elements.findall('.//total//set//set//r')

        TOTAL_DOS = {'spin1':{},'spin2':{}}
        
        for ind,i in enumerate(TOTAL_FIELD):
            TOTAL_DOS['spin1'][i.text.strip()] = []
            for j in TOTAL_VALUE_SPIN1:
                _TEXT = j.text.strip().split()
                if i.text.strip() == 'energy':
                    TOTAL_DOS['spin1'][i.text.strip()].append(round(round(float(_TEXT[ind]),3)-__EFERMI,5))
                else:
                    TOTAL_DOS['spin1'][i.text.strip()].append(round(float(_TEXT[ind]),5))
            
            TOTAL_DOS['spin2'][i.text.strip()] = []
            for j in TOTAL_VALUE_SPIN2:
                _TEXT = j.text.strip().split()
                if i.text.strip() == 'energy':
                    TOTAL_DOS['spin2'][i.text.strip()].append(round(round(float(_TEXT[ind]),3)-__EFERMI,5))
                else:
                    TOTAL_DOS['spin2'][i.text.strip()].append(-round(float(_TEXT[ind]),5))


        PARTIAL_FIELD = dos_elements.findall('.//partial//field')
        PARTIAL_FIELD = [i.text.strip() for i in PARTIAL_FIELD]

        IONs_spin1 = dos_elements.findall('.//partial//set[@comment]//set[@comment="spin 1"]')
        IONs_spin2 = dos_elements.findall('.//partial//set[@comment]//set[@comment="spin 2"]')


        IONs_TYPES = root.findall(".//atominfo/array[@name='atoms']/set/rc")
        IONs_type_array = []
        for _ty in IONs_TYPES:
            IONs_type_array.append(_ty.getchildren()[0].text.strip())

        self.__IONs_DATA = []
        
        for _index,_ION in enumerate(IONs_spin1):
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
            PARTIAL_DOS = YLDOS(PARTIAL_DOS, _index, _ele = IONs_type_array[_index],_spin=1,_filepath = self.__filepath)
            self.__IONs_DATA.append({'spin1':PARTIAL_DOS})

        
        for _index,_ION in enumerate(IONs_spin2):
            # print(_ION.getparent().get('comment'))
            PARTIAL_DOS = {}
            for ind,_field in enumerate(PARTIAL_FIELD):
                PARTIAL_DOS[_field] = []
                
                for _r in _ION.findall('.//r'):
                    _TEXT = _r.text.strip().split()
                    if _field == 'energy':
                        PARTIAL_DOS[_field].append(round(round(float(_TEXT[ind]),3)-__EFERMI,5))
                    else:
                        PARTIAL_DOS[_field].append(-round(float(_TEXT[ind]),5))
            PARTIAL_DOS_TOTAL = []
            for i in range(len(PARTIAL_DOS['energy'])):
                total = 0
                for j in PARTIAL_DOS.keys():
                    if j != 'energy':
                        total += PARTIAL_DOS[j][i]
                PARTIAL_DOS_TOTAL.append(total)
            PARTIAL_DOS['total'] = PARTIAL_DOS_TOTAL
            PARTIAL_DOS = YLDOS(PARTIAL_DOS, _index, _ele = IONs_type_array[_index],_spin=2, _filepath=self.__filepath)
            self.__IONs_DATA[_index]['spin2'] = PARTIAL_DOS
        self.__EFERMI = 0


        for i in PARTIAL_FIELD:
            if i == 'energy':
                continue
            elif i == 'total':
                continue
            
            TOTAL_DOS['spin1'][i] = []
            for j in range(len(TOTAL_DOS['spin1']['energy'])):
                TT = 0
                for _ION in self.__IONs_DATA:
                    TT +=_ION['spin1'].getDataJson()[i][j]
                TOTAL_DOS['spin1'][i].append(TT)

            TOTAL_DOS['spin2'][i] = []
            for j in range(len(TOTAL_DOS['spin2']['energy'])):
                TT = 0
                for _ION in self.__IONs_DATA:
                    TT +=_ION['spin2'].getDataJson()[i][j]
                TOTAL_DOS['spin2'][i].append(TT)

        if 'integrated' in TOTAL_DOS['spin1'].keys():
            del TOTAL_DOS['spin1']['integrated']
        if 'integrated' in TOTAL_DOS['spin2'].keys():
            del TOTAL_DOS['spin2']['integrated']
        
        
        self.__TOTAL_DOS = {'spin1': YLDOS(TOTAL_DOS['spin1'],_index='total', _ele = 'total',_spin = 1,_filepath=self.__filepath),
                            'spin2': YLDOS(TOTAL_DOS['spin2'],_index='total', _ele = 'total',_spin = 2,_filepath=self.__filepath)}
        if self.__TOTAL_DOS['spin2'].getDataJson()['energy'] == []:
            del self.__TOTAL_DOS['spin2']

        
    def getIonsNum(self):
        return len(self.__IONs_DATA)
    

    def getTotalDos(self, _spin = 'up'):
        _spin = 'spin1' if _spin == 'up' else 'spin2'
        if _spin not in self.__TOTAL_DOS.keys():
            raise Exception('也许没有自旋')
        return self.__TOTAL_DOS[_spin]
    
    def getDosbyIndex(self,index,_spin = 'up'):
        _spin = 'spin1' if _spin == 'up' else 'spin2'
        if _spin not in self.__TOTAL_DOS.keys():
            raise Exception('也许没有自旋')
        return self.__IONs_DATA[index][_spin]
    
    def pplot(self, _atoms=None,_orbits=None, _isSpin = False):
        if _isSpin == True and 'spin2' not in self.__TOTAL_DOS.keys():
            raise Exception('也许没有自旋')

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
        fig.add_hline(y=0, line_dash="solid",line_width=1, line_color="black")

        for ind,_atom in enumerate(_ATOMS):
            if _isSpin:
                _atom['spin1']._plot(fig, Orbit = _orbits[ind], _spinNo = True)
                _atom['spin2']._plot(fig, Orbit = _orbits[ind], _spinNo = True)
            else:
                _atom['spin1']._plot(fig, Orbit = _orbits[ind], _spinNo = False)

        
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
    
    def getbyType(self, _type='total', _spin = 'up'):
        _spin = 'spin1' if _spin == 'up' else 'spin2'
        if _spin not in self.__TOTAL_DOS.keys():
            raise Exception('也许没有自旋')

        if _type == 'total':
            return self.__TOTAL_DOS
        else:   
            _TYPES = []
            for i in self.__IONs_DATA:
                if i[_spin].getType() == _type:
                    _TYPES.append(i[_spin])
            return _TYPES
    def getbyIndex(self, _index, _spin = 'up'):
        _spin = 'spin1' if _spin == 'up' else 'spin2'

        if _spin not in self.__TOTAL_DOS.keys():
            raise Exception('也许没有自旋')
        
        return self.__IONs_DATA[_index][_spin]
    
    def test(self):
        return self.__IONs_DATA
    def test1(self):
        return self.__TOTAL_DOS
    
    