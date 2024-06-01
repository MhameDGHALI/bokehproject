
import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show,curdoc
from bokeh.plotting import figure,output_file,show
from bokeh.models import ColumnDataSource,Select,Slider,LabelSet,NumeralTickFormatter,HoverTool,Div
from bokeh.layouts import gridplot,column,row
from bokeh.transform import dodge,cumsum
from bokeh.core.properties import value
from bokeh.palettes import Spectral6,Category20c


from math import pi


###################################################

#premiere visualisation
data=pd.read_excel('C:/Users/a/Desktop/projet bokeh 2/2023-tourisme-PF (2).xlsx')

data.columns=['Type','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','Var 23/22','Part 2023']
data=data.dropna(subset=['Type'])

#on precise les postes frontiers
pfrontiers=['T.AIR','T.MER','T.TERRE']
filteree=data[data['Type'].isin(pfrontiers)]

filteree=filteree.melt(id_vars='Type',value_vars=[str(year) for year in range(2012, 2024)],var_name='Year',value_name='Visitors')

pivot_data1=filteree.pivot(index='Year',columns='Type',values='Visitors').fillna(0)
pivot_data1=pivot_data1[pfrontiers]
pivot_data1=pivot_data1.reset_index()

#on prepare la source
source1=ColumnDataSource(pivot_data1)

colors=["#002f58","#005197","#0083f4"]

#creation de la figure
p1=figure(x_range=pivot_data1['Year'].tolist(),title="Nombre de Visiteurs par Année et Postes Frontieres",toolbar_location=None,tools="")


types=pfrontiers
p1.vbar_stack(stackers=types,x='Year',width=0.9,color=colors,source=source1,legend_label=types)

# design
p1.y_range.start=0
p1.x_range.range_padding=0.1
p1.legend.location="top_left"
p1.yaxis.formatter=NumeralTickFormatter(format="0,0")
p1.legend.orientation="horizontal"
p1.title.align="center"
p1.title.text_font_size='17pt'


#affichage 
layout1=column(p1)
curdoc().add_root(layout1)



#################################################

#deuxieme visualisation

data2=pd.read_excel('C:/Users/a/Desktop/projet bokeh 2/evolution_nationalite_nuitees (1).xlsx')

data2.columns=['Nationality','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','Var 23/22','Part 2023']
data2=data2.dropna(subset=['Nationality'])

# on precise les colonnes qu on veut
years=[str(year) for year in range(2012, 2024)]
data2= data2[['Nationality']+years]
data2.set_index('Nationality',inplace=True)

data2=data2[~data2.index.isin(['Touristes Etrangers','T.Recepteur'])]
#fonc pour la sourc
def create_source(year):
    df=data2[[year]].reset_index()
    df.columns=['Nationality','Value']
    df['Percentage']=df['Value']/df['Value'].sum()*100
    df['Angle']=df['Value']/df['Value'].sum()*2*pi
    df['Color']=Category20c[len(df)]
    return ColumnDataSource(df)

#la source
source2=create_source('2012')

#creation de la figure
p2=figure(title="Répartition des arrivées des touristes par nationalité",toolbar_location=None,
           tools="hover",tooltips="@Nationality: @Value(@Percentage{0.2f}% )",x_range=(-0.5,1.0))


p2.wedge(x=0,y=1,radius=0.4,
        start_angle=cumsum('Angle',include_zero=True),end_angle=cumsum('Angle'),
        line_color="white",fill_color='Color',legend_field='Nationality',source=source2)

p2.axis.axis_label=None
p2.axis.visible=False
p2.grid.grid_line_color=None
p2.title.text_font_size="14pt"
p2.title.align="center"
#creation du selecteur
year_select2=Select(title="Year",value='2012',options=years)
#fonc de mis a jour
def update_plot(attr,old,new):
    new_source=create_source(year_select2.value)
   
    source2.data.update(new_source.data)

year_select2.on_change('value',update_plot)

#affichage
layout2=column(year_select2,p2)
curdoc().add_root(layout2)

############################################

