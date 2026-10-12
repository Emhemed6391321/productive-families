from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
S=8
c=Image.open('img/i-001.png').convert('RGB')
BG=(180,133,46)
def region(c,x0,x1,text,rightx):
    a=np.array(c)
    a[1043:1067,x0:x1]=BG
    c2=Image.fromarray(a)
    size=14.8*1.0
    P='/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
    f0=ImageFont.truetype(P,100);cap=f0.getbbox('0')[3]-f0.getbbox('0')[1]
    f=ImageFont.truetype(P,int(100*12.2/cap*S))
    W=(x1-x0)*S;H=24*S
    m=Image.new('L',(W,H),0);d=ImageDraw.Draw(m)
    # right-aligned at rightx, baseline at y=1060
    d.text(((rightx-x0)*S,(1060.4-1043)*S),text,font=f,fill=255,anchor='rs')
    m=m.resize((x1-x0,24),Image.LANCZOS)
    layer=Image.new('RGB',m.size,(255,255,255))
    c2.paste(layer,(x0,1043),m)
    return c2
c=region(c,386,428,'1448',424)
c=region(c,489,531,'2027',527.8)
c.save('img/i-001_new.png')
c.crop((300,1030,600,1075)).resize((1200,180),Image.LANCZOS).save('foot_new_zoom.png')
Image.open('img/i-001.png').crop((300,1030,600,1075)).resize((1200,180),Image.LANCZOS).save('foot_old_zoom.png')
