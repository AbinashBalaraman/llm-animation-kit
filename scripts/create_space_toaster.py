"""A second, unrelated authored film: a toaster launches toast into orbit.

Uses exactly the same engine and SDK as the cat film, with new art and acting.
"""
import argparse
from animation_kit.authoring import *

PROMPT="A tiny toaster dreams of space, launches its toast like a rocket, and watches it become a moon."
INK="#222943"; CREAM="#FFF0D8"; CORAL="#E98370"; TEAL="#6DC7BC"


def make_story():
    doc=story(PROMPT,[("toaster","A recognizable toaster is the protagonist."),
                     ("launch","Toast visibly launches from the toaster like a rocket."),
                     ("moon","The launched toast becomes a moon in space, with a visual payoff.")],title="One small step for toast")
    doc["frames"]=240
    doc["assets"]=[{"id":"toaster","description":"An original coral countertop toaster with top slots, eyes, a lever and feet.","nodes":[
        rect("body",210,133,CORAL,x=-105,y=-133,radius=33,stroke=INK,stroke_width=5),
        ellipse("top",90,21,"#D46762",y=-128,stroke=INK,stroke_width=3),
        rect("slot",122,10,INK,x=-61,y=-137,radius=5),
        ellipse("eye_left",8,12,INK,x=-38,y=-79),ellipse("eye_right",8,12,INK,x=38,y=-79),
        path("smile",[("M",-15,-53),("Q",0,-36,15,-53)],stroke=INK,stroke_width=4),
        rect("lever_slot",7,74,INK,x=101,y=-111,radius=3),
        group("lever",rect("stem",26,7,INK),ellipse("knob",13,11,TEAL,x=30,y=4,stroke=INK,stroke_width=3),x=107,y=-105),
        rect("foot_left",33,13,INK,x=-77,y=-1,radius=4),rect("foot_right",33,13,INK,x=44,y=-1,radius=4)]},
        {"id":"toast","description":"A piece of golden toast with rounded crown and dark crust, entirely authored vector geometry.","nodes":[
            path("crust",[("M",-53,-35),("C",-83,-102,83,-102,53,-35),("L",49,62),("Q",0,78,-49,62),("Z",)],"#B57444",stroke=INK,stroke_width=4),
            path("crumb",[("M",-40,-32),("C",-66,-78,66,-78,40,-32),("L",38,52),("Q",0,63,-38,52),("Z",)],"#F7D287"),
            ellipse("crumb_a",5,4,"#D8AA66",x=-18,y=-20),ellipse("crumb_b",4,3,"#D8AA66",x=20,y=27),
            ellipse("crumb_c",3,3,"#D8AA66",x=-14,y=39)]}]
    doc["shots"]=[shot("dream",0,72,"A toaster looks from the counter toward a space poster.",CREAM,
        rect("counter",960,150,"#B9D5CA",y=390),rect("counter_edge",960,12,INK,y=390),
        rect("poster",221,230,INK,x=650,y=107,radius=8),ellipse("poster_moon",57,57,"#E3D8B9",x=760,y=197),
        text("poster_text","DREAM BIG",760,292,27,CREAM,font="display"),
        instance("dreamer","toaster",x=351,y=385,overrides={"lever":{"y":track((0,-105),(24,-44),(71,-44))}}),
        text("title","ONE SMALL STEP FOR TOAST",480,49,38,INK,font="display"),
        text("caption","Some appliances dream bigger.",480,487,28,INK)),
      shot("launch",72,168,"Toast accelerates upward from the slot with squash, anticipation and a flame.","#AFD9E0",
        rect("counter",960,112,"#B9D5CA",y=428),rect("counter_edge",960,12,INK,y=428),
        group("rocket",path("flame",[("M",-26,59),("Q",-15,108,0,149),("Q",17,106,26,59),("Z",)],CORAL,
                             scale_y=track((0,.01),(21,.01),(35,1),(48,.65),(61,1.2),(80,.8)),opacity=track((0,0),(20,0),(21,1))),
              instance("bread","toast"),x=480,y=track((0,281),(20,310),(34,210),(62,-120,"in_cubic"),(95,-160)),
              scale_x=track((0,.8),(20,.95),(34,.65),(60,.8)),scale_y=track((0,.8),(20,.65),(34,1.1),(60,.8))),
        instance("launcher","toaster",x=480,y=416,scale_x=track((0,1),(20,1.12),(28,.92),(42,1)),
                 scale_y=track((0,1),(20,.84),(28,1.06),(42,1)),overrides={"lever":{"y":track((0,-44),(20,-44),(29,-105))}}),
        text("launch_text","LIFT-OFF!",190,117,42,INK,font="display",opacity=track((0,0),(27,0),(28,1)))),
      shot("orbit",168,240,"The toast becomes a large moon above a tiny planet; the toast shape makes the absurd outcome visible.",INK,
        *[ellipse(f"star_{i}",2+(i%3),2+(i%3),CREAM,x=35+(i*137)%895,y=50+(i*83)%355) for i in range(20)],
        ellipse("planet",202,122,TEAL,x=480,y=521),
        instance("toast_moon","toast",x=track((0,494),(71,516)),y=199,rotation=track((0,-15),(71,10)),scale_x=1.4,scale_y=1.4),
        text("moon_title","THE MOON IS NOW GLUTEN.",480,43,34,CREAM,font="display"),
        text("end","Houston, we have breakfast.",480,386,29,CREAM))]
    doc["beats"]=[beat("identity","dream",48,"Toaster body, slot and lever establish the new character.",["toaster"],["dreamer"]),
                  beat("blastoff","launch",108,"Toast emerges above the reacting toaster with a flame.",["launch","toaster"],["rocket","launcher"]),
                  beat("payoff","orbit",213,"A clearly toast-shaped moon floats above a planet.",["moon"],["toast_moon","planet"])]
    doc["audio"]=[{"frame":96,"duration":.35,"frequency":190,"gain":.18,"kind":"pop"},
                  {"frame":171,"duration":1.3,"frequency":698,"gain":.15,"kind":"bell"}]
    return doc


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",default="examples/stories/space-toaster/story.json")
    print(save(make_story(),parser.parse_args().output))