#troisieme visualisation
file_path3='C:/Users/a/Desktop/projet bokeh 2/2023-tourisme-destination (2).xlsx'
data3=pd.read_excel(file_path3)
#on renomme la premiere colonne
data3.rename(columns={data3.columns[0]:'City'},inplace=True)
data_3=data3.drop(columns=[data3.columns[-2],data3.columns[-1]])
# verfication du format
data_3.columns=['City']+[str(col) for col in data_3.columns[1:]]
data_3.set_index('City',inplace=True)
#on la transforme en une liste
cities=data_3.index.tolist()

#on prepare la data
initial_city=cities[0]
source3=ColumnDataSource(data={
    'year': data_3.columns.tolist(),
    'visitors': data_3.loc[initial_city].values
})
#creation du graph
p3=figure(x_range=data_3.columns.tolist(),title="Nombre de visiteurs par année",toolbar_location=None,tools="")

p3.vbar(x='year',top='visitors',width=0.9,source=source3)

p3.y_range.start=0
p3.xaxis.axis_label="Année"
p3.yaxis.axis_label="Nombre de visiteurs"
p3.yaxis.formatter=NumeralTickFormatter(format="0,0")
p3.title.text_align="center"
p3.title.text_font_size="17pt"
#creation du select
city_select3=Select(title="City",value=initial_city,options=cities,width=200)

#la fonc du mis a jour
def update_plot(attr,old,new):
    selected_city=city_select3.value
    new_data={
        'year':data_3.columns.tolist(),
        'visitors':data_3.loc[selected_city].values
    }
    source3.data=new_data

city_select3.on_change('value',update_plot)

# affichage
layout3=column(city_select3,p3)
curdoc().add_root(layout3)

##################################################"

#derniere visualisation
file_path4='C:/Users/a/Desktop/guideavecville.xlsx'
data4=pd.read_excel(file_path4)
#fonct pour la mis a jour 
def update_plot(attr, old, new):
    ville4=select4.value
    ville_data=data4[data4['Ville']==ville4].iloc[0]
    total_guides=ville_data['Nombre de guides']
    langues=ville_data.index[2:].tolist()
    nombres=ville_data[2:].values
    
    #filtrer la data 
    langues_filtrees=[langue for langue, nombre in zip(langues, nombres) if nombre > 0]
    nombres_filtres=[nombre for nombre in nombres if nombre > 0]
    langues_triees=[x for _, x in sorted(zip(nombres_filtres, langues_filtrees))]
    nombres_tries=sorted(nombres_filtres)
    
    source4.data={
        'langues':langues_triees,
        'nombres':nombres_tries
    }
    p4.y_range.factors=langues_triees
    p4.title.text=f'Langues des guides pour la ville de {ville4}'
    total_guides_div.text=f"<b>Total de guides : {total_guides}</b>"

ville_initiale=data4['Ville'].iloc[0]
ville_data=data4[data4['Ville']==ville_initiale].iloc[0]
total_guides_initial=ville_data['Nombre de guides']

langues=ville_data.index[2:].tolist()
nombres=ville_data[2:].values

langues_filtrees=[langue for langue,nombre in zip(langues,nombres) if nombre>0]
nombres_filtres=[nombre for nombre in nombres if nombre>0]
langues_triees=[x for _,x in sorted(zip(nombres_filtres,langues_filtrees))]
nombres_tries=sorted(nombres_filtres)
    

source4=ColumnDataSource(data={
         'langues':langues_triees,
    'nombres':nombres_tries
})

#creation du graph
p4=figure(y_range=langues_triees,title=f'Langues des guides pour la ville de {ville_initiale}',
           x_axis_label='Nombre de guides parlant cette langue',y_axis_label='Langues',tools="pan,box_zoom,reset")

p4.hbar(y='langues',right='nombres',height=0.4,source=source4,color='navy')

#le select
select4=Select(title="Sélectionner la ville",value=ville_initiale,options=list(data4['Ville']))
select4.on_change('value',update_plot)

#le total des guides
total_guides_div=Div(text=f"<b>Total de guides : {total_guides_initial}</b>",stylesheets=['.bokeh div{font-size:17px;color:black;}'])

#affichage du graph
layout4=column(select4,total_guides_div,p4)
curdoc().add_root(layout4)
