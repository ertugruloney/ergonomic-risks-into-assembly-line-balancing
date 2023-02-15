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
import numpy as np
import pandas as pd
class meta:
    def __init__(self,df,obj,J,I,C,frekans,force,Typeposture,t,names,sure,p):
        self.df=df
        self.J=J
        self.I=I
        self.obj=obj
        self.Typeposture=Typeposture
        self.frekans=frekans
        self.C=C
        self.force=force
        self.t=t
        self.sure=sure
        self.names=names
        self.p=p
    def Ocrahesaplama (self,):
        Ocraindeks=np.zeros([self.obj+1,6])#her istasyon için ocr değerlerinin tutulduğu liste
        Pm=[]
        Fom=[]
        Adm=1
        OS=18
        RM=1
        for i in self.df:
          
          #frekans hesapalam
          Ocraindeks[i[4]][0]+=int(self.frekans[i[1]])
          #posture hesaplama
          Ocraindeks[i[4]][3+int(self.Typeposture[i[1]])]+=self.t[i[1]]
          #force hesaplama
          Ocraindeks[i[4]][1]+=((self.t[i[1]]/self.C)*float(self.force[i[1]]))
        for i in range(len(Ocraindeks)):
            if sum(Ocraindeks[i,4:])==0:
                Pm.append(1)
            
            else:
                for count,j in enumerate(Ocraindeks[i,4:]):
                    rate=j/self.C
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
                fom=(0.2-0.01)*fom+0.01
            elif i[1]<0.4 and i[1]>=0.3:
                fom=(i[1]-0.3)*10
                fom=(0.35-0.2)*fom+0.2    
            elif i[1]<0.3 and i[1]>=0.2:
                fom=(i[1]-0.2)*10
                fom=(0.65-0.35)*fom+0.35      
            elif i[1]<0.2 and i[1]>=0.1:
                fom=(i[1]-0.1)*10
                fom=(0.85-0.65)*fom+0.65  
            elif i[1]<0.1 and i[1]>=0:
                fom=(i[1]-0.5)*10
                fom=(1-0.85)*fom+0.85  
           
                
            else:
                fom=1
            Fom.append(fom)
            
        OcraPuan=[]
        for i in range(int(self.obj)+1):
            ocra=Ocraindeks[i][0]/(OS*Pm[i]*Fom[i]*RM*Adm)
            OcraPuan.append(ocra)
        feasbile=True
        for i in OcraPuan:
            if i>3.2:
                feasbile=False
                break

        return feasbile,Fom,Pm,OcraPuan,Ocraindeks     

    


    def sureguncelleme(self,data):
                   
        data=pd.DataFrame(data,columns=['Task','Complete','Start','Finish','istasyon'])
        sure=np.zeros(self.J)

        data.sort_values(['istasyon'], inplace=True, ascending=True)
        data = data.values.tolist()
        
        for count, i in enumerate(data):
            data[count][2]=sure[i[4]]
            data[count][3]=data[count][2]+self.t[i[1]]
            sure[i[4]]+=self.t[i[1]]

        return data, sure
        
    def atamakontrol(self,SS,st):
        durum=True
        for i in range(self.I):
            if self.p[i][SS]==1:
                for j in  self.df:
                    if j[1]==i:
                        if j[4]>st:
                            durum=False
                            break
            if durum is False:
                break
        return durum
    def degisimyapma(self,SI,ST,SS,SS2):
        dfs=copy.deepcopy(self.df)
        a=copy.deepcopy(self.df)
        for count, i in enumerate(dfs):
           
            if i[1]==SS2:
                dfs[count][4]=SI
                dfs[count][0]=self.names[SI]
            if i[1]==SS:
                dfs[count][4]=ST
                dfs[count][0]=self.names[ST]   
        return dfs
    def atamakontrolsure(self,SI,ST,SS,SS2):
        dfchild=self.degisimyapma(SI,ST,SS,SS2)
        dfchild,sureR2=self.sureguncelleme(dfchild) 
        
         
        return dfchild,sureR2


    def komsucozum(self,OcraPuan,Pm,Fom,sayac,obj):
        SI=np.argmax(OcraPuan)  
        Ocrapuansort=np.array(OcraPuan)
        Ocrapuansort=np.argsort(Ocrapuansort)
        Ocrapuansort=np.flipud(Ocrapuansort)
        durum3=0
        if sayac!=50:
            if durum3==0:
                for SI in Ocrapuansort:
                        SI=int(SI)
            
                       
                
                        secilecekbilecekisler=[]
                        avaregas=[]
                       
                        for  i in self.df:
                            if i[4]==SI:
                               
                                if self.Typeposture[i[1]]!=0:
                                    secilecekbilecekisler.append(i)
                                    avaregas.append(self.t[i[1]])
                        adayisler= [x for _, x in sorted(zip(avaregas,secilecekbilecekisler ))]
                        adayisler.reverse()
                        
                        for SS in adayisler:
                            if durum3==0:
                                SS=SS[1]
                                Aistasyon=[]
                                AistasyonOcra=[]
                                for count,i in enumerate(OcraPuan):
                                    if count!=SI:
                                       durum2= self.atamakontrol(SS,count)
                                       if durum2 is True:
                                           Aistasyon.append(count)
                                           AistasyonOcra.append((self.sure[count]))
                                if len(Aistasyon)!=0:
                                    Aistasyonsort=[x for _, x in sorted(zip(  AistasyonOcra,  Aistasyon))]
                                  
                                    for ST in  Aistasyonsort:
                                        if durum3==0:
                                          
                                            secilecekbilecekisler2=[]
                                            avaregas2=[]
                                            Fomsi=[]
                                            for  i in self.df:
                                                if i[4]==ST:
                                                    secilecekbilecekisler2.append(i)
                                                    avaregas2.append(t[i[1]])
                                         
                                            adayisler2= [x[1] for _, x in sorted(zip(avaregas2,secilecekbilecekisler2 ))]
                                            adayisler2.reverse()
                                         
                                            for SS2 in adayisler2:
                                                if durum3==0:
                                                    durum2= self.atamakontrol(SS2,SI)
                                                    sureR3=self.sure[ST]+t[SS]

                                                    if durum2 is True and sureR3<=self.C:
                                                        durum3=1
                                                        for count, i in enumerate(self.df):
                                                            if i[1]==SS:
                                                                self.df[count][4]=ST
                                                                self.df[count][0]=self.names[ST]
             
                                                                                                  
                                                    if durum2 is True :
                                                        
                                                      casd=4
                                                      df2,sureR2=  self.atamakontrolsure(SI,ST,SS,SS2)
                                                      if max(sureR2)<=self.C:
                                                          durum3=1
                                                          self.df=df2
                                                          self.sureR=sureR2

                                    
                               

            
        if sayac==50:  
                      
            self.obj+=1
     
            SI=Ocrapuansort[0]

            secilecekbilecekisler=[]
            avaregas=[]
           
            for  i in self.df:
                if i[4]==SI:
                    secilecekbilecekisler.append(i)
                    avaregas.append(float(t[i[1]]))
            adayisler= [x for _, x in sorted(zip(avaregas,secilecekbilecekisler ))]
            adayisler.reverse()
             
            for count,i in enumerate(self.df):               
                if adayisler[0][1]==i[1]:
                  self.df[count][4]=self.obj
                  self.df[count][0]=self.names[self.obj]        
                           
        self.df,self.sure=self.sureguncelleme(self.df) 

   
