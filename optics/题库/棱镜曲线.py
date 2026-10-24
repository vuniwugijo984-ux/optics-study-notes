"""P05：精确逐面折射；仅使用Python标准库。运行后在assets/生成SVG和CSV。"""
from pathlib import Path
import math
import csv

ROOT = Path(__file__).resolve().parent / 'assets'
M = 1.5                         # 棱镜/外界的相对折射率

def deviation(i_deg, a_deg, m=M):
    i, a = map(math.radians, (i_deg, a_deg))
    r1 = math.asin(math.sin(i) / m)
    r2 = a - r1                 # 保留符号；很薄的棱镜可有r2<0
    u = m * math.sin(r2)
    if abs(u) > 1 + 1e-12:
        return None            # 第二面无传播透射光；不连到下一段
    e = math.asin(max(-1, min(1, u)))
    return math.degrees(i + e - a)

def generate():
    ROOT.mkdir(exist_ok=True)
    aa = [3, 5, 8, 10, 12] + [30 + 2.5*j for j in range(13)]
    with (ROOT/'棱镜曲线.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['入射角_deg']+[f'A={a:g}deg_偏向角_deg' for a in aa])
        for j in range(900):
            inc = j/10          # 0至89.9度，90度为掠射边界
            w.writerow([inc]+['' if (d:=deviation(inc,a)) is None else f'{d:.8f}' for a in aa])
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="740" viewBox="0 0 960 740">',
         '<rect width="960" height="740" fill="white"/>',
         '<style>text{font:17px "Microsoft YaHei",sans-serif;fill:#243349}.small{font-size:14px}</style>',
         '<text x="35" y="32">棱镜逐面折射复算（n/n₀=1.5）</text>']
    palettes=['#175bb7','#af4f12','#12845d','#8b3ab0','#ba3157']
    panels=[(55,85,380,520,35,[3,5,8,10,12]),(535,85,380,520,65,[30+2.5*j for j in range(13)])]
    for k,(x,y,w,h,ymax,angles) in enumerate(panels):
        X=lambda v:x+w*v/90
        Y=lambda v:y+h*(1-v/ymax)
        for v in range(0,91,15):
            xx=X(v);s += [f'<path d="M{xx} {y}V{y+h}" stroke="#e2e8ef"/>',f'<text class="small" x="{xx-7}" y="{y+h+23}">{v}</text>']
        step=5 if k==0 else 20
        for v in range(0,ymax+1,step):
            yy=Y(v);s +=[f'<path d="M{x} {yy}H{x+w}" stroke="#e2e8ef"/>',f'<text class="small" x="{x-30}" y="{yy+5}">{v}</text>']
        s += [f'<path d="M{x} {y}V{y+h}H{x+w}" fill="none" stroke="#38465a"/>',
              f'<text x="{x}" y="{y-18}">{"A=3、5、8、10、12°" if k==0 else "A=30°至60°，每2.5°一条"}</text>',
              f'<text x="{x+85}" y="{y+h+53}">入射角 i（度）</text>',f'<text x="{x}" y="{y+h+81}">纵轴：偏向角 δ（度）</text>']
        for j,a in enumerate(angles):
            color=palettes[j%5] if k==0 else f'hsl({220-j*17},65%,40%)'
            path=[]; pen=False
            for ii in range(900):
                inc=ii/10;d=deviation(inc,a)
                if d is None or not 0<=d<=ymax:pen=False;continue
                path.append(f'{"L" if pen else "M"}{X(inc):.2f},{Y(d):.2f}');pen=True
            s += [f'<path d="{" ".join(path)}" fill="none" stroke="{color}" stroke-width="1.8"/>']
            if k==0:
                s +=[f'<path d="M{x} {Y((M-1)*a)}H{x+w}" stroke="{color}" stroke-dasharray="5 5" opacity=".55"/>',
                     f'<text class="small" x="{x+8}" y="{y+22+j*22}" fill="{color}">A={a:g}°</text>']
            else:
                im=math.degrees(math.asin(M*math.sin(math.radians(a/2))));dm=2*im-a
                s +=[f'<circle cx="{X(im)}" cy="{Y(dm)}" r="2.8" fill="{color}"/>']
    s += ['<text class="small" x="55" y="723">左：实线精确值，虚线为(m−1)A；右：圆点为对称光路的最低点，无法透出的区间留空。</text>','</svg>']
    (ROOT/'棱镜曲线.svg').write_text('\n'.join(s),encoding='utf-8')
    # 一个非对称点、一个最低点及一个全反射点，独立于绘图过程检查。
    assert deviation(0,60) is None
    assert abs(deviation(30,60)-47.0958115)<1e-5
    im=math.degrees(math.asin(.75))
    assert abs(deviation(im,60)-(2*im-60))<1e-10
    print('已生成 assets/棱镜曲线.svg、assets/棱镜曲线.csv')

if __name__ == '__main__':
    generate()
