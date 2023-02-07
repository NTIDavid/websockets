var socket;
window.addEventListener("load", function() {
	ws.setup();
	canvas = document.querySelector("canvas");
	canvas.width = 800;
	canvas.height = 800;
	draw = canvas.getContext("2d");
});
let fps = 60;
let ws = {
	host: "ntigkristianstad.se",
	port: "8765",
	socket: null,
	latencyTimer: null,
	updTimer: null,
	setup: function() {
		ws.socket = new WebSocket("wss://"+ws.host+":"+ws.port);
		ws.socket.addEventListener("open", ws.loaded);
		ws.socket.addEventListener("error", ws.error);
		ws.socket.addEventListener("message", ws.get);
		ws.socket.addEventListener("close", ws.error);
	},
	loaded: function(event) {
		console.log("loaded");
		g.setup();
		clearInterval(ws.latencyTimer);
		ws.latencyTimer = setInterval(ws.ping, 1000);
	},
	ping: function() {
		ws.send("ping", new Date().getTime());
	},
	send: function(key, val = "") {
		ws.socket.send(JSON.stringify({
			cmd: key,
			val: val
		}));
	},
	get: function(event) {
		data = JSON.parse(event.data);
		if(data.cmd === "ping") {
			let up = Number(data.val) - Number(data.sent);
			let total = (new Date().getTime()) - Number(data.sent);
			let down = total-up;
			let playerCount = 0;
			for(let p of g.players) {
				if(p.on === true) {
					playerCount++;
				}
			}
			document.querySelector("#lat").innerText = "Spelare: "+playerCount+"st Latens:"+total+"ms";
		} else if(data.cmd === "setup") {
			if(g.on === false) {
				ajax("setup.php?id="+encodeURIComponent(data.val), "GET", function(data) {
					data = JSON.parse(data);
					player = Number(data);
					clearInterval(ws.updTimer);
					ws.updTimer = setInterval(function() { ws.upd(); }, 1000/fps);
					loop();
				});
			}
		}  else if(data.cmd === "setupcheck") {
			if(data.val === false) {
				window.location.href = "logout.php";
			} else {
				clearInterval(ws.updTimer);
				ws.updTimer = setInterval(function() { ws.upd(); }, 1000/fps);
				loop();
			}
		} else if(data.cmd === "upd") {
			g.players = data.val;
			g.on = true;
		} else {
			console.log("Unknown command: "+data.cmd)
		}
		if(data.log != "") {
			console.log("LOG: "+data.log);
		}
	},
	error: function(event) {
		error.send("Kunde inte ansluta. Ansluter igen...");
		ws.setup();
	},
	upd: function() {
		ws.send("upd", {
			player: player,
			dir: g.move()
		});
	}
};
let error = {
	timer: null,
	send: function(msg, permanent = false) {
		document.querySelector("#error").innerText = msg;
		document.querySelector("#error").classList.add("on");
		if(!permanent) {
			error.timer = setTimeout(error.end, 2000);
		}
	},
	end: function() {
		document.querySelector("#error").classList.remove("on");
	}
}
function dist(x1, y1, x2, y2) {
	return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}
