"""Authored regression film for the user's failed brief. Not an engine preset.

All character, set, prop, pose and shot decisions live in this editable script.
Run to write a portable story JSON; the host then uses the normal production tools.
"""
from pathlib import Path
import argparse
from animation_kit.authoring import *

INK="#183B4E"; CREAM="#FFF2D6"; GOLD="#EBA249"; LIGHT="#FFC978"
TEAL="#367E80"; RED="#D85B50"; BLUE="#264F70"; WHITE="#FFFCF3"
PROMPT="Create a small funny story of a cat becoming president of the US."


def line(i, commands, color=INK, width=3, **props):
    return path(i,commands,stroke=color,stroke_width=width,**props)


def cat_asset():
    eye=lambda side,x: group(side,
        ellipse(side+"_white",12,17,WHITE,stroke=INK,stroke_width=2),
        ellipse(side+"_iris",7,12,TEAL,x=1),ellipse(side+"_pupil",3,10,INK,x=2),
        ellipse(side+"_shine",2.4,3,WHITE,x=4,y=-5),x=x,y=-8)
    face=[
        polygon("ear_left",[(-57,-17),(-53,-79),(-12,-49)],GOLD,stroke=INK,stroke_width=4),
        polygon("ear_right",[(12,-49),(53,-79),(57,-17)],GOLD,stroke=INK,stroke_width=4),
        polygon("inner_ear_left",[(-46,-34),(-45,-64),(-27,-46)],"#E99389"),
        polygon("inner_ear_right",[(27,-46),(45,-64),(46,-34)],"#E99389"),
        ellipse("face",65,51,GOLD,stroke=INK,stroke_width=4),
        ellipse("muzzle_left",26,21,CREAM,x=-21,y=19),ellipse("muzzle_right",26,21,CREAM,x=21,y=19),
        eye("eye_left",-25),eye("eye_right",25),
        line("sleep_left",[("M",-36,-7),("Q",-25,2,-14,-7)],opacity=0),
        line("sleep_right",[("M",14,-7),("Q",25,2,36,-7)],opacity=0),
        polygon("nose",[(-8,12),(8,12),(0,20)],RED),
        line("mouth",[("M",0,20),("Q",-2,32,-14,29),("M",0,20),("Q",2,32,14,29)]),
        polygon("stripe_a",[(-20,-44),(-8,-25),(-6,-48)],"#BB7139"),
        polygon("stripe_b",[(5,-48),(9,-25),(21,-44)],"#BB7139")]
    for s,name in [(-1,"left"),(1,"right")]:
        for j in range(3):
            face.append(line(f"whisker_{name}_{j}",[("M",s*39,14+j*7),("L",s*80,7+j*13)],width=2))
    arm=lambda name,x,sign: group(name,
        line(name+"_outline",[("M",0,0),("Q",sign*20,23,sign*14,49)],INK,23),
        line(name+"_fur",[("M",0,0),("Q",sign*20,23,sign*14,49)],GOLD,16),
        ellipse(name+"_paw",17,14,LIGHT,x=sign*14,y=49,stroke=INK,stroke_width=3),x=x,y=-128)
    return {"id":"mittens","description":"Original orange tabby: triangular pink ears, whiskers, vertical pupils, cream muzzle, articulated paws and curled tail.","nodes":[
        group("tail",line("tail_outline",[("M",0,0),("C",79,16,111,-94,65,-98)],INK,24),
              line("tail_fur",[("M",0,0),("C",79,16,111,-94,65,-98)],GOLD,16),x=39,y=-52),
        ellipse("body",49,73,GOLD,x=0,y=-86,stroke=INK,stroke_width=4),
        ellipse("bib",30,51,CREAM,x=0,y=-78),
        ellipse("foot_left",25,13,LIGHT,x=-28,y=-10,stroke=INK,stroke_width=3),
        ellipse("foot_right",25,13,LIGHT,x=28,y=-10,stroke=INK,stroke_width=3),
        arm("left_arm",-43,-1),arm("right_arm",43,1),
        group("head",*face,y=-177),
        group("tie",polygon("collar_left",[(-30,0),(0,7),(-10,24)],WHITE,stroke=INK,stroke_width=2),
              polygon("collar_right",[(0,7),(30,0),(10,24)],WHITE,stroke=INK,stroke_width=2),
              polygon("tie_knot",[(-7,9),(7,9),(4,18),(-4,18)],RED),
              polygon("tie_tail",[(-4,18),(4,18),(10,44),(0,51),(-10,44)],RED),y=-128,opacity=0)]}


