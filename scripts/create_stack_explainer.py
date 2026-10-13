"""A non-character script: explain a stack with an animated data-structure diagram."""
import argparse
from animation_kit.authoring import *

PROMPT="Explain a stack: push A, push B, then pop B to demonstrate last-in, first-out."


def make_story():
    s=story(PROMPT,[("push_a","Show A being pushed onto an empty stack."),
                   ("push_b","Show B above A after a second push."),
                   ("pop_b","Show B leaving first while A remains, demonstrating LIFO.")],title="Last in. First out.")
    s["frames"]=192
    s["assets"]=[]
    def block(ident,label,color,x,y):
        return group(ident,rect(ident+"_box",154,68,color,x=-77,y=-34,radius=12),
                     text(ident+"_label",label,0,0,38,"#FFFFFF",font="display"),x=x,y=y)
    s["shots"]=[shot("stack",0,192,"Two blocks enter a stack; the most recently pushed block exits first.","#F5F0E5",
        text("title","LAST IN. FIRST OUT.",480,54,44,"#243D58",font="display"),
        text("subtitle","A stack remembers order.",480,101,24,"#243D58"),
        path("stack_outline",[("M",386,192),("L",386,437),("L",574,437),("L",574,192)],stroke="#243D58",stroke_width=7),
        text("stack_label","STACK",480,468,23,"#243D58",font="display"),
        text("input","PUSH",145,173,27,"#327E7E",font="display"),
        text("output","POP",803,173,27,"#D66651",font="display"),
        block("a","A","#327E7E",track((0,145),(14,145),(29,480),(191,480)),track((0,235),(14,235),(29,145),(48,395),(191,395))),
        block("b","B","#D66651",track((0,145),(64,145),(80,480),(146,480),(166,803),(191,803)),
              track((0,329),(64,329),(80,145),(103,319),(126,319),(146,145),(166,235),(191,235))),
        text("step_one","1   PUSH A",165,498,24,"#327E7E",font="display",opacity=track((0,1),(63,1),(64,.3))),
        text("step_two","2   PUSH B",480,498,24,"#D66651",font="display",opacity=track((0,.3),(63,.3),(64,1),(125,1),(126,.3))),
        text("step_three","3   POP RETURNS B",780,498,24,"#243D58",font="display",opacity=track((0,.3),(125,.3),(126,1))))]
    s["beats"]=[beat("first_push","stack",48,"A rests at the bottom of the stack.",["push_a"],["a","stack_outline"]),
                beat("second_push","stack",105,"B now rests above A.",["push_b"],["a","b","stack_outline"]),
                beat("first_out","stack",179,"B is at the output while A remains in the stack.",["pop_b"],["a","b","stack_outline"])]
    s["audio"]=[{"frame":frame,"duration":.3,"frequency":freq,"gain":.1,"kind":"pop"} for frame,freq in [(48,330),(103,440),(166,660)]]
    return s


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",default="examples/stories/stack-explainer/story.json")
    print(save(make_story(),p.parse_args().output))
