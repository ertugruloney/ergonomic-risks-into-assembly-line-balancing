import matplotlib.pyplot as plot
from math import *
import pandas as pd
from gurobipy import GRB
import gurobipy as gp
import numpy as np
import copy
import re
import plotly.figure_factory as ff
import plotly.io as io
import random
io.renderers.default = 'browser'
f = open("Arc83_c=3786_iteration10.alb", "r")
text = f.read()
numberoftask = int(text[18:20])
cycle = int(text[35:39])
t = np.zeros(numberoftask)
times = text[54:]
indekst = times.index("<")
times = times[:indekst-2]
times = times.split(" ")
BestOcraPuan=100000
T = Ti = 1000 # Baslangic sicakligi
Cooling=0.999

for i in range(numberoftask):
    lenn = len(times[i+1].split(" "))
    a = times[i+1][:lenn-3]
    t[i] = int(a)
oncul = text[77+indekst:]
p = np.zeros([numberoftask, numberoftask])
indekso = oncul.index("<")
oncul = oncul[:indekso-2]
oncul = oncul.split()



lenn = len(oncul)
oncullukler = []

count = 0
for i in oncul:
    indeks = i.index(",")
    x = int(i[:indeks])-1
    y = int(i[indeks+1:])-1
    p[x][y] = 1
pindeks = []
for i in range(numberoftask):
    for k in range(numberoftask):
        if p[i][k] == 1:
            pindeks.append((i, k))
# average forceleri sistemden çekme
force = text[93+indekst+indekso:]
indeksfo = force.index("<")
force = force[:indeksfo-2]
force = force.split()


# frekannları veriden çekme
frekans = text[111+indekst+indekso+indeksfo:]
indeksfe = frekans.index("<")
frekans = frekans[:indeksfe-2]
frekans = frekans.split()

# several posture

several = text[157+indekst+indekso+indeksfo+indeksfe :]
indeksse = several.index("<")
several= several[:indeksse-2]
several=several.split()
Several=[]
sseveral=[]
count=1
for i in several:
    if len(i)!=1:
        sseveral.append(float(i))
    else:
        sseveral.append(0)
    if count%3==0:
        Several.append(sseveral)
        sseveral=[]
    count+=1

# Mild posture

mild = text[198+indekst+indekso+indeksfo+indeksfe+indeksse :]
indeksmi = mild.index("<")
mild= mild[:indeksmi-2]
mild=mild.split()
Mild=[]
mmild=[]
count=1
for i in mild:
    mmild.append(i)
    
    if count%3==0:
        Mild.append(mmild)
        mmild=[]
    count+=1
# Additionalfactor 
adm=text[218+indekst+indekso+indeksfo+indeksfe+indeksse+indeksmi :]
indeksad = adm.index("<")
adm= adm[:indeksad-2]
adm=adm.split()

Typeposture=np.zeros([len(Mild)])

for count, i in enumerate(Several):
    buyuk=0
    durum=0
    for j in i :
        if float(j)>buyuk:
            durum=1
            buyuk=float(j)
        for k in Mild[count]:
            if float(k)>buyuk:
                durum=2
                buyuk=float(k)
    Typeposture[count]=durum

Kmin = ceil(sum(t)/cycle)
J = int(Kmin*1.5)
I = numberoftask
C = cycle
YellowOcra = 3.5
bigm=100000000
model = gp.Model("Arc83_c=3786_iteration8.alb")
OS = 18
FOMindeks=[]


# %% model kurma

x = model.addVars(I, J, name="x", lb=0, vtype="B")
z = model.addVars(J, name="z", lb=0, vtype="B")
Mmax = model.addVar(name="Mmax", lb=0, vtype="I")


constraint1 = model.addConstrs(gp.quicksum(x[i, j]*t[i] for i in range(I)) <= C
                               for j in range(J)
                               )





constraint3 = model.addConstrs(gp.quicksum(j*x[i, j] for j in range(J))<=gp.quicksum(j*x[k, j] for j in range(J))
                               for i, k in pindeks)

constraint4 = model.addConstrs(x.sum(i, "*") == 1 for i in range(I))

constraint5 = model.addConstrs(x.sum("*", j) <= bigm*z[j] for j in range(J))

constrint6 = model.addConstrs(z[j]*j <= Mmax for j in range(J))


model.setObjective(Mmax, GRB.MINIMIZE)
model.write("project.lp")
model.optimize()

result = []
for v in model.getVars():
    result.append('%s %g' % (v.VarName, v.X))

obj = model.objVal


ct = []
Station = []
task = []
names = ['Station %s' % s for s in range(J)]
sure = np.zeros(J)
start = np.zeros(I)
station = []
for i in range(I):
    for j in range(J):
        if x[i, j].X == 1:
            Station.append(names[j])
            start[i] = sure[j]
            sure[j] += t[i]
            station.append(j)
            break