io.renderers.default = 'browser'
f = open("Arc83_c=3786_iteration1.alb", "r")
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
model = gp.Model("Arc83_c=3786_iteration1.alb")
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

sure2=[]
for i in sure:
    sure2.append(int(i))
sure=sure2
obj=int(obj)
#%% ocr hesaplama
df = []


for i in range(I):

    df.append([ Station[i],  i,  start[i],
                   start[i]+t[i], station[i]])
       
df=pd.DataFrame(df,columns=['Task','Complete','Start','Finish','istasyon'])


df.sort_values('istasyon', inplace=True, ascending=True)
df = df.values.tolist()
def Ocrahesaplama (frekans,force,C,Typeposture,df,obj):

    
    Ocraindeks=np.zeros([obj+1,6])#her istasyon için ocr değerlerinin tutulduğu liste
    Pm=[]
    Fom=[]
    Adm=1
    OS=18
    RM=1
    for i in df:
      
      #frekans hesapalam
      Ocraindeks[i[4]][0]+=int(frekans[i[1]])
      #posture hesaplama
      Ocraindeks[i[4]][3+int(Typeposture[i[1]])]+=t[i[1]]
      #force hesaplama
      Ocraindeks[i[4]][1]+=((t[i[1]]/C)*float(force[i[1]]))
    for i in range(len(Ocraindeks)):
        if sum(Ocraindeks[i,4:])==0:
            Pm.append(1)
        
        else:
            for count,j in enumerate(Ocraindeks[i,4:]):
                rate=j/C
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
            fom=(0.2-0.01)*fom+0.01
        elif i[1]<0.4 and i[1]>=0.3:
            fom=(i[1]-0.3)*10
            fom=(0.35-0.2)*fom+0.2    
        elif i[1]<0.3 and i[1]>=0.2:
            fom=(i[1]-0.2)*10
            fom=(0.65-0.35)*fom+0.35      
        elif i[1]<0.2 and i[1]>=0.1:
            fom=(i[1]-0.1)*10
            fom=(0.85-0.65)*fom+0.65  
        elif i[1]<0.1 and i[1]>=0:
            fom=(i[1]-0.5)*10
            fom=(1-0.85)*fom+0.85  
       
            
        else:
            fom=1
        Fom.append(fom)
        
    OcraPuan=[]
    for i in range(int(obj)+1):
        ocra=Ocraindeks[i][0]/(OS*Pm[i]*Fom[i]*RM*Adm)
        OcraPuan.append(ocra)
    feasbile=True
    for i in OcraPuan:
        if i>3.2:
            feasbile=False
            break

    return feasbile,Fom,Pm,OcraPuan,Ocraindeks     

