"""Small, dependency-free KiCad S-expression reader/writer."""
import re,json
class S(str): pass
def parse(t):
 tokens=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',t))
 def one(v):
  if v=='(':
   a=[]
   for k in tokens:
    if k==')': return a
    a.append(one(k))
   raise ValueError('unbalanced')
  if v.startswith('"'): return json.loads(v)
  return S(v)
 return one(next(tokens))
def children(n,k): return [v for v in n if isinstance(v,list) and v and v[0]==k]
def child(n,k): return next(iter(children(n,k)),None)
def val(n,k,default=None):
 c=child(n,k)
 return c[1] if c and len(c)>1 else default
def props(n): return {v[1]:v[2] for v in children(n,'property')}
def dump(n,level=0):
 if not isinstance(n,list): return str(n) if isinstance(n,S) else json.dumps(n,ensure_ascii=False)
 if not any(isinstance(x,list) for x in n): return '('+' '.join(dump(x) for x in n)+')'
 out='('
 for i,x in enumerate(n):
  out+= ('\n'+'  '*(level+1) if isinstance(x,list) else (' ' if i else ''))+dump(x,level+1)
 return out+')'