let draw = null;
let d = {
	player: function(x, y, col, hp, dt, id) {
		draw.beginPath();
		draw.moveTo(x, y);
		draw.fillStyle = col;
		draw.arc(x, y, 20, 0, Math.PI*2);
		draw.fill();
		draw.closePath();
		draw.beginPath();
		draw.moveTo(x, y);
		let hpcol = "#0f0";
		if(dt > 60*5) {
			hpcol = "#f00";
		} else if(dt > 60*2.5) {
			hpcol = "#f80";
		} else if(dt > 60) {
			hpcol = "#ff0";
		} else if(dt > 0) {
			hpcol = "#9f0";
		} else {
			if(hp <= 0) {
				hpcol = "#000";
			} else if(hp < 20) {
				hpcol = "#f00";
			} else if(hp < 50) {
				hpcol = "#f80";
			} else if(hp < 75) {
				hpcol = "#ff0";
			} else if(hp <= 100) {
				hpcol = "#0f0";
			}
		}
		draw.fillStyle = hpcol;
		draw.arc(x, y, 6, 0, Math.PI*2);
		draw.fill();
		draw.closePath();
		draw.beginPath();
		draw.font = "10px Verdana";
		draw.fillStyle = "#000";
		draw.textAlign = "center";
		draw.textBaseline = "top";
		draw.fillText(id, x, y+25);
		draw.closePath();
	}
};
let ori = {
	x: 0,
	y: 0
};
window.addEventListener("deviceorientation", function(event) {
	ori.x = event.gamma;
	ori.y = event.beta;
});
let g = {
	on: false,
	players: [],
	keys: [],
	move: function() {
		let m = {
			x: 0,
			y: 0
		};
		if(document.querySelector("#autopilot") != undefined) {
			if(document.querySelector("#autopilot").checked == true) {
				for(let p1 of g.players) {
					if(p1.id == player) {
						for(let p of g.players) {
							if(p.id != p1.id) {
								if(p.on == true) {
									if(Math.random() < 0.4) {
										let r = Math.atan2(p.pos.y - p1.pos.y, p.pos.x - p1.pos.x);
										console.log(r);
										console.log(m);
										m.x = Math.cos(r)*5;
										m.y = Math.sin(r)*5;
										break;
									}
								}
							}
						}
					}
				}
			}
		}
		if ((ori.x !== null) && (ori.y !== null)) {
			if(dist(ori.x, ori.y, 0, 0) > 5) {
				m.x = ori.x;
				m.y = ori.y;
			} else {
				return false;
			}
			//document.querySelector("#log").innerHTML = "x: "+ori.x+"<br>y: "+ori.y;
		} else {
			if(g.keys.indexOf("KeyA") !== -1) {
				m.x -= 5;
			}
			if(g.keys.indexOf("KeyD") !== -1) {
				m.x += 5;
			}
			if(g.keys.indexOf("KeyW") !== -1) {
				m.y -= 5;
			}
			if(g.keys.indexOf("KeyS") !== -1) {
				m.y += 5;
			}
			if(m.x === 0 && m.y === 0) {
				return false;
			}
		}
		return m;
	},
	setup: function() {
		window.addEventListener("keydown", function(event) {
			if(g.keys.indexOf(event.code) === -1) {
				g.keys.push(event.code);
			}
		});
		window.addEventListener("keyup", function(event) {
			if(g.keys.indexOf(event.code) !== -1) {
				g.keys.splice(g.keys.indexOf(event.code), 1);
			}
		});
		if(player === null) {
			ws.send("setup", "sure");
		} else {
			ws.send("setupcheck", player);
		}
	}
};
function loop() {
	draw.clearRect(0, 0, 800, 800);
	if(g.on === true) {
		let iexist = false;
		for(let p of g.players) {
			if(p.id == player) {
				iexist = true;
			}
		}
		if(iexist === false) {
			g.on = false;
			//alert("Du blev kickad pga inaktivitet");
			//window.location.href = "logout.php";
			//ws.send("setup", "sure");
		}
		for(let p of g.players) {
			if(p.on === true) {
				d.player(p.pos.x, p.pos.y, p.col, p.hp, p.dt, p.id);
			} else if(p.on === false) {
				d.player(p.pos.x, p.pos.y, "rgba(0,0,0,0.2)", p.hp, p.dt, p.id);
			} else if(p.on === "dead") {
				d.player(p.pos.x, p.pos.y, "rgba(150,150,150,1)", p.hp, p.dt, p.id);
			} else if(p.on === "dc") {
				d.player(p.pos.x, p.pos.y, "rgba(255,0,0,0.2)", p.hp, p.dt, p.id);
			} else {
				d.player(p.pos.x, p.pos.y, "rgba(0,0,0,0.2)", p.hp, p.dt, p.id);
			}
		}
	}
	window.requestAnimationFrame(loop);
}