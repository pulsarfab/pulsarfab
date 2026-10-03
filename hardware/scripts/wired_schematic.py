"""Connected schematic authoring helpers; source files remain editable in KiCad."""
from kicad_sexp import *
from pathlib import Path
import copy,uuid,math,json,os
BASE=Path(__file__).resolve().parents[2]
PROJECT='pulsardewhub'
OUT=BASE/'hardware'/PROJECT
LIB=Path(os.environ.get('KICAD_SYMBOL_DIR','/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'))
rootid='e52b73dc-d0d2-4d83-a7ea-224e97decc28'
def uid(name): return str(uuid.uuid5(uuid.UUID(rootid),name))
def q(v):return json.dumps(str(v),ensure_ascii=False)
def n(v):return S(str(round(float(v),4)))
def node(k,*args):return [S(k),*args]
def xy(p):return f'{p[0]:.4f} {p[1]:.4f}'
def snap(v):return round(round(v/1.27)*1.27,4)
def pt(x,y):return (snap(x),snap(y))
libs={}
def symbol(libid):
 if libid in libs:return copy.deepcopy(libs[libid])
 lib,name=libid.split(':')
 f=BASE/'hardware/lib/symbols'/ (lib+'.kicad_sym') if lib.startswith('pulsarfab') else LIB/(lib+'.kicad_sym')
 d=parse(f.read_text()); c=copy.deepcopy(next(s for s in children(d,'symbol') if s[1]==name))
 parent=val(c,'extends')
 if parent:
  merged=symbol(lib+':'+parent)
  merged[1]=name
  for s in children(merged,'symbol'):s[1]=s[1].replace(parent+'_',name+'_')
  for p in children(c,'property'):
   merged[:]=[v for v in merged if not (isinstance(v,list) and v[0]=='property' and v[1]==p[1])]
   merged.append(p)
  c=merged
 c[1]=libid; libs[libid]=c
 return copy.deepcopy(c)

