#!/usr/bin/env python3
"""web.py - FastAPI web UI for chess-cli."""
import sys
import os
import threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from board import Board, Color

app = FastAPI()
class GameState:
    def __init__(self):
        self.reset()
    def reset(self):
        self.board = Board()
        self.history = []
    def turn(self):
        return "w" if self.board.turn == Color.WHITE else "b"


_state = GameState()
_lock = threading.Lock()


class MoveIn(BaseModel):
    src: str
    dst: str


def _alg_to_pos(alg):
    return (8 - int(alg[1]), ord(alg[0]) - ord('a'))


@app.get("/api/state")
def get_state():
    with _lock:
        return {"fen": _state.board.to_fen(), "history": _state.history, "turn": _state.turn()}


@app.post("/api/move")
def do_move(m: MoveIn):
    with _lock:
        try:
            _state.board.move_piece(_alg_to_pos(m.src), _alg_to_pos(m.dst))
            _state.history.append(m.src + m.dst)
            return {"ok": True, "fen": _state.board.to_fen(), "history": _state.history, "turn": _state.turn()}
        except Exception as e:
            return {"ok": False, "error": str(e)}


@app.post("/api/reset")
def do_reset():
    with _lock:
        _state.reset()
        return {"ok": True, "fen": _state.board.to_fen(), "history": [], "turn": _state.turn()}


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chess</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#302e2b;color:#e8e6e3;font-family:-apple-system,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px}
.app{display:flex;gap:20px;flex-wrap:wrap;justify-content:center;align-items:flex-start}
.board-wrap{background:#262421;padding:16px;border-radius:12px}
.banner{background:#5c4a1a;color:#ffd966;padding:6px 12px;border-radius:6px;font-size:12px;margin-bottom:12px;text-align:center}
.board{display:grid;grid-template-columns:repeat(8,1fr);grid-template-rows:repeat(8,1fr);width:min(90vw,560px);height:min(90vw,560px);border-radius:6px;overflow:hidden}
.sq{display:flex;align-items:center;justify-content:center;font-size:min(10vw,60px);cursor:pointer;user-select:none}
.sq.light{background:#f0d9b5}
.sq.dark{background:#b58863}
.sq.sel{box-shadow:inset 0 0 0 4px #7fa650}
.sq.last{background:#cdd26a!important}
.w{color:#fff;text-shadow:0 0 1px #000,0 1px 1px #000}
.b{color:#1a1a1a;text-shadow:0 0 1px #fff}
.side{background:#262421;padding:16px;border-radius:12px;min-width:200px;max-width:280px;flex:1}
.side h2{font-size:13px;color:#8a8578;text-transform:uppercase;margin-bottom:10px}
.hist{list-style:none;font-family:monospace;font-size:13px;max-height:400px;overflow-y:auto}
.hist li{padding:4px 8px;border-radius:4px}
.hist li:nth-child(odd){background:rgba(255,255,255,0.03)}
.err{color:#e45b5b;font-size:12px;margin-top:8px;min-height:18px}
.btn{width:100%;padding:10px;border:none;background:#7fa650;color:#000;font-weight:600;border-radius:6px;cursor:pointer;margin-top:10px;font-size:14px}
.btn:hover{filter:brightness(1.1)}
</style>
</head>
<body>
<div class="app">
  <div class="board-wrap">
    <div class="banner">Prototype</div>
    <div class="board" id="board"></div>
  </div>
  <div class="side">
    <h2>Moves</h2>
    <ol class="hist" id="hist"></ol>
    <div class="err" id="err"></div>
    <button class="btn" onclick="reset()">Reset</button>
  </div>
</div>
<script>
const G={K:'\u2654',Q:'\u2655',R:'\u2656',B:'\u2657',N:'\u2658',P:'\u2659',k:'\u265A',q:'\u265B',r:'\u265C',b:'\u265D',n:'\u265E',p:'\u265F'};
let fen='',history=[],turn='w',selected=null,last=null;
function pos(r,c){return String.fromCharCode(97+c)+(8-r)}
function render(){
  const el=document.getElementById('board');el.innerHTML='';
  const rows=fen.split(' ')[0].split('/');
  for(let r=0;r<8;r++){let c=0;
    for(const ch of rows[r]){
      if(/\d/.test(ch)){for(let i=0;i<+ch;i++){mk(r,c,null);c++}}
      else{mk(r,c,ch);c++}
    }
  }
  const h=document.getElementById('hist');h.innerHTML='';
  history.forEach(m=>{const li=document.createElement('li');li.textContent=m;h.appendChild(li)});
}
function mk(r,c,p){
  const el=document.getElementById('board');
  const sq=document.createElement('div');
  sq.className='sq '+((r+c)%2===0?'light':'dark');
  if(selected&&selected.r===r&&selected.c===c)sq.classList.add('sel');
  if(last&&((last.fr===r&&last.fc===c)||(last.tr===r&&last.tc===c)))sq.classList.add('last');
  if(p){const sp=document.createElement('span');sp.className=p===p.toUpperCase()?'w':'b';sp.textContent=G[p]||'';sq.appendChild(sp)}
  sq.onclick=()=>click(r,c);el.appendChild(sq);
}
async function click(r,c){
  document.getElementById('err').textContent='';
  if(!selected){selected={r,c};render();return}
  if(selected.r===r&&selected.c===c){selected=null;render();return}
  const src=pos(selected.r,selected.c),dst=pos(r,c);const from=selected;selected=null;
  const res=await fetch('/api/move',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({src,dst})});
  const d=await res.json();
  if(d.ok){fen=d.fen;history=d.history;turn=d.turn;last={fr:from.r,fc:from.c,tr:r,tc:c}}
  else{document.getElementById('err').textContent=d.error||'illegal move'}
  render();
}
async function load(){const res=await fetch('/api/state');const d=await res.json();fen=d.fen;history=d.history;turn=d.turn;render()}
async function reset(){const res=await fetch('/api/reset',{method:'POST'});const d=await res.json();if(d.ok){fen=d.fen;history=[];turn='w';selected=null;last=null;render()}}
load();
</script>
</body>
</html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
