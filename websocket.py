import asyncio
import websockets
import json
import time
import random
import math


def randCol():
    red = random.randint(0, 180)
    green = random.randint(0, 180)
    blue = random.randint(0, 180)
    color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    return color

players = []
def addPlayer():
    global players
    high = 0
    for index, p in enumerate(players):
        if players[index]["id"] > high:
            high = players[index]["id"]
    players.append({
        "id": high+1,
        "pos": {
            "x": 400,
            "y": 400,
            "xm": 0,
            "ym": 0
        },
        "r": 0,
        "col": randCol(),
        "upd": time.time(),
        "on": True
    })
def setDir(player, r):
    global players
    for index, p in enumerate(players):
        if int(p["id"]) == int(player):
            dir = math.atan2(r["y"], r["x"])
            players[index]["pos"]["xm"] += math.cos(dir) * 1
            players[index]["pos"]["ym"] += math.sin(dir) * 1
            players[index]["upd"] = time.time()
            players[index]["on"] = True
            return players[index]["pos"]
    return "not found"

async def echo_server(websocket, path):
    async for message in websocket:
        global players
        data = json.loads(message)
        k = data["cmd"]
        v = data["val"]
        ret = {
            "code": 500,
            "val": "error",
            "cmd": k,
            "sent": v,
            "log": ""
        }
        if k == 'setup':
            addPlayer()
            ret["code"] = 200
            ret["val"] = len(players)
        elif k == 'upd':
            if v["dir"] != False:
                ret["log"] = setDir(v["player"], v["dir"])
            ret["code"] = 200
            ret["val"] = players
        elif k == 'setupcheck':
            found = False
            for index, p in enumerate(players):
                if p["id"] == v:
                    found = True
            ret["code"] = 200
            ret["val"] = found
        elif k == 'log':
            ret["code"] = 200
            ret["val"] = v
        elif k == 'leave':
            ret["code"] = 200
            ret["val"] = "left"
        elif k == 'ping':
            ret["code"] = 200
            ret["val"] =  int(time.time() * 1000)
        await websocket.send(json.dumps(ret))

async def loop_function():
    global players
    while True:
        for index, player in enumerate(players):
            if players[index]["pos"]["x"] + players[index]["pos"]["xm"] < 0:
                players[index]["pos"]["xm"] = -players[index]["pos"]["xm"]
            if players[index]["pos"]["x"] + players[index]["pos"]["xm"] > 800:
                players[index]["pos"]["xm"] = -players[index]["pos"]["xm"]
            if players[index]["pos"]["y"] + players[index]["pos"]["ym"] < 0:
                players[index]["pos"]["ym"] = -players[index]["pos"]["ym"]
            if players[index]["pos"]["y"] + players[index]["pos"]["ym"] > 800:
                players[index]["pos"]["ym"] = -players[index]["pos"]["ym"]
            players[index]["pos"]["x"] += players[index]["pos"]["xm"]
            players[index]["pos"]["y"] += players[index]["pos"]["ym"]
            players[index]["pos"]["xm"] *= 0.9
            players[index]["pos"]["ym"] *= 0.9
            if time.time() - players[index]["upd"] > 5:
                players[index]["on"] = False
            if time.time() - players[index]["upd"] > 10:
                players[index]["on"] = "dead"
            if time.time() - players[index]["upd"] > 60*5:
                del players[index]
        await asyncio.sleep(1/60) # 30 times per second

#start_server = websockets.serve(echo_server, '0.0.0.0', 8765)

#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()
#loop_function()

async def main():
    start_server = websockets.serve(echo_server, '0.0.0.0', 8765)
    #asyncio.ensure_future(start_server)
    #asyncio.ensure_future(loop_function())
    await asyncio.gather(start_server, loop_function())

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()