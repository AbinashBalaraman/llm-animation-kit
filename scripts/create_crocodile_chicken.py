"""A caption-independent friendship film; artwork belongs here, not in the engine.

The causal chain is fear -> an egg in danger -> a careful rescue -> a return ->
reciprocal trust. Contact uses a shared parent and the reusable anchor helper.
"""
import argparse
from pathlib import Path
from animation_kit.authoring import *
from animation_kit.contracts import read_json
from animation_kit.motion import arc, follow_anchor

PROMPT="create a story of a crocodile and chicken and how they become friends"
INK="#214D48"; GREEN="#60A86D"; LIGHT="#BADD91"; CREAM="#FFF6DD"
RED="#D56958"; GOLD="#EBB653"; SKY="#F5E8C8"; WATER="#68B9B1"


def outlined(node):
    return dict(node,stroke=INK,stroke_width=3)


def assets():
    chicken=[
        group("leg_back",path("shin_back",[("M",0,0),("L",0,26),("L",18,26)],stroke=GOLD,stroke_width=6),x=-15,y=-26),
        group("leg_front",path("shin_front",[("M",0,0),("L",0,26),("L",22,26)],stroke=GOLD,stroke_width=6),x=15,y=-26),
        outlined(path("tail",[("M",-32,-85),("Q",-97,-169,-65,-72),("Q",-100,-129,-54,-54),("Z",)],CREAM)),
        outlined(ellipse("body",51,65,CREAM,y=-81)),
        ellipse("belly",32,44,"#F2E4C7",x=10,y=-75),
        group("head",outlined(ellipse("face",32,37,CREAM)),
              ellipse("comb_a",10,16,RED,x=-16,y=-36),ellipse("comb_b",11,20,RED,x=0,y=-39),ellipse("comb_c",9,15,RED,x=16,y=-35),
              outlined(polygon("beak",[(26,-5),(54,5),(26,13)],GOLD)),
              ellipse("wattle",7,12,RED,x=24,y=23),
              group("eye",ellipse("eye_white",11,14,"#FFFFFF"),ellipse("pupil",5,8,INK,x=4),x=13,y=-7),
              path("brow",[("M",3,-24),("Q",15,-32,23,-21)],stroke=INK,stroke_width=3),
              ellipse("cheek",10,6,"#E8B18E",x=9,y=15),x=19,y=-140),
        group("wing",outlined(path("feathers",[("M",0,0),("Q",-37,8,-22,45),("Q",-8,62,9,25),("Q",16,9,0,0),("Z",)],"#EDE1BC")),x=-12,y=-103)]
    croc=[
        group("tail",outlined(path("tail_shape",[("M",-65,-62),("Q",-137,-49,-211,-12),("Q",-139,12,-62,-2),("Z",)],GREEN)),x=-18),
        group("rear_leg",outlined(ellipse("rear_thigh",27,21,GREEN)),outlined(ellipse("rear_foot",36,12,GREEN,x=8,y=17)),x=-50,y=-10),
        outlined(ellipse("body",104,51,GREEN,y=-53)),ellipse("belly",80,29,LIGHT,x=10,y=-39),
        *[polygon(f"scute_{i}",[(-10,0),(0,-15),(11,0)],INK,x=-72+i*27,y=-94) for i in range(6)],
        group("head",outlined(ellipse("skull",49,46,GREEN,x=85,y=-82)),
              group("jaw",outlined(path("lower",[("M",0,0),("L",143,0),("Q",141,28,24,21),("Q",0,18,0,0),("Z",)],LIGHT)),
                    *[polygon(f"tooth_{i}",[(0,0),(5,-11),(10,0)],CREAM,x=30+i*24,y=1) for i in range(4)],x=94,y=-69),
              outlined(path("snout",[("M",82,-106),("Q",177,-113,238,-96),("L",241,-70),("Q",173,-55,83,-72),("Z",)],GREEN)),
              ellipse("nose",5,3,INK,x=223,y=-91),
              ellipse("eye_ridge",22,26,GREEN,x=93,y=-120),
              group("eye",ellipse("eye_white",14,19,"#FFFFFF"),ellipse("pupil",6,11,INK,x=5),x=96,y=-126),
              path("brow",[("M",76,-145),("Q",95,-155,111,-141)],stroke=INK,stroke_width=3),
              path("smile",[("M",125,-75),("Q",160,-67,193,-77)],stroke=INK,stroke_width=3)),
        group("front_leg",outlined(ellipse("front_thigh",25,20,GREEN)),outlined(ellipse("front_foot",37,12,GREEN,x=15,y=18)),x=53,y=-10)]
    egg=[outlined(ellipse("shell",19,26,CREAM)),ellipse("shine",5,10,"#FFFFFF",x=-6,y=-8)]
    return [{"id":"chicken","description":"Cream hen with jointed wings, orange feet, red comb, expressive head and eyes.","nodes":chicken},
            {"id":"croc","description":"Long green crocodile with broad snout, back scutes, articulated jaw, head, legs and tail.","nodes":croc},
            {"id":"egg","description":"An intact cream egg with a small highlight.","nodes":egg}]


