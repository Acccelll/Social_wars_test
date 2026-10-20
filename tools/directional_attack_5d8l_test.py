#!/usr/bin/env python3
"""Offline unit tests of 5D.8L placement and attack direction declaration."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from directional_attack_5d8l import DIRECTIONS, placement_at, static_analysis


def test_place_and_remove():
    e=[{"frame":1,"op":"place","depth":1,"character_id":13},
       {"frame":2,"op":"place","depth":1,"resolved_character_id":13},
       {"frame":3,"op":"remove","depth":1},
       {"frame":4,"op":"place","depth":1,"character_id":18}]
    assert [placement_at(e,x,1) for x in range(1,5)]==[13,13,None,18]


def test_root_binding_and_no_projectile_inference():
    root=[{"frame":v,"op":"place","depth":1,"character_id":cid}
          for _,v,cid,_ in DIRECTIONS]
    main={"character_id":1092,
          "declared_frames":50,
          "frame_labels":[{"name":"ATAQUE","frame":11}],
          "frame_events":root}
    sprites=[main]
    names={}
    for n,(name,frame,cid,label) in enumerate(DIRECTIONS):
        names[str(cid)]=label
        sprites.append({"character_id":cid,"declared_frames":60,
          "parse_warnings":0,"frame_events":[
            {"frame":1,"op":"place","depth":n+1,"character_id":7},
            {"frame":11,"op":"place","depth":n+2,"character_id":100+n}],
          "place_events":2,"remove_events":0,"child_character_ids":[7,100+n]})
    parsed=static_analysis({"sprites":sprites,"symbol_names":names})
    assert len(parsed["directions"])==5
    assert parsed["shared_direct_child_ids"]==[7]
    for i,row in enumerate(parsed["directions"]):
        assert row["projectile_id_confirmed"] is None
        assert row["direction_specific_direct_child_ids"]==[100+i]
        assert row["main_attack_frame"]==11+i
        assert row["display_list_per_frame"][11]["placements"]==1


if __name__=="__main__":
    test_place_and_remove()
    test_root_binding_and_no_projectile_inference()
    print("DIRECTIONAL_ATTACK_TEST_5D8L PASS: 2 offline tests")