def sleepy_asset():
    return {"id":"sleepy_mittens","description":"The same orange tabby curled into a sleeping loaf; ears, whiskers, stripes and closed eyes remain identifiable.","nodes":[
        ellipse("loaf",106,52,GOLD,x=24,y=-51,stroke=INK,stroke_width=4),
        line("curl_outline",[("M",103,-69),("C",164,-11,59,21,37,-24)],INK,25),
        line("curl",[("M",103,-69),("C",164,-11,59,21,37,-24)],LIGHT,17),
        polygon("ear_l",[(-110,-63),(-117,-124),(-70,-91)],GOLD,stroke=INK,stroke_width=4),
        polygon("ear_r",[(-67,-93),(-22,-119),(-21,-63)],GOLD,stroke=INK,stroke_width=4),
        ellipse("head",58,43,GOLD,x=-64,y=-67,stroke=INK,stroke_width=4),
        ellipse("muzzle",34,18,CREAM,x=-64,y=-47),
        polygon("nose",[(-71,-54),(-57,-54),(-64,-46)],RED),
        line("eye_l",[("M",-101,-67),("Q",-89,-54,-77,-67)],width=4),
        line("eye_r",[("M",-54,-67),("Q",-42,-54,-30,-67)],width=4),
        line("whisker_l",[("M",-92,-45),("L",-137,-53),("M",-92,-38),("L",-132,-31)],width=2),
        line("whisker_r",[("M",-37,-45),("L",3,-49),("M",-37,-38),("L",5,-27)],width=2),
        ellipse("paws",39,13,CREAM,x=-63,y=-17,stroke=INK,stroke_width=3),
        polygon("stripe",[(-77,-104),(-67,-84),(-60,-108)],"#BB7139") ]}


def flag(ident,x,y,scale=1):
    shapes=[rect(ident+"_field",94,58,WHITE)]
    for n in range(7): shapes.append(rect(f"{ident}_stripe_{n}",94,58/13,RED,y=n*58/6.5))
    shapes.append(rect(ident+"_blue",43,32,BLUE))
    for row in range(3):
        for col in range(4): shapes.append(ellipse(f"{ident}_star_{row}_{col}",1.6,1.6,WHITE,x=7+col*9,y=7+row*9))
    return group(ident,line(ident+"_pole",[("M",0,-8),("L",0,175)],"#AD8456",5),
                 ellipse(ident+"_top",5,5,"#D3AC69",y=-10),*shapes,x=x,y=y,scale_x=scale,scale_y=scale)


def caption(top,bottom):
    return [rect("caption_band",960,57,INK,y=483),
            text("caption",bottom,480,510,24,CREAM),
            text("heading",top,480,43,31,INK,font="display")]


def office():
    nodes=[rect("wall_lower",960,220,"#DCDEC6",y=270),
           ellipse("oval_window_frame",242,169,"#CBA56B",x=480,y=196),
           ellipse("oval_window",226,153,"#BBDADC",x=480,y=196),
           ellipse("lawn",211,49,"#8FB18E",x=480,y=300),
           rect("white_house",155,57,WHITE,x=402,y=237),
           polygon("roof",[(388,237),(480,202),(572,237)],WHITE,stroke="#8BB3B6",stroke_width=2)]
    for i in range(6): nodes.append(rect(f"column_{i}",10,47,"#BAC9CA",x=418+i*23,y=245))
    nodes += [rect("window_vertical",7,278,WHITE,x=476,y=50),rect("window_horizontal",439,7,WHITE,x=260,y=189),
              flag("flag_left",126,178,1.15),flag("flag_right",737,178,1.15),
              rect("chair",155,159,BLUE,x=402,y=231,radius=30,stroke=INK,stroke_width=4)]
    return nodes