sure2222=[]
for i in sure:
    sure2222.append(int(i))
sure=sure2222.copy()
obj=int(obj)
#%% ocr hesaplama
df = []


for i in range(I):

    df.append([ Station[i],  i,  start[i],
                   start[i]+t[i], station[i]])
       
df=pd.DataFrame(df,columns=['Task','Complete','Start','Finish','istasyon'])


df.sort_values('istasyon', inplace=True, ascending=True)
dfxx = df.values.tolist()
def Ocrahesaplama (frekans,force,C,Typeposture,ddfchild,ddataobj):
    
    
    Ocraindeks=np.zeros([ddataobj+1,6])#her istasyon için ocr değerlerinin tutulduğu liste
    Pm=[]
    Fom=[]
    Adm=1
    OS=18
    RM=1
    for i in ddfchild:
      
      #frekans hesapalam
      try:
          Ocraindeks[i[4]][0]+=int(frekans[i[1]])
      except:
          ssdasda=5
      #posture hesaplama
      try:
          Ocraindeks[i[4]][3+int(Typeposture[i[1]])]+=t[i[1]]
      except:
          
          dsada=3
      #force hesaplama
      try:
          Ocraindeks[i[4]][1]+=((t[i[1]]/C)*float(force[i[1]]))
      except:
          asda=2
    for i in range(len(Ocraindeks)):
        if sum(Ocraindeks[i,4:])==0:
            Pm.append(1)
        
        else:
            for count,j in enumerate(Ocraindeks[i,4:]):
                rate=j/cycle
                if rate<=1/4:
                    RRm=1
                    RRm1=1
                elif count==0 and rate>1/4 and rate<=1/3:
                    RRm=0.95
                elif count==1 and rate>1/4 and rate<=1/3:
                    RRm1=1          
                elif count==0 and rate>1/3 and rate<=1/2:
                    RRm=0.925
                elif count==1 and rate>1/3 and rate<=1/2:
                    RRm1=1            
                elif count==0 and rate>1/2 and rate<=2/3:
                    RRm=0.9
                elif count==1 and rate>1/2 and rate<=2/3:
                    RRm1=0.7
                elif count==0 and rate>2/3:
                    RRm=0.8  
                elif count==1 and rate>2/3 :
                    RRm1=0.6    
            if RRm1>=RRm:
              Pm.append(RRm)
            else:
                Pm.append(RRm1)
        i=Ocraindeks[i,:]
        if  i[1]>=0.5:
            Fom.append(0.01)
        elif i[1]<0.5 and i[1]>=0.4:
            fom=(i[1]-0.4)*10
            fom=((0.2-0.01)/10)*fom+0.01
        elif i[1]<0.4 and i[1]>=0.3:
            fom=(i[1]-0.3)*10
            fom=((0.35-0.2)/10)*fom+0.2    
        elif i[1]<0.3 and i[1]>=0.2:
            fom=(i[1]-0.2)*10
            fom=((0.65-0.35)/10)*fom+0.35      
        elif i[1]<0.2 and i[1]>=0.1:
            fom=(i[1]-0.1)*10
            fom=((0.85-0.65)/10)*fom+0.65  
        elif i[1]<0.1 and i[1]>=0.05:
            fom=(i[1]-0.05)*10
            fom=0.015*fom+0.85  
       
            
        else:
            fom=1
        Fom.append(fom)
        
    OcraPuan=[]
    for i in range(int(obj)+1):
        ocra=Ocraindeks[i][0]/(OS*Pm[i]*Fom[i]*RM*Adm)
        OcraPuan.append(ocra)
    feasbile=True
    for i in OcraPuan:
        if i>3.5:
            feasbile=False
            break

    return feasbile,Fom,Pm,OcraPuan,Ocraindeks     

feasbile,Fom,Pm,OcraPuan,Ocraindeks     =Ocrahesaplama (frekans=frekans,force=force,C=C,Typeposture=Typeposture,ddfchild=dfxx,ddataobj=obj)

if max(OcraPuan)<BestOcraPuan:
    BestOcraPuan=max(OcraPuan)
    Bestdf=copy.deepcopy(df)
    BestSure=copy.deepcopy(sure)
    BestOcra=copy.deepcopy(OcraPuan)
    BestObj=copy.deepcopy(obj)

def sureguncelleme(sdataorgin,t,J):
    datas=copy.deepcopy(sdataorgin)
    datas=pd.DataFrame(datas   ,columns=['Task','Complete','Start','Finish','istasyon'])
   
  
    sdatasure=np.zeros(J)
    datas.sort_values(['istasyon'], inplace=True, ascending=True)
    datas = datas.values.tolist()
    try:
        for count, i in enumerate(datas):
            datas[count][2]=sdatasure[i[4]]
            datas[count][3]=datas[count][2]+t[i[1]]
            sdatasure[i[4]]+=t[i[1]]
            
    except:
        adasd=4

    return datas, sdatasure
    