def scenery(*,river=True):
    nodes=[ellipse("sun",62,62,"#F3CD7C",x=785,y=105),
        path("hill_far",[("M",0,232),("Q",185,116,359,248),("Q",675,127,960,221),("L",960,540),("L",0,540),("Z",)],"#C2D0A1"),
        path("hill_near",[("M",0,302),("Q",283,202,502,304),("Q",766,202,960,310),("L",960,540),("L",0,540),("Z",)],"#99B790"),
        rect("ground",960,170,"#D7D99F",y=370)]
    if river:
        nodes += [path("river",[("M",566,337),("Q",499,401,425,540),("L",960,540),("L",960,346),("Q",742,326,566,337),("Z",)],WATER),
            path("bank",[("M",566,337),("Q",499,401,425,540)],stroke="#F2D4A0",stroke_width=16)]
        for i in range(7):
            nodes.append(path(f"ripple_{i}",[("M",0,0),("Q",29,8,64,0)],stroke="#A4DED0",stroke_width=3,x=585+(i*97)%260,y=373+i*23))
    for i in range(7):
        x=25+i*57; y=460+(i%3)*19
        nodes.append(path(f"grass_{i}",[("M",x-5,y),("Q",x-9,y-26,x-18,y-34),("M",x,y),("Q",x+3,y-30,x+11,y-39)],stroke="#789766",stroke_width=3))
    return nodes


def nest(x,y):
    return group("nest",ellipse("shadow",55,13,"#B3B780",y=8),
        outlined(ellipse("straw",48,14,"#C1965C")),
        *[path(f"fiber_{i}",[("M",-38+i*13,-6),("L",-25+i*13,8)],stroke="#EDD090",stroke_width=3) for i in range(6)],x=x,y=y)


def flower(x,y,**props):
    return group("flower",path("stem",[("M",0,0),("L",0,-47)],stroke=INK,stroke_width=4),
        *[ellipse(f"petal_{i}",12,12,RED,x=dx,y=-48+dy) for i,(dx,dy) in enumerate([(0,-13),(13,0),(0,13),(-13,0)])],
        ellipse("pollen",8,8,GOLD,y=-48),x=x,y=y,**props)


