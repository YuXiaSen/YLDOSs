```
import YLDOSs as YLs

#  提供vasprun.xml路径文件
a = YLs.YLDOSs('vasprun.xml')

# _atoms  数字数组，默认None，即画出总DOS 
# _atoms = [1,2,4]  即绘制第1,2,4个原子的DOS
# _orbits 轨道  默认None，即 画出['s','p','d','f','total']轨道DOS
# 如果_atoms = [1,2,4,'total'],_orbits = [ ['s','p'], ['s'], ['p','d'], ['s','p','d','f','total'] ]
# 为画出第1个原子的s,p
# 第2个原子的s
# 第4个原子的p,d
# 总DOS的s,p,d,f,total
# 返回一个plotly.graph_objects.Figure()对象
fig = a.pplot(_atoms=[1,15],_orbits=[['s','p'],['s','p'])
# 设置x轴范围  0--5
fig.update_xaxes(range=[0,5])
# 设置y轴范围  0--20
fig.update_yaxes(range=[0,20])
# 显示
fig.show()
```
