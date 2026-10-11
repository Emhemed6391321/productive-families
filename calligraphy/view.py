import sys; sys.path.insert(0,"/home/user/productive-families/brand_kit")
import render, build
S="/tmp/claude-0/-home-user-productive-families/279b9344-f325-5676-997e-4eb1bcac3822/scratchpad/"
def go(name="cal"):
    P=build.compose(); s=build.svg(P)
    open("tansiqiya-calligraphy.svg","w",encoding="utf-8").write(s)
    open(S+name+".html","w").write('<body style="margin:0;background:#fff">'+s.replace('<svg ','<svg style="width:1200px;display:block" ')+'</body>')
    render.to_png(S+name+".html",S+name+".png",1200,900)
if __name__=="__main__": go()