def desk():
    return [rect("desktop",660,28,"#B77C51",x=150,y=355,radius=7,stroke=INK,stroke_width=4),
            rect("desk_front",609,115,"#986143",x=175,y=382,stroke=INK,stroke_width=4),
            rect("desk_inset",575,82,"#B47950",x=192,y=396,radius=9),
            ellipse("seal",42,42,"#D7B978",x=480,y=438,stroke=INK,stroke_width=3),
            text("seal_text","USA",480,438,24,INK,font="display"),
            rect("nameplate",221,33,INK,x=220,y=357,radius=5),
            text("president_label","PRESIDENT MITTENS",330,372,18,CREAM,font="display")]


def make_story():
    doc=story(PROMPT,[
        ("cat","A recognizable cat is the protagonist; maintain its identity across shots."),
        ("campaign","Show the cat campaigning for president, with a visible campaign action."),
        ("election","Show the cat winning the election, not just a presidential title."),
        ("us_president","Establish the US presidency through the office, flags and presidential role."),
        ("comedy","Deliver visual jokes and a payoff caused by the cat's behavior.")],title="Mittens takes office")
    doc["frames"]=576
    doc["assets"]=[cat_asset(),sleepy_asset()]
    blink=track((0,1),(22,1),(24,.06),(27,1),(66,1),(69,.06),(72,1))
    kitchen=[rect("floor",960,180,"#E8CFA9",y=360),rect("skirting",960,9,"#C3A079",y=353),
             rect("cupboard",183,201,"#B5CDB8",x=733,y=151,radius=6,stroke=INK,stroke_width=3),
             line("cupboard_divider",[("M",824,155),("L",824,350)],width=2),
             ellipse("knob_l",4,4,INK,x=807,y=246),ellipse("knob_r",4,4,INK,x=839,y=246),
             rect("price_card",162,96,WHITE,x=65,y=122,radius=9,stroke=INK,stroke_width=3),
             text("milk_price","MILK: $9",146,161,27,RED,font="display"),
             text("price_note","per tiny bowl",146,190,15),
             ellipse("cat_shadow",100,15,"#C4A784",x=414,y=452),
             instance("cat","mittens",x=398,y=451,scale_x=1.17,scale_y=1.17,
                      overrides={"head":{"rotation":track((0,0),(20,-9),(48,-9),(65,6))},
                                 "eye_left":{"scale_y":blink},"eye_right":{"scale_y":blink},
                                 "right_arm":{"rotation":track((0,0),(35,-65),(67,-65),(95,0))},
                                 "tail":{"rotation":track((0,-8),(30,8),(60,-8),(95,8))}}),
             ellipse("empty_bowl",57,21,TEAL,x=639,y=432,stroke=INK,stroke_width=4),
             ellipse("bowl_inside",45,9,"#2C6067",x=639,y=422),
             text("empty_label","EMPTY",639,459,16,INK,font="display"),
             group("idea",ellipse("idea_halo",35,35,"#F9D377"),text("idea_mark","!",0,1,43,INK,font="display"),
                   x=582,y=151,opacity=track((0,0),(56,0),(57,1)),scale_x=track((0,.5),(57,.5),(70,1,"out_back")),scale_y=track((0,.5),(57,.5),(70,1,"out_back")))]
    doc["shots"].append(shot("ambition",0,96,"An empty bowl and expensive milk give Mittens a political ambition.",CREAM,*kitchen,
                              *caption("EMPTY BOWL. BIG AMBITIONS.","Mittens had one policy: more milk.")))
    rally=[rect("rally_wall",960,385,"#BCD6D0"),rect("rally_floor",960,165,"#DFB888",y=375),
           rect("banner",598,88,INK,x=181,y=90,radius=9),
           text("campaign_name","MITTENS FOR PRESIDENT",480,126,35,WHITE,font="display"),
           text("campaign_tag","A VERY QUALIFIED CAT",480,158,16,"#D4E9E2"),
           flag("rally_flag_l",72,190,1.3),flag("rally_flag_r",775,190,1.3),
           instance("candidate","mittens",x=480,y=403,scale_x=.96,scale_y=.96,overrides={
               "tie":{"opacity":1},"right_arm":{"rotation":track((0,0),(16,-112),(31,-87),(45,-112),(60,-87),(78,-100),(105,0))},
               "tail":{"rotation":track((0,6),(40,-12),(80,6),(119,-8))}}),
           rect("podium",236,144,TEAL,x=362,y=340,radius=8,stroke=INK,stroke_width=4),
           rect("podium_top",267,16,INK,x=347,y=335,radius=5),
           text("promise_a","NAP MORE.",480,384,33,WHITE,font="display"),
           text("promise_b","WORK LESS.",480,426,33,WHITE,font="display"),
           line("mic_stem",[("M",550,335),("L",550,297),("L",517,284)],width=5),
           ellipse("microphone",13,8,INK,x=516,y=284,rotation=20)]
    # A foreground audience responds; it does not replace the protagonist.
    for i in range(7):
        x=66+i*141; y=492+(i%2)*8
        rally.append(group(f"crowd_{i}",ellipse(f"crowd_head_{i}",30,32,BLUE),
             polygon(f"crowd_ears_{i}",[(-26,-10),(-28,-42),(-8,-29),(7,-29),(29,-43),(26,-9)],BLUE),
             x=x,y=track((0,y),(44,y-9),(72,y),(100,y-7))))
    doc["shots"].append(shot("campaign",96,216,"Mittens waves from a campaign podium, promising more naps and less work.","#BCD6D0",*rally,
                              *caption("THE CAMPAIGN",'His platform? "Nap more. Work less."')))
    election=[rect("results_card",880,331,WHITE,x=40,y=94,radius=21,stroke=INK,stroke_width=3),
              text("election_header","ELECTION NIGHT",480,121,24,INK,font="display"),
              instance("winner","mittens",x=213,y=381,scale_x=.79,scale_y=.79,overrides={"tie":{"opacity":1},
                       "right_arm":{"rotation":track((0,0),(45,0),(60,-122),(78,-108),(95,-122))},
                       "left_arm":{"rotation":track((0,0),(45,0),(60,122),(95,122))}}),
              text("winner_label","MITTENS",470,201,30,TEAL,font="display",align="left"),
              rect("winner_bar_bg",363,36,"#E4E8D9",x=465,y=225,radius=6),
              rect("winner_bar",360,36,TEAL,x=465,y=225,radius=6,scale_x=track((0,.02),(44,1,"out_cubic"))),
              text("winner_percent","99%",837,243,22,INK,font="display",opacity=track((0,0),(44,0),(45,1))),
              text("rival_label","THE VACUUM",470,301,24,INK,font="display",align="left"),
              rect("rival_bar",12,28,RED,x=465,y=327,radius=5),
              text("rival_percent","1%",510,341,20,RED,font="display"),
              group("vacuum",rect("vacuum_body",83,42,RED,radius=17,stroke=INK,stroke_width=3),
                    ellipse("wheel_l",11,11,INK,x=15,y=43),ellipse("wheel_r",11,11,INK,x=66,y=43),
                    line("hose",[("M",65,8),("C",114,-3,66,-67,116,-72)],TEAL,8),
                    line("handle",[("M",116,-72),("L",134,-71)],INK,8),x=333,y=331,scale_x=.75,scale_y=.75),
              text("landslide","A PURR-FECT LANDSLIDE.",480,456,29,INK,font="display",opacity=track((0,0),(46,0),(47,1)))]
    for i in range(26):
        x=70+(i*73)%820; y=70+(i*67)%290
        election.append(rect(f"confetti_{i}",7,15,[RED,TEAL,GOLD][i%3],x=x,
                              y=track((0,y-200),(45,y-200),(95,y+70,"linear")),
                              rotation=track((0,i*17),(95,i*17+180,"linear")),opacity=track((0,0),(46,0),(47,1))))
    doc["shots"].append(shot("election",216,312,"A results board declares Mittens the winner; the defeated rival is a vacuum cleaner.","#E9C677",*election,
                              text("result_caption","Even the dog voted for him.",480,515,25,INK)))
    signing=[*office(),instance("president","mittens",x=479,y=383,scale_x=.83,scale_y=.83,
               overrides={"tie":{"opacity":1},"head":{"rotation":track((0,0),(27,8),(74,8),(108,0))},
                          "right_arm":{"opacity":track((0,1),(29,1),(30,0),(88,0),(89,1))}}),
             *desk(),
             group("order",rect("paper_shadow",239,74,"#795745",x=5,y=7,radius=3),
                   rect("paper",239,74,WHITE,radius=3,stroke=INK,stroke_width=2),
                   text("order_heading","EXECUTIVE ORDER #1",119,16,14,INK,font="display"),
                   text("order_policy","MANDATORY NAPS",116,40,22,TEAL,font="display"),x=542,y=349,rotation=-3),
             group("paw_stamp",ellipse("stamp_pad",13,10,RED,y=4),
                   ellipse("stamp_toe_a",5,7,RED,x=-13,y=-8),ellipse("stamp_toe_b",5,7,RED,x=-3,y=-14),
                   ellipse("stamp_toe_c",5,7,RED,x=9,y=-12),ellipse("stamp_toe_d",5,7,RED,x=18,y=-3),
                   x=726,y=402,rotation=-12,opacity=track((0,0),(58,0),(59,1)),
                   scale_x=track((0,1),(59,1.3),(68,1)),scale_y=track((0,1),(59,1.3),(68,1)))]
    # Foreground paw reaches the paper; both follow the same contact beat.
    signing.append(group("signing_paw",line("signing_arm_outline",[("M",0,0),("L",226,0)],INK,22),
                         line("signing_arm_fur",[("M",0,0),("L",226,0)],GOLD,16),
                         ellipse("signing_fingers",22,17,LIGHT,x=226,stroke=INK,stroke_width=3),
                         x=520,y=315,rotation=track((0,-80),(29,-80),(55,22),(65,22),(89,-80)),
                         scale_x=track((0,.2),(29,.2),(55,1),(65,1),(89,.2)),
                         opacity=track((0,0),(29,0),(30,1),(88,1),(89,0))))
    signing+=caption("THE OVAL OFFICE","His first order was signed... with a paw.")
    doc["shots"].append(shot("first_order",312,456,"In the US presidential office, Mittens paw-stamps an executive order making naps mandatory.",CREAM,*signing))
    ending=[*office(),*desk(),
            rect("nap_order",196,67,WHITE,x=640,y=306,rotation=7,stroke=INK,stroke_width=2),
            text("nap_word","MANDATORY",731,326,18,TEAL,font="display",rotation=7),
            text("naps_word","NAPS",728,349,25,TEAL,font="display",rotation=7),
            instance("sleeping_president","sleepy_mittens",x=454,y=358,scale_x=1.25,
                     scale_y=track((0,1.22),(30,1.27),(60,1.22),(90,1.27),(119,1.22))),
            text("clock","10:01 AM",153,151,23,INK,font="display")]
    for i in range(3):
        ending.append(text(f"zzz_{i}","Z",601+i*38,track((0,260-i*28),(119,220-i*28,"linear")),24+i*8,TEAL,font="display",
                           opacity=track((0,0),(6+i*14,0),(19+i*14,1))))
    ending+=caption("FIRST DAY. FIRST NAP.","He took office. Then he took a nap.")
    doc["shots"].append(shot("payoff",456,576,"Mittens immediately obeys his own order and sleeps on the presidential desk at 10:01 AM.",CREAM,*ending))
    doc["beats"]=[
        beat("recognizable_cat","ambition",65,"Ears, whiskers, pupils, paws and tail identify a tabby inspecting its empty bowl.",["cat"],["cat","empty_bowl"]),
        beat("campaign_promise","campaign",144,"Cat waves at a campaign podium with its nap platform.",["campaign","cat"],["candidate","podium"]),
        beat("wins_election","election",290,"Mittens wins 99% against a vacuum cleaner and raises both paws.",["election","comedy"],["winner","winner_bar","vacuum"]),
        beat("presidential_action","first_order",380,"US flags, office and desk establish presidency; a paw mark signs the nap order.",["us_president","cat"],["president","flag_left","desk_front","paw_stamp"]),
        beat("nap_payoff","payoff",533,"The same cat sleeps on the presidential desk beneath drifting Zs.",["comedy","cat","us_president"],["sleeping_president","desk_front","flag_left"])]
    for frame,freq,kind,gain in [(57,880,"bell",.15),(113,450,"pop",.12),(156,560,"bell",.08),(262,880,"bell",.16),
                                (272,1108,"bell",.13),(282,1318,"bell",.12),(371,140,"pop",.22),
                                (462,95,"purr",.1),(509,95,"purr",.1),(555,95,"purr",.1)]:
        doc["audio"].append({"frame":frame,"duration":.55 if kind!="purr" else .8,"frequency":freq,"gain":gain,"kind":kind})
    return doc


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="examples/stories/cat-president/story.json")
    args=parser.parse_args()
    print(save(make_story(),args.output))
