# canvas_components.py — Canvas Design & Algorithmic Art
# Renders HTML5 canvas elements inside Streamlit via components.v1.html()

from __future__ import annotations
import json
from typing import List

import streamlit.components.v1 as components


# ---------------------------------------------------------------------------
# Particle Network — animated algorithmic art header banner
# ---------------------------------------------------------------------------

def render_particle_network(
    palette: List[str],
    height: int = 130,
    n_particles: int = 55,
    key: str = "particle_net",
) -> None:
    """
    Renders an animated particle-network canvas as an art banner.

    Parameters
    ----------
    palette   : list of hex colour strings from the active theme
    height    : canvas height in px
    n_particles : number of floating nodes
    key       : unique Streamlit component key
    """
    colors_js = json.dumps(palette)
    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ overflow:hidden; background:{palette[-1]}; }}
  canvas {{ display:block; width:100%; height:{height}px; }}
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
(function(){{
  const COLORS = {colors_js};
  const N = {n_particles};
  const canvas = document.getElementById('c');
  const ctx = canvas.getContext('2d');
  let W, H, particles=[];

  function resize(){{
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = {height};
  }}

  function rand(a,b){{ return a + Math.random()*(b-a); }}

  function initParticles(){{
    particles = [];
    for(let i=0;i<N;i++){{
      particles.push({{
        x: rand(0,W), y: rand(0,H),
        vx: rand(-0.5,0.5), vy: rand(-0.35,0.35),
        r: rand(2.5,5),
        color: COLORS[Math.floor(Math.random()*3)],
        alpha: rand(0.55,0.95),
      }});
    }}
  }}

  const LINK_DIST = 110;

  function draw(){{
    ctx.clearRect(0,0,W,H);

    // subtle gradient background
    const grd = ctx.createLinearGradient(0,0,W,H);
    grd.addColorStop(0, COLORS[3] || '#1e293b');
    grd.addColorStop(1, COLORS[4] || '#0f172a');
    ctx.fillStyle = grd;
    ctx.fillRect(0,0,W,H);

    // links
    for(let i=0;i<N;i++){{
      for(let j=i+1;j<N;j++){{
        const dx=particles[i].x-particles[j].x;
        const dy=particles[i].y-particles[j].y;
        const d=Math.sqrt(dx*dx+dy*dy);
        if(d<LINK_DIST){{
          const alpha=0.22*(1-d/LINK_DIST);
          ctx.beginPath();
          ctx.strokeStyle=`rgba(255,255,255,${{alpha}})`;
          ctx.lineWidth=0.8;
          ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);
          ctx.stroke();
        }}
      }}
    }}

    // nodes
    for(const p of particles){{
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=p.color;
      ctx.globalAlpha=p.alpha;
      ctx.fill();
      ctx.globalAlpha=1;
    }}
  }}

  function update(){{
    for(const p of particles){{
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<-10) p.x=W+10;
      if(p.x>W+10) p.x=-10;
      if(p.y<-10) p.y=H+10;
      if(p.y>H+10) p.y=-10;
    }}
  }}

  function loop(){{
    update(); draw();
    requestAnimationFrame(loop);
  }}

  resize();
  initParticles();
  loop();
  window.addEventListener('resize', ()=>{{ resize(); initParticles(); }});
}})();
</script>
</body>
</html>
"""
    components.html(html, height=height, scrolling=False)


# ---------------------------------------------------------------------------
# Geometric Wave — decorative section divider
# ---------------------------------------------------------------------------

def render_wave_divider(
    color1: str = "#3b82f6",
    color2: str = "#06b6d4",
    height: int = 56,
    key: str = "wave_div",
) -> None:
    """Renders a smooth animated sine-wave divider between sections."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; }}
  body {{ overflow:hidden; }}
  canvas {{ display:block; width:100%; height:{height}px; }}
