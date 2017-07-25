from __future__ import division
from lxml import etree
from math import ceil

def make_image(Q,A,height=200, width=300):
    def to_lines(s,maxlen=20):
        lineno  = int(ceil(len(s)/maxlen))
        linelen = int(ceil(len(s)/lineno))
        def split(lines,word):
            if len(lines)==0 or len(lines[-1])+len(word)+1 > linelen:
                return lines+[word]
            else:
                lines[-1] = lines[-1]+" "+word
                return lines

        return reduce(split, s.split(),[] )

    def text(s,x=None,y=None,color=None,maxlen=20,align="start"):
        s= s.upper()
        tspans=[etree.fromstring('<tspan x="0" dy="25">'+l+"</tspan>") for l in to_lines(s,maxlen=maxlen)]
        txt= etree.fromstring("""
        <text
           style="font-style:normal;font-weight:normal;font-size:25px;line-height:125%;font-family:Sans;text-align:{align};letter-spacing:0px;word-spacing:0px;text-anchor:{align};fill:#{color};fill-opacity:1;stroke:none;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
           transform="translate({x})" y="{y}">
        </text>""".format(x=x,y=y,color=color,align=align))
        for ts in tspans: txt.append(ts)
        return txt

    def question(s): return text(s,x=30 , y=30 , color="FFFFFF", align="start")
    def answer  (s): return text(s,x=350, y=150, color="000000", align="end"  )

    tree = etree.parse(open("./Plantila.svg",'r'))
    tree.getroot().append(question(Q))
    tree.getroot().append(answer(A))
    tree.getroot().attrib["height"]= str(height)
    tree.getroot().attrib["width" ]= str(width)
    return tree

def line_filter(lines): return [l for l in lines if l and not l.isspace()]
    
class chapter():
    def __init__(self, text):
        lines = list(text.split("\n"))
        lines = line_filter(lines)
        self.title          = lines[ 0].strip()
        self.summary        = lines[ 1].strip()
        self.body           = '\n'.join([l.strip() for l in lines[2:-2]])
        self.image_question = lines[-2].strip() 
        self.image_answer   = lines[-1].strip()
                
class book():
    def __init__(self,text):
        chapters_text = line_filter(text.split("#"))
        self.chapters = [chapter(c)     for c in chapters_text]
        self.index_format   ="<p><b>{}- {}</b></p>"
    def make_chapter(self,n, c):
        return """ <p><h2> {n}- {title}   </h2></p>
                   <p><i>       {summary} </i></p>
                   <p>          {body}    </p>""".format(n=n,**c.__dict__)+\
        etree.tostring(make_image(  c.__dict__["image_question"],
                                    c.__dict__["image_answer"]))
        
    def _repr_html_(self):
        index= "<p><h2>Indice</h2></p>\n"+\
        "\n".join([self.index_format.format(i+1,c.title) for i,c in enumerate(self.chapters)])
        return "\n".join([index]+[self.make_chapter(i+1,c) for i,c in enumerate(self.chapters)])

if __name__ == "__main__":
    with open("./respuestas.md") as f:
        html=book(f.read())._repr_html_()
    with open("./output.html","w") as f:
        f.write(html)