class Sheet:
 def __init__(self,name,title,paths,paper='A4'):
  self.name=name; self.paths=paths; self.items=[]; self.cache={}; self.pins={}; self.symbols={}; self.wires=[]; self.joints=set()
  self.id=rootid if name==PROJECT else uid('file:'+name)
  self.header=f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid "{self.id}") (paper "{paper}")\n(title_block (title {q("PulsarDew Hub - "+title)}) (date "2026-10-03") (rev "0.2-draft") (company "PulsarFab"))'
 def add(self,s):self.items.append(s)
 def text(self,t,x,y,size=1.27):self.add(f'(text {q(t)} (at {xy(pt(x,y))} 0) (effects (font (size {size} {size})) (justify left top)) (uuid "{uid(self.name+":text:"+t)}"))')
 def wire(self,*points):
  for a,b in zip(points,points[1:]):
   a=tuple(round(v,4) for v in a); b=tuple(round(v,4) for v in b)
   if a==b:continue
   assert a[0]==b[0] or a[1]==b[1],(self.name,a,b)
   self.wires.append((a,b))
 def join(self,p):self.joints.add(tuple(p))
 def label(self,name,p,angle=0,hier=None):
  typ='hierarchical_label' if hier else 'label'
  shape=f'(shape {hier})' if hier else ''
  self.add(f'({typ} {q(name)} {shape} (at {xy(p)} {angle}) (effects (font (size 1.27 1.27)) (justify {"left" if angle==0 else "right"} bottom)) (uuid "{uid(self.name+typ+name+str(p))}"))')
  return p
 def port(self,name,x,y,direction='input',right=False):return self.label(name,pt(x,y),0 if not right else 180,direction)
 def nc(self,p):self.add(f'(no_connect (at {xy(p)}) (uuid "{uid(self.name+"nc"+str(p))}"))')
 def comp(self,ref,libid,x,y,angle=0,value=None,fp=None,orig=None,refs=None,fields=None):
  c=copy.deepcopy(orig) if orig else [S('symbol')]
  props0=props(c); sym=symbol(libid); self.cache[libid]=sym
  x,y=pt(x,y); sid=val(c,'uuid',uid(self.name+ref)); value=value or props0.get('Value') or props(sym).get('Value',libid.split(':')[1])
  vals={**props0,'Reference':ref,'Value':value,'Footprint':fp or props0.get('Footprint') or props(sym).get('Footprint',''),'Datasheet':props(sym).get('Datasheet','')}
  vals.update(fields or {})
  power=ref.startswith('#')
  c=[S('symbol'),node('lib_id',libid),node('at',n(x),n(y),n(angle)),node('unit',S('1')),node('in_bom',S('no' if power else 'yes')),node('on_board',S('no' if power else 'yes')),node('dnp',S('no')),node('uuid',sid)]
  # Put visible properties above wide ICs, beside vertical passives, above horizontal passives.
  if ref.startswith('U') or libid.startswith('Connector:'):
   ys=[float(child(p,'at')[2]) for u in children(sym,'symbol') for p in children(u,'pin')]
   top=y-max(ys or [5])-8.89
   # Leave the vertical supply label clear on ICs with top-facing pins.
   xx=x+15.24 if any(float(child(p,'at')[1])==0 and float(child(p,'at')[2])>0 for u in children(sym,'symbol') for p in children(u,'pin')) else x
   positions=[(xx,top),(xx,top+2.54)]; justify=None
  elif angle in (90,270) and ref.startswith('D'):
   positions=[(x+5.08,y-2.54),(x+5.08,y+2.54)];justify='left'
  elif angle in (90,270,180) and not ref.startswith('J'):
   positions=[(x,y-6.35),(x,y-3.81)];justify=None
  else:positions=[(x+5.08,y-2.54),(x+5.08,y+2.54)];justify='left'
  for key,v in vals.items():
   visible=key in ('Reference','Value') and not power
   pp=positions[0 if key=='Reference' else 1] if visible else (x,y)
   effects=node('effects',node('font',node('size',S('1.27'),S('1.27'))))
   if visible and justify:effects.append(node('justify',S(justify)))
   if not visible:effects.append(node('hide',S('yes')))
   c.append(node('property',key,v,node('at',n(pp[0]),n(pp[1]),n(angle%180)),effects))
  pins={}; a=math.radians(angle)
  for u in children(sym,'symbol'):
   for pin in children(u,'pin'):
    px,py=map(float,child(pin,'at')[1:3]); num=val(pin,'number')
    pins[num]=(round(x+px*math.cos(a)-py*math.sin(a),4),round(y-px*math.sin(a)-py*math.cos(a),4))
    c.append(node('pin',num,node('uuid',uid(sid+num))))
  projects=node('project',PROJECT)
  for i,path in enumerate(self.paths):projects.append(node('path',path,node('reference',refs[i] if refs else ref),node('unit',S('1'))))
  c.append(node('instances',projects));self.items.append(c); self.pins[ref]=pins; self.symbols[ref]=c
  return pins
 def pinlabel(self,ref,num,name,length=7.62,side='left'):
  p=self.pins[ref][str(num)];end=(p[0]+(-length if side=='left' else length),p[1]);self.wire(p,end);self.label(name,end,0 if side=='right' else 180);return end
 def flag(self,ref,p):self.comp(ref,'power:PWR_FLAG',*p)
 def finish(self):
  # Split T-junctions; every real branch is visible. Crossings without a node stay separate.
  endpoints={p for w in self.wires for p in w}|self.joints|{p for pins in self.pins.values() for p in pins.values()}
  segs=set()
  for a,b in self.wires:
   pts=[p for p in endpoints if (a[0]==b[0]==p[0] and min(a[1],b[1])<=p[1]<=max(a[1],b[1])) or (a[1]==b[1]==p[1] and min(a[0],b[0])<=p[0]<=max(a[0],b[0]))]
   pts.sort()
   segs.update(zip(pts,pts[1:]))
  degree={}
  for a,b in sorted(segs):
   self.add(f'(wire (pts (xy {xy(a)}) (xy {xy(b)})) (stroke (width 0) (type default)) (uuid "{uid(self.name+str(a)+str(b))}"))')
   for p in (a,b):degree[p]=degree.get(p,0)+1
  for p,k in degree.items():
   if k>2:self.add(f'(junction (at {xy(p)}) (diameter 0) (color 0 0 0 0) (uuid "{uid(self.name+"j"+str(p))}"))')
  body='\n'.join(dump(v) if isinstance(v,list) else v for v in self.items)
  cache='\n'.join(dump(v) for v in self.cache.values())
  inst='(sheet_instances (path "/" (page "1")))' if self.name==PROJECT else ''
  (OUT/(self.name+'.kicad_sch')).write_text(self.header+'\n(lib_symbols\n'+cache+')\n'+body+'\n'+inst+'\n(embedded_fonts no)\n)\n')