</style>
</head>
<body>
<canvas id="w"></canvas>
<script>
(function(){{
  const canvas = document.getElementById('w');
  const ctx = canvas.getContext('2d');
  let W, H={height}, t=0;

  function resize(){{
    W = canvas.width = canvas.offsetWidth;
    canvas.height = H;
  }}

  function draw(){{
    ctx.clearRect(0,0,W,H);
    for(let layer=0;layer<2;layer++){{
      const amp = layer===0 ? 10 : 7;
      const freq = layer===0 ? 0.018 : 0.025;
      const speed = layer===0 ? 0.04 : 0.06;
      const yBase = H*0.55 + layer*6;
      const alpha = layer===0 ? 0.55 : 0.35;
      const color = layer===0 ? '{color1}' : '{color2}';

      ctx.beginPath();
      ctx.moveTo(0,H);
      for(let x=0;x<=W;x+=2){{
        const y = yBase + Math.sin(x*freq + t + layer*1.2)*amp;
        ctx.lineTo(x,y);
      }}
      ctx.lineTo(W,H);
      ctx.closePath();
      const grd = ctx.createLinearGradient(0,0,W,0);
      grd.addColorStop(0, color+'99');
      grd.addColorStop(0.5, color+'cc');
      grd.addColorStop(1, '{color2}'+'88');
      ctx.fillStyle = grd;
      ctx.globalAlpha = alpha;
      ctx.fill();
      ctx.globalAlpha = 1;
    }}
    t += 0.035;
    requestAnimationFrame(draw);
  }}

  resize();
  draw();
  window.addEventListener('resize', resize);
}})();
</script>
</body>
</html>
"""
    components.html(html, height=height, scrolling=False)


# ---------------------------------------------------------------------------
# Donut Ring — canvas KPI ring for a single metric
# ---------------------------------------------------------------------------

def render_kpi_ring(
    value: float,
    total: float,
    label: str,
    accent: str = "#3b82f6",
    bg_color: str = "#f0f4ff",
    size: int = 140,
    key: str = "kpi_ring",
) -> None:
    """
    Renders an animated arc/ring widget showing value/total ratio.

    Parameters
    ----------
    value     : current value
    total     : maximum / reference value
    label     : text below the ring
    accent    : arc colour (hex)
    bg_color  : background colour
    size      : widget width/height in px
    key       : unique component key
    """
    pct = max(0.0, min(1.0, value / total if total else 0))
    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; }}
  body {{ background:{bg_color}; display:flex; justify-content:center; align-items:center; height:{size}px; }}
  canvas {{ display:block; }}
</style>
</head>
<body>
<canvas id="ring" width="{size}" height="{size}"></canvas>
<script>
(function(){{
  const canvas = document.getElementById('ring');
  const ctx = canvas.getContext('2d');
  const cx = {size}/2, cy = {size}/2;
  const R = {size}/2 - 14;
  const TARGET = {pct};
  const ACCENT = '{accent}';
  const VALUE_LABEL = '{int(value):,}';
  const TEXT_LABEL = '{label}';
  let current = 0;

  function draw(prog){{
    ctx.clearRect(0,0,{size},{size});

    // track ring
    ctx.beginPath();
    ctx.arc(cx,cy,R, -Math.PI/2, Math.PI*3/2);
    ctx.strokeStyle='rgba(0,0,0,0.08)';
    ctx.lineWidth=10;
    ctx.lineCap='round';
    ctx.stroke();

    // value arc
    const end = -Math.PI/2 + prog * Math.PI*2;
    ctx.beginPath();
    ctx.arc(cx,cy,R,-Math.PI/2,end);
    ctx.strokeStyle=ACCENT;
    ctx.lineWidth=10;
    ctx.lineCap='round';
    ctx.stroke();

    // value text
    ctx.fillStyle=ACCENT;
    ctx.font='bold {int(size*0.17)}px system-ui, sans-serif';
    ctx.textAlign='center';
    ctx.textBaseline='middle';
    ctx.fillText(VALUE_LABEL, cx, cy-7);

    // label text
    ctx.fillStyle='rgba(0,0,0,0.45)';
    ctx.font='{int(size*0.09)}px system-ui, sans-serif';
    ctx.fillText(TEXT_LABEL, cx, cy+14);
  }}

  function animate(){{
    if(current < TARGET){{
      current = Math.min(current + 0.022, TARGET);
      draw(current);
      requestAnimationFrame(animate);
    }} else {{
      draw(TARGET);
    }}
  }}
  animate();
}})();
</script>
</body>
</html>
"""
    components.html(html, height=size, scrolling=False)


# ---------------------------------------------------------------------------
# Algorithmic Mosaic — generative tile art for section backgrounds
# ---------------------------------------------------------------------------

def render_mosaic_art(
    palette: List[str],
    height: int = 80,
    key: str = "mosaic_art",
) -> None:
    """
    Renders a slow-shifting geometric mosaic using Voronoi-style tiles.
    """
    colors_js = json.dumps(palette[:4])
    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; }}
  body {{ overflow:hidden; }}
  canvas {{ display:block; width:100%; height:{height}px; }}
</style>
</head>
<body>
<canvas id="m"></canvas>
<script>
(function(){{
  const COLORS = {colors_js};
  const canvas = document.getElementById('m');
  const ctx = canvas.getContext('2d');
  let W, H={height}, t=0;
  const SEEDS = 18;
  let seeds=[];

  function resize(){{
    W = canvas.width = canvas.offsetWidth;
    canvas.height = H;
    seeds = Array.from({{length:SEEDS}},()=>([
      Math.random()*W, Math.random()*H,
      (Math.random()-0.5)*0.4, (Math.random()-0.5)*0.3,
      COLORS[Math.floor(Math.random()*COLORS.length)]
    ]));
  }}

  function draw(){{
    const img = ctx.createImageData(W,H);
    const d=img.data;
    for(let y=0;y<H;y+=2){{
      for(let x=0;x<W;x+=2){{
        let minD=1e9, closest=0;
        for(let s=0;s<seeds.length;s++){{
          const dx=x-seeds[s][0], dy=y-seeds[s][1];
          const dist=dx*dx+dy*dy;
          if(dist<minD){{ minD=dist; closest=s; }}
        }}
        const hex=seeds[closest][4];
        const r=parseInt(hex.slice(1,3),16);
        const g=parseInt(hex.slice(3,5),16);
        const b=parseInt(hex.slice(5,7),16);
        const alpha=Math.floor(180+60*(minD/(W*H)*SEEDS));
        for(let dy2=0;dy2<2&&y+dy2<H;dy2++){{
          for(let dx2=0;dx2<2&&x+dx2<W;dx2++){{
            const idx=((y+dy2)*W+(x+dx2))*4;
            d[idx]=r; d[idx+1]=g; d[idx+2]=b; d[idx+3]=alpha;
          }}
        }}
      }}
    }}
    ctx.putImageData(img,0,0);
  }}

  function update(){{
    for(const s of seeds){{
      s[0]+=s[2]; s[1]+=s[3];
      if(s[0]<0||s[0]>W) s[2]*=-1;
      if(s[1]<0||s[1]>H) s[3]*=-1;
    }}
  }}

  let frame=0;
  function loop(){{
    if(frame%3===0){{ update(); draw(); }}
    frame++;
    requestAnimationFrame(loop);
  }}

  resize();
  loop();
  window.addEventListener('resize',()=>{{ resize(); }});
}})();
</script>
</body>
</html>
"""
    components.html(html, height=height, scrolling=False)
