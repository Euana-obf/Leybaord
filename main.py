from flask import Flask, render_template_string, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "data.json"), "r", encoding="utf-8") as f:
    DATA = json.load(f)

WORDS = DATA["words"]
SENTENCES = DATA["sentences"]

HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>욕 타자 연습</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
    background: #0d0d0d;
    color: #e0e0e0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 12px;
    padding-bottom: 48px;
  }
  h1 {
    font-size: 1.35rem;
    margin: 10px 0 2px;
    color: #ff4444;
    letter-spacing: -0.5px;
  }
  .sub {
    font-size: 0.72rem;
    color: #555;
    margin-bottom: 12px;
  }
  .mode-row {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
    width: 100%;
    max-width: 420px;
  }
  .mode-btn {
    flex: 1;
    padding: 10px;
    font-size: 0.9rem;
    border: 2px solid #333;
    border-radius: 8px;
    background: #1a1a1a;
    color: #888;
    cursor: pointer;
    font-weight: 600;
  }
  .mode-btn.active {
    border-color: #ff4444;
    background: #2a1212;
    color: #ff6666;
  }
  .stats {
    display: flex;
    gap: 14px;
    margin-bottom: 14px;
    font-size: 0.82rem;
    color: #777;
  }
  .stats span { color: #ff6666; font-weight: 600; }
  .word-box {
    width: 100%;
    max-width: 420px;
    background: #1a1a1a;
    border: 2px solid #333;
    border-radius: 12px;
    padding: 22px 14px;
    text-align: center;
    margin-bottom: 14px;
    min-height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  #target {
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    word-break: keep-all;
    line-height: 1.45;
    white-space: pre-wrap;
  }
  .input-wrap {
    width: 100%;
    max-width: 420px;
  }
  #input {
    width: 100%;
    font-size: 1.2rem;
    padding: 13px 14px;
    border: 2px solid #444;
    border-radius: 10px;
    background: #111;
    color: #fff;
    outline: none;
    text-align: center;
    -webkit-appearance: none;
  }
  #input:focus { border-color: #ff4444; }
  #input.correct { border-color: #22c55e; background: #0a1f0a; }
  #input.wrong { border-color: #ef4444; background: #1f0a0a; }
  .progress {
    width: 100%;
    max-width: 420px;
    height: 5px;
    background: #222;
    border-radius: 3px;
    margin-top: 10px;
    overflow: hidden;
  }
  .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #ff2222, #ff6666);
    width: 0%;
    transition: width 0.12s ease;
  }
  .btn-row {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    width: 100%;
    max-width: 420px;
  }
  button.action {
    flex: 1;
    padding: 11px;
    font-size: 0.9rem;
    border: none;
    border-radius: 8px;
    background: #2a2a2a;
    color: #bbb;
    cursor: pointer;
    font-weight: 600;
  }
  button.action:active { background: #3a3a3a; }
  #skip { background: #3a1a1a; color: #ff8888; }
  #reset { background: #1a2a3a; color: #88aaff; }
  .msg {
    margin-top: 12px;
    font-size: 0.88rem;
    height: 20px;
    color: #22c55e;
  }
  .msg.err { color: #ef4444; }
  .count {
    font-size: 0.7rem;
    color: #444;
    margin-top: 8px;
  }
  footer {
    margin-top: auto;
    padding-top: 20px;
    font-size: 0.68rem;
    color: #333;
  }
</style>
</head>
<body>
  <h1>욕 타자 연습</h1>
  <div class="sub">패드립 · 성적 표현 · 쌍욕</div>

  <div class="mode-row">
    <button class="mode-btn active" id="btnWord" data-mode="word">단어</button>
    <button class="mode-btn" id="btnSentence" data-mode="sentence">문장</button>
  </div>

  <div class="stats">
    <div>정답 <span id="score">0</span></div>
    <div>연속 <span id="streak">0</span></div>
    <div>최고 <span id="best">0</span></div>
  </div>

  <div class="word-box">
    <div id="target">로딩중...</div>
  </div>

  <div class="input-wrap">
    <input id="input" type="text" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" placeholder="여기 입력" enterkeyhint="done">
  </div>
  <div class="progress"><div class="progress-bar" id="bar"></div></div>
  <div class="msg" id="msg"></div>
  <div class="count" id="count"></div>

  <div class="btn-row">
    <button class="action" id="skip">스킵</button>
    <button class="action" id="reset">리셋</button>
  </div>

  <footer>iPhone 최적화 · 렌더 배포용</footer>

<script>
const WORDS = {{ words | tojson }}, SENTENCES = {{ sentences | tojson }};
let mode=localStorage.getItem("mode")||"word", pool=mode==="sentence"?SENTENCES:WORDS;
let current="",score=0,streak=0,best=+(localStorage.getItem("best_"+mode)||0),composing=false,timer=null;
const $=id=>document.getElementById(id);
function update(){ $("count").textContent=`풀: ${pool.length}개`; }
function next(){clearTimeout(timer);timer=null;current=pool[Math.floor(Math.random()*pool.length)]||"";$("target").textContent=current;$("input").value="";$("input").className="";$("msg").textContent="";$("msg").className="msg";$("bar").style.width="0%";$("input").focus();}
function setMode(m){mode=m;localStorage.setItem("mode",m);pool=m==="sentence"?SENTENCES:WORDS;best=+(localStorage.getItem("best_"+mode)||0);$("best").textContent=best;score=streak=0;$("score").textContent=0;$("streak").textContent=0;$("btnWord").classList.toggle("active",m==="word");$("btnSentence").classList.toggle("active",m==="sentence");update();next();}
function check(){let v=$("input").value;if(composing||$("input").isComposing)return;if(v===current){$("input").className="correct";$("msg").textContent="정답!";score++;streak++;if(streak>best){best=streak;localStorage.setItem("best_"+mode,best);$("best").textContent=best;}$("score").textContent=score;$("streak").textContent=streak;if(!timer)timer=setTimeout(next,320);}else if(current.startsWith(v)){$("input").className="";$("bar").style.width=(v.length/current.length*100)+"%";$("msg").textContent="";}else{$("input").className="wrong";streak=0;$("streak").textContent=0;$("msg").textContent="틀림";$("msg").className="msg err";}}
$("btnWord").onclick=()=>setMode("word");$("btnSentence").onclick=()=>setMode("sentence");
$("input").addEventListener("compositionstart",()=>composing=true);$("input").addEventListener("compositionend",()=>{composing=false;check();});$("input").addEventListener("input",check);
$("input").addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();if($("input").value===current)next();}});
$("skip").onclick=()=>{streak=0;$("streak").textContent=0;next();};$("reset").onclick=()=>{score=streak=0;$("score").textContent=$("streak").textContent=0;next();};
$("best").textContent=best;$("btnWord").classList.toggle("active",mode==="word");$("btnSentence").classList.toggle("active",mode==="sentence");update();next();document.body.addEventListener("touchstart",()=> $("input").focus(),{passive:true});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, words=WORDS, sentences=SENTENCES)

@app.route("/api/data")
def api_data():
    return jsonify(DATA)

@app.route("/data.json")
def serve_json():
    return send_from_directory(BASE, "data.json")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
