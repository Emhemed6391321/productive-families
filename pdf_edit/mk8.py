import math
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
def ring(pen,cx,cy,ox,oy,ix,iy,n=16):
    for rx,ry,cw in ((ox,oy,True),(ix,iy,False)):
        R=1/math.cos(math.pi/n); pts=[]
        for k in range(n):
            a=(-1 if cw else 1)*(k*2*math.pi/n)
            pts.append((round(cx+rx*R*math.cos(a)),round(cy+ry*R*math.sin(a))))
        pen.qCurveTo(*pts,None); pen.closePath()
t=TTFont('F13.ttf'); gs=t.getGlyphSet()
pen=TTGlyphPen(gs)
cx=375
ring(pen,cx,272,318,280,232,210)           # bottom loop
ring(pen,cx,656,270,172,188,104)            # top loop
eight=pen.glyph()
order=t.getGlyphOrder()
t['glyf'].glyphs['eight']=eight; t['glyf'].glyphOrder=order+['eight']; t.glyphOrder=order+['eight']
t['hmtx'].metrics['eight']=(746,50)
for tb in t['cmap'].tables: tb.cmap[56]='eight'
t['post'].formatType=3.0
t.save('F13_8.ttf')
from PIL import Image,ImageDraw,ImageFont
f=ImageFont.truetype('F13_8.ttf',300)
im=Image.new('L',(1800,400),255);ImageDraw.Draw(im).text((10,10),'0 2 6 8 7 1448',font=f,fill=0);im.save('t8.png')
