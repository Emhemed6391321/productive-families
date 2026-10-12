import pypdf, subprocess, numpy as np, sys
from PIL import Image
from pypdf.generic import NameObject
S="/tmp/claude-0/-home-user-productive-families/279b9344-f325-5676-997e-4eb1bcac3822/scratchpad/"
lines=open("x38.txt").read().split("\n")
def render_prefix(n):
    r=pypdf.PdfReader("source.pdf"); pg=r.pages[0]
    x=pg["/Resources"]["/XObject"]["/X38"].get_object()
    x.set_data(("\n".join(lines[:n])+"\n").encode("latin1"))
    w=pypdf.PdfWriter(); w.add_page(pg); w.write(S+"probe.pdf")
    subprocess.run(["pdftoppm","-r","150","-x","650","-y","1660","-W","350","-H","90","-png","-singlefile",S+"probe.pdf",S+"probe"],stderr=subprocess.DEVNULL)
    a=np.asarray(Image.open(S+"probe.png").convert("L")).astype(int)
    return (a>235).sum()      # bright (white text) pixels in the gold bar area
for n in (0,100,4300,5400,5710,6100,6200,len(lines)):
    print(n, render_prefix(n))