def atamakontrol(SS,p,st,I,dataorgin):
    durum=True
    for i in range(I):
        if p[i][SS]==1:
            for j in  dataorgin:
                if j[1]==i:
                    if j[4]>st:
                        durum=False
                        break
        if durum is False:
            break
    return durum
def degisimyapma(dataorgin,SI,ST,SS,SS2):
    dfs=copy.deepcopy(dataorgin)
    for count, i in enumerate(dfs):
       
        if i[1]==SS2:
            dfs[count][4]=SI
            dfs[count][0]=names[SI]
        if i[1]==SS:
            dfs[count][4]=ST
            dfs[count][0]=names[ST]   
    return dfs
def atamakontrolsure(SI,ST,SS,SS2,dataorgin,C,t,J):
    dfchild=degisimyapma(dataorgin=dataorgin,SI=SI,ST=ST,SS=SS,SS2=SS2)
    sureR2=0
    
    dfchild,sureR2=sureguncelleme(sdataorgin=dfchild,t=t,J=J) 
    
     
    return dfchild,sureR2


def komsucozum(kkdataorgin,dddataocrapuan,Pm,Fom,t,p,I,kkdatasure,sayac,kkdataobj):
    kdataorgin=copy.deepcopy(kkdataorgin)
    ddataocrapuan=copy.deepcopy(dddataocrapuan)
    kdatasure=copy.deepcopy(kkdatasure)
    kdataobj=copy.deepcopy(kkdataobj)
    Ocrapuansort=np.array(ddataocrapuan)
    Ocrapuansort=np.argsort(Ocrapuansort)
    Ocrapuansort=np.flipud(Ocrapuansort)
    durum3=0
    
    objVall=kdataobj+0 
    if sayac%50!=0 or sayac==0:
        if durum3==0:
            for SI in Ocrapuansort:
                    SI=int(SI)
        
                   
            
                    secilecekbilecekisler=[]
                    avaregas=[]
                    Fomsi=[]
                    for  i in kdataorgin:
                        if i[4]==SI:
                           
                            if Typeposture[i[1]]!=0:
                                secilecekbilecekisler.append(i)
                                avaregas.append(float(force[i[1]])*t[i[1]])
                    adayisler= [x for _, x in sorted(zip(avaregas,secilecekbilecekisler ))]
                    adayisler.reverse()
                    
                    for SS in adayisler:
                        if durum3==0:
                            SS=SS[1]
                            Aistasyon=[]
                            AistasyonOcra=[]
                            for count,i in enumerate(ddataocrapuan):
                                if count!=SI:
                                   durum2= atamakontrol(SS,p,count,I,kdataorgin)
                                   if durum2 is True:
                                       Aistasyon.append(count)
                                       AistasyonOcra.append((kdatasure[count]))
                            if len(Aistasyon)!=0:
                                Aistasyonsort=[x for _, x in sorted(zip(  AistasyonOcra,  Aistasyon))]
                              
                                for ST in  Aistasyonsort:
                                    if durum3==0:
                                      
                                        secilecekbilecekisler2=[]
                                        avaregas2=[]
                                        
                                        for  i in dataorgin:
                                            if i[4]==ST:
                                                secilecekbilecekisler2.append(i)
                                                avaregas2.append(float(force[i[1]])*t[i[1]])
                                     
                                        adayisler2= [x[1] for _, x in sorted(zip(avaregas2,secilecekbilecekisler2 ))]
                                        adayisler2.reverse()
                                     
                                        for SS2 in adayisler2:
                                            if durum3==0:
                                                durum2= atamakontrol(SS2,p,SI,I,kdataorgin)
                                           
                                                if durum2 is True and kdatasure[ST]+t[SS]<=cycle:
                                                    durum3=1
                                                    for count, i in enumerate(kdataorgin):
                                                        if i[1]==SS:
                                                            kdataorgin[count][4]=ST
                                                            kdataorgin[count][0]=names[ST]
         
                                                                                              
                                                if durum2 is True :
                                                    
                                                  casd=4
                                                  sureR2=0
                                                  df2,sureR2=  atamakontrolsure(SI=SI,ST=ST,SS=SS,SS2=SS2,dataorgin=kdataorgin,C=cycle,t=t,J=J)
                                                  if max(sureR2)<=cycle:
                                                      durum3=1
                                                      kdataorgin=copy.deepcopy(df2)
                                                      kdatasure=copy.deepcopy(sureR2)

                                
                           

   
    if sayac%50==0 and sayac!=0:  
                  
        objVall=kdataobj+1
        
        

        secilecekbilecekisler=[]
        avaregas=[]
        durum3=0
        for SI in Ocrapuansort:
            if durum3==0:
                for  i in kdataorgin:
                    if i[4]==SI:
                        secilecekbilecekisler.append(i)
                        avaregas.append(float(force[i[1]])*t[i[1]])
                adayisler= [x for _, x in sorted(zip(avaregas,secilecekbilecekisler ))]
                adayisler.reverse()
                
                for count,i in enumerate(kdataorgin):    
                    if durum3==0:
                        for j in  adayisler:
                         if   durum3==0:
                              if j[1]==i[1]:
                                  durum2= atamakontrol(j[1],p,kdataobj,I,kdataorgin)
                                  if durum2==1:
                                      durum3=1
                                      kdataorgin[count][4]=objVall
                                      kdataorgin[count][0]=names[objVall]        
                                      break
                           
    kdataorgin,kdatasure=sureguncelleme(sdataorgin=kdataorgin,t=t,J=J) 

    return kdataorgin,kdatasure,objVall