def make_story():
    doc=story(PROMPT,[("characters","Recognizable crocodile and chicken with distinct expressions and poses."),
        ("danger","The chicken's egg visibly leaves the nest and falls toward the river; she reacts."),
        ("rescue","The crocodile catches the falling egg on his snout and returns it intact."),
        ("friendship","The chicken changes from fear to trust and gives the crocodile a flower; they share the bank.")],title="A Friend with Teeth")
    doc["frames"]=528; doc["assets"]=assets()
    # 0-4s: a shared geography, a frightened hen, and a crocodile who notices.
    intro=shot("strangers",0,96,"The hen guards her egg and recoils from the crocodile's teeth.",SKY,
        *scenery(),nest(343,396),instance("egg","egg",x=343,y=367),
        instance("hen","chicken",x=track((0,272),(23,272),(35,243),(60,250)),y=420,
            overrides={"head":{"rotation":track((0,5),(26,5),(36,-13),(64,-8))},"wing":{"rotation":track((0,0),(30,0),(40,65))},
                "leg_front":{"rotation":track((0,0),(26,0),(33,-24),(41,0))},"leg_back":{"rotation":track((0,0),(26,0),(33,23),(41,0))}}),
        instance("croc","croc",x=826,y=432,scale_x=-.88,scale_y=.88,
            overrides={"jaw":{"rotation":track((0,0),(16,18),(30,18),(45,0))},"eye":{"scale_y":track((0,1),(68,1),(71,.08),(75,1))}}),
        text("title","A FRIEND WITH TEETH",480,57,40,INK,font="display",opacity=track((0,1),(53,1),(72,0))))
    # 4-7s: the wind and downhill path are visible; no prose explains the danger.
    trouble=shot("danger",96,168,"A gust rocks the egg out of its nest. The hen reaches too late at the riverbank.",SKY,
        *scenery(),nest(330,361),
        *[path(f"gust_{i}",[("M",0,0),("Q",80,-18,164,0)],stroke="#FFF6DD",stroke_width=4,
               x=track((0,-180),(50,800)),y=227+i*22,opacity=track((0,0),(8,.9),(45,.9),(58,0))) for i in range(3)],
        instance("hen","chicken",x=track((0,215),(22,215),(48,290)),y=track((0,419),(27,419),(35,407),(48,419)),
            overrides={"wing":{"rotation":track((0,0),(18,-100),(68,-100))},"head":{"rotation":track((0,0),(26,15),(68,22))},
                "leg_front":{"rotation":track((0,0),(23,0),(31,-30),(40,28),(49,0))},"leg_back":{"rotation":track((0,0),(23,0),(31,28),(40,-30),(49,0))}}),
        instance("egg","egg",x=track((0,330),(16,340),(29,390),(50,536),(71,616,"linear")),
            y=track((0,332),(16,329),(29,352),(50,379),(71,413,"in_cubic")),rotation=track((0,0),(10,-12),(16,20),(50,200),(71,250))))
    # 7-11s: close view. Egg falls from above, never through the croc's body.
    root={"x":track((0,210),(18,260),(30,390),(44,400),(70,400),(95,400)),
          "y":track((0,686),(18,679),(30,621),(39,631),(52,621),(95,621))}
    contact=30
    held=follow_anchor(range(contact,96),[root],(218,-123))
    falling=arc(0,contact,(616,413),(608,498),lift=-12)
    catch=shot("rescue",168,264,"A close view shows the croc rise under the falling egg, cushion it, and hold it safely above water.","#DCECD6",
        rect("water",960,550,WATER,y=250),
        *[path(f"line_{i}",[("M",0,0),("Q",65,15,139,0)],stroke="#9DD8CA",stroke_width=4,x=28+(i*203)%780,y=420+(i%4)*61) for i in range(9)],
        instance("croc","croc",**root,overrides={"head":{"rotation":0},"front_leg":{"rotation":track((0,0),(20,-24),(39,13),(52,0))},
            "tail":{"rotation":track((0,0),(18,10),(30,-7),(47,0))},"eye":{"scale_y":track((0,1),(29,1),(34,.45),(49,1))}}),
        instance("egg_falling","egg",**falling,rotation=track((0,250),(30,360)),opacity=track((0,1),(contact,0,"hold"))),
        instance("egg_held","egg",**held,rotation=track((0,0),(30,0),(39,12),(52,0)),opacity=track((0,0),(contact,1,"hold"))),
        *[ellipse(f"splash_{i}",5,13,"#D7EFE2",x=455+i*33,y=track((0,667),(23,657),(36,551-i*9),(51,677)),
                  opacity=track((0,0),(20,0),(24,1),(49,0))) for i in range(4)],camera={"x":480,"y":490,"zoom":1.4})
    # 11-13s reaction, then 13-17s return: show the hen understand the rescue.
    return_root={"x":track((0,738),(39,628),(60,628),(95,772)),"y":track((0,421),(39,468),(60,468),(95,429)),"scale_x":-1}
    carried=follow_anchor(range(0,50),[return_root],(218,-123))
    relief=shot("relief",264,312,"Close on the hen: alarm turns to relief when she sees her intact egg balanced on the croc's snout.",SKY,
        *scenery(),nest(370,382),
        instance("hen","chicken",x=270,y=420,overrides={"head":{"rotation":track((0,18),(17,18),(33,0),(47,6))},
            "wing":{"rotation":track((0,-95),(18,-95),(36,0))},"eye":{"scale_y":track((0,1.18),(18,1.18),(25,.15),(32,1),(40,.45))},
            "brow":{"rotation":track((0,14),(30,0))}}),
        instance("croc","croc",x=680,y=421,scale_x=-1),instance("egg","egg",x=462,y=298),
        camera={"x":345,"y":315,"zoom":1.65})
    give=shot("return",312,408,"The crocodile lowers the intact egg into the nest; the hen relaxes and leans toward him.",SKY,
        *scenery(),nest(370,382),
        path("plant_stalk",[("M",258,361),("L",258,420)],stroke=INK,stroke_width=4),flower(258,361,rotation=-12),
        instance("hen","chicken",x=270,y=420,overrides={"head":{"rotation":track((0,15),(44,15),(63,0),(80,7))},
            "wing":{"rotation":track((0,-82),(43,-82),(69,0))},"eye":{"scale_y":track((0,1),(58,1),(64,.2),(76,1))}}),
        instance("croc","croc",**return_root,overrides={"eye":{"scale_y":track((0,1),(62,1),(69,.3),(80,1))}}),
        instance("egg_carried","egg",**carried,opacity=track((0,1),(50,0,"hold"))),
        instance("egg_safe","egg",**arc(50,60,(410,345),(370,355),lift=12),
                 rotation=track((0,0),(50,0),(55,-18),(60,0)),opacity=track((0,0),(50,1,"hold"))))
    # 17-22s: a reciprocal gesture. Chicken approaches the former threat voluntarily.
    giftroot=arc(8,56,(270,420),(500,420),lift=150)
    wing={"x":-12,"y":-103,"rotation":track((0,0),(8,0),(20,-100),(48,-100),(63,-76),(84,-76),(94,0))}
    bouquet=follow_anchor(range(0,85),[giftroot,wing],(0,44))
    # The flower is passed to the crocodile at a matching position on frame 84.
    fx=bouquet["x"]["keys"][-1]["value"]; fy=bouquet["y"]["keys"][-1]["value"]
    friends=shot("friends",408,528,"The hen plucks the flower, hops over the nest to approach the croc, and offers it. He accepts with a soft blink.",SKY,
        *scenery(),nest(370,382),instance("egg","egg",x=370,y=355),
        path("plant_stalk",[("M",258,361),("L",258,420)],stroke=INK,stroke_width=4),
        instance("croc","croc",x=772,y=429,scale_x=-1,overrides={"eye":{"scale_y":track((0,1),(80,1),(86,.2),(101,.35))},
            "front_leg":{"rotation":track((0,0),(108,0),(115,-8),(119,0))}}),
        instance("hen","chicken",**giftroot,overrides={"wing":wing,
            "head":{"rotation":track((0,0),(54,0),(87,17),(119,17))},"eye":{"scale_y":track((0,1),(86,1),(94,.2))},
            "leg_front":{"rotation":track((0,0),(8,-12),(20,-48),(43,-48),(56,12),(63,0))},
            "leg_back":{"rotation":track((0,0),(8,12),(20,48),(43,48),(56,-12),(63,0))}}),
        flower(bouquet["x"],bouquet["y"],rotation=track((0,-12),(8,-12),(30,30),(63,90),(84,90)),opacity=track((0,1),(85,0,"hold"))),
        group("accepted_flower",flower(0,0),x=fx,y=fy,rotation=track((0,90),(84,90),(105,103)),opacity=track((0,0),(85,1,"hold"))),
        text("end","A LITTLE KINDNESS GOES A LONG WAY.",480,66,28,INK,font="display",opacity=track((0,0),(88,0),(111,1))))
    # IDs are scoped to a shot, including groups: rename the nested flower.
    friends["nodes"][-2]["children"][0]["id"]="gift_bloom"
    for child in friends["nodes"][-2]["children"][0]["children"]: child["id"]="gift_"+child["id"]
    doc["shots"]=[intro,trouble,catch,relief,give,friends]
    doc["beats"]=[beat("fear","strangers",40,"Hen recoils from the crocodile beside her nest.",["characters","friendship"],["hen","croc"]),
        beat("rolling","danger",147,"Egg leaves the nest, hen reaches, water is below.",["danger"],["egg","hen"]),
        beat("catch","rescue",198,"Egg contacts the top of the snout, clear of water.",["rescue"],["egg_held","croc"]),
        beat("relief","relief",301,"Hen sees the saved egg and relaxes in a closer shot.",["friendship"],["hen","egg","croc"]),
        beat("safe","return",388,"Egg rests intact in the nest and hen lowers her wing.",["rescue"],["egg_safe","hen","croc"]),
        beat("gift","friends",485,"Hen voluntarily approaches and gives a flower.",["friendship","characters"],["hen","croc","flower"]),
        beat("together","friends",518,"They stay together with the saved egg beside them.",["friendship"],["hen","croc","accepted_flower"])]
    doc["audio"]=[{"frame":f,"duration":dur,"frequency":hz,"gain":gain,"kind":kind} for f,dur,hz,gain,kind in
        [(22,.2,150,.07,"pop"),(125,.25,430,.06,"pop"),(198,.6,523,.1,"bell"),(370,.5,659,.09,"bell"),(494,1.3,784,.1,"bell")]]
    doc["direction"]=read_json(Path(__file__).resolve().parents[1]/"examples/stories/crocodile-chicken/direction.json")
    return doc


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",default="examples/stories/crocodile-chicken/story.json")
    print(save(make_story(),p.parse_args().output))
