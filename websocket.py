import asyncio
import websockets
import json
import time
import random
import math
import ssl

def randCol():
    red = random.randint(0, 180)
    green = random.randint(0, 180)
    blue = random.randint(0, 180)
    color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
    return color
def dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

players = []
def addPlayer(name):
    global players
    high = 0
    exists = False
    for index, p in enumerate(players):
        if players[index]["id"] > high:
            high = players[index]["id"]
        if players[index]["name"] == name:
            exists = True
    if exists == False:
        players.append({
            "id": high+1,
            "name": name,
            "hp": float(100),
            "pos": {
                "x": random.randint(20, 780),
                "y": random.randint(20, 780),
                "xm": 0,
                "ym": 0
            },
            "r": 0,
            "col": randCol(),
            "upd": time.time(),
            "dt": 0,
            "on": True
        })
        return high+1
    else:
        return False
def setDir(player, r, speed = 0.8):
    global players
    for index, p in enumerate(players):
        if int(p["id"]) == int(player):
            if players[index]["dt"] <= 0:
                dir = math.atan2(r["y"], r["x"])
                players[index]["pos"]["xm"] += math.cos(dir) * speed
                players[index]["pos"]["ym"] += math.sin(dir) * speed
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
            ret["code"] = 200
            ret["val"] = addPlayer(v)
        elif k == 'upd':
            if v["dir"] != False:
                setDir(v["player"], v["dir"])
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
            if players[index]["dt"] > 0:
                players[index]["dt"] -= 1
                players[index]["upd"] = time.time()
            if players[index]["dt"] <= 0:
                if players[index]["on"] == "dead":
                    players[index]["on"] = True
                    players[index]["dt"] = 0
                    players[index]["hp"] = 100
                    players[index]["pos"]["x"] = random.randint(20, 380)
                    players[index]["pos"]["y"] = random.randint(20, 380)
                elif players[index]["hp"] <= 0:
                    players[index]["on"] = "dead"
                    players[index]["dt"] = 60*10
        for index, player in enumerate(players):
            for index2, player2 in enumerate(players):
                if index != index2:
                    if players[index]["on"] == True:
                        if players[index2]["on"] == True:
                            if dist(players[index]["pos"]["x"], players[index]["pos"]["y"], players[index2]["pos"]["x"], players[index2]["pos"]["y"]) <= 40:
                                players[index2]["hp"] -= dist(0, 0, players[index]["pos"]["xm"], players[index]["pos"]["ym"])*2
        for index, player in enumerate(players):
            for index2, player2 in enumerate(players):
                if index != index2:
                    if players[index]["on"] == True:
                        if players[index2]["on"] == True:
                            if dist(players[index]["pos"]["x"], players[index]["pos"]["y"], players[index2]["pos"]["x"], players[index2]["pos"]["y"]) <= 40:
                                r = math.atan2(players[index]["pos"]["y"] - players[index2]["pos"]["y"], players[index]["pos"]["x"] - players[index2]["pos"]["x"])
                                setDir(players[index]["id"], {
                                    "x": math.cos(r)*5,
                                    "y": math.sin(r)*5
                                }, 20)

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
                players[index]["on"] = "dc"
            if time.time() - players[index]["upd"] > 60*2:
                del players[index]
        await asyncio.sleep(1/60) # 30 times per second

#start_server = websockets.serve(echo_server, '0.0.0.0', 8765)

#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()
#loop_function()

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('crt.pem', 'key.pem')
    start_server = websockets.serve(echo_server, '0.0.0.0', 8765, ssl=ssl_context)
    #asyncio.ensure_future(start_server)
    #asyncio.ensure_future(loop_function())
    await asyncio.gather(start_server, loop_function())

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()