count=0
while True:
    
    dataorgin=copy.deepcopy(dfxx)
   
    datasure=copy.deepcopy(sure)
    dataocrapuan=copy.deepcopy(OcraPuan)
    dataobj=copy.deepcopy(obj)
    dfchild=[]
    surechild=[]
    obchild=0
    dfchild,surechild,objchild=komsucozum(kkdataorgin=dataorgin,dddataocrapuan=dataocrapuan,Pm=Pm,Fom=Fom,t=t,p=p,I=I,kkdatasure=datasure,sayac=count,kkdataobj=dataobj)
    feasbile,Fomchild,Pmchild,OcraPuanchild,Ocraindekschild   =Ocrahesaplama (frekans=frekans,force=force,C=cycle,Typeposture=Typeposture,ddfchild=dfchild,ddataobj=objchild)
    if max(OcraPuanchild)<max(OcraPuan):
        dfxx=copy.deepcopy(dfchild)
        OcraPuan=copy.deepcopy(OcraPuanchild)
        Fom=copy.deepcopy(Fomchild)
        Pm=copy.deepcopy(Pmchild)
        obj=copy.deepcopy(objchild)
        Ocraindeks=copy.deepcopy(Ocraindekschild)
        sure=copy.deepcopy(surechild)
    else:
        r1=random.random()
        if r1<exp((max(OcraPuan)-max(OcraPuanchild))/T):
           dfxx=copy.deepcopy(dfchild)
           OcraPuan=copy.deepcopy(OcraPuanchild)
           Fom=copy.deepcopy(Fomchild)
           Pm=copy.deepcopy(Pmchild)
           obj=copy.deepcopy(objchild)
           Ocraindeks=copy.deepcopy(Ocraindekschild)
           sure=copy.deepcopy(surechild)
    if max(OcraPuan)<BestOcraPuan:
        BestOcraPuan=max(OcraPuan)
        Bestdf=copy.deepcopy(dfxx)
        BestSure=copy.deepcopy(sure)
        BestOcra=copy.deepcopy(OcraPuan)
        BestObj=copy.deepcopy(obj)
   
    T=T*Cooling
    print(BestOcraPuan,T,obj)   
    count+=1
    if count%50==0:
       
        feasbile,Fom,Pm,OcraPuan,Ocraindeks     =Ocrahesaplama (frekans=frekans,force=force,C=cycle,Typeposture=Typeposture,ddfchild=Bestdf,ddataobj= BestObj)
        if feasbile is True:
         
            break
    if T<0 or obj==J-1:
        break

#%% görseleştirme
df=Bestdf


fig, ax = plot.subplots()
xranges = []
yrange = (0, 1)
count2 = 0
istasyonguncel = 0
for count, i in enumerate(df):
    if i[4] == istasyonguncel:
        xranges.append((int(i[2]), int(t[i[1]])))

    else:
        yrange = (yrange[0]+5, 2)
        ax.broken_barh(xranges, yrange, facecolors=(
            'tab:orange', 'tab:green', 'tab:red', 'tab:blue'), hatch='//')
        xranges = []
        xranges.append((int(i[2]), int(t[i[1]])))
        istasyonguncel = i[4]


# Give x axis label for the broken horizontal bar chart
ax.broken_barh(xranges, yrange, facecolors=(
    'tab:orange', 'tab:green', 'tab:red', 'tab:blue'), hatch='//')
plot.xlabel('İşler')


# Give y axis label for for the broken horizontal bar chart

plot.ylabel('İstasyonlar')


plot.show()

name="Arc83_c=3786_iteration10.xlsx"
df=pd.DataFrame(df,columns=['Task','Complete','Start','Finish','istasyon'])


df.sort_values('istasyon', inplace=True, ascending=True)
ocrapuan=pd.DataFrame(BestOcra,columns=['Ocra Indeksi'])
result=pd.concat([df,ocrapuan],axis=1)
result.to_excel(name)