feasbile,Fom,Pm,OcraPuan,Ocraindeks     =Ocrahesaplama (frekans,force,C,Typeposture,df,obj)

if max(OcraPuan)<BestOcraPuan:
    BestOcraPuan=max(OcraPuan)
    Bestdf=df

count=0
Meta=meta(df,obj,J,I,C,frekans,force,Typeposture,t,names,sure,p)
while True:
    
    Meta.komsucozum(OcraPuan, Pm, Fom, count, obj)
    feasbile,Fomchild,Pmchild,OcraPuanchild,Ocraindekschild   =Meta.Ocrahesaplama()
    if max(OcraPuanchild)<max(OcraPuan):
        df=dfchild.copy()
        OcraPuan=OcraPuanchild
        Fom=Fomchild
        Pm=Pmchild
        Ocraindeks=Ocraindekschild
        sure=surchild
    else:
        r1=random.random()
        if r1<exp((max(OcraPuan)-max(OcraPuan))/T):
           df=dfchild
           OcraPuan=OcraPuanchild
           Fom=Fomchild
           Pm=Pmchild
           Ocraindeks=Ocraindekschild
           sure=surchild
    if max(OcraPuan)<BestOcraPuan:
        BestOcraPuan=max(OcraPuan)
        Bestdf=df
        BestSure=sure
        count=0
    print(max(OcraPuan),T)
    T=T*Cooling
    count+=1
    if count%50==0:
        feasbile,Fom,Pm,OcraPuan,Ocraindeks     =Ocrahesaplama (frekans,force,C,Typeposture,Bestdf,obj)
        if feasbile is True:
            
            break
    if T<0:
        break

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
