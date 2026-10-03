#!/usr/bin/env python3
"""Author the connected PulsarDew Hub prototype schematic.

Explicit regeneration only: running this replaces this project's schematic files.
It does not modify the original PulsarDew or any PCB. See the project README for
ratings, datasheet sources, assembly variants and outstanding release work.
"""
from wired_schematic import *

RFP='Resistor_SMD:R_0603_1608Metric'
CFP='Capacitor_SMD:C_0603_1608Metric'
SOT6='Package_TO_SOT_SMD:SOT-23-6'
CATALOG=OUT/'parts-catalog.json'
catalog=json.loads(CATALOG.read_text()) if CATALOG.exists() else {}

def fields(code='',mpn='',manufacturer='',**extra):
 d=catalog.get(code,{})
 result={'LCSC':code,'MPN':d.get('mpn') or mpn,'Manufacturer':d.get('manufacturer') or manufacturer,
         'Source checked':'2026-10-03' if d.get('mpn') else '',**extra}
 if d.get('datasheet_url'):result['Datasheet']=d['datasheet_url']
 return result

def block(name,fp,left,right,ds,width=15.24,step=5.08):
 """A single-unit symbol with explicit, individually numbered physical pins."""
 height=snap((max(len(left),len(right))+1)*step/2)
 s=[S('symbol'),name,node('pin_names',node('offset',n(.508))),node('in_bom',S('yes')),node('on_board',S('yes'))]
 for key,value in [('Reference','U'),('Value',name),('Footprint',fp),('Datasheet',ds),('Description',name+'; pin mapping checked against manufacturer datasheet')]:
  s.append(node('property',key,value,node('at',n(0),n(height+5.08),n(0)),node('effects',node('font',node('size',n(1.27),n(1.27))),*([node('hide',S('yes'))] if key not in ('Reference','Value') else []))))
 s.append(node('symbol',name+'_0_1',node('rectangle',node('start',n(-width),n(height)),node('end',n(width),n(-height)),node('stroke',node('width',n(.254)),node('type',S('default'))),node('fill',node('type',S('background'))))))
 unit=node('symbol',name+'_1_1');nums=[]
 for side,pins in [('left',left),('right',right)]:
  for i,(num,pinname,typ) in enumerate(pins):
   nums.append(str(num));x=(-1 if side=='left' else 1)*(width+2.54);y=height-step*(i+1)
   unit.append(node('pin',S(typ),S('line'),node('at',n(x),n(y),n(0 if side=='left' else 180)),node('length',n(2.54)),node('name',pinname,node('effects',node('font',node('size',n(1),n(1))))),node('number',str(num),node('effects',node('font',node('size',n(1),n(1)))))))
 assert len(nums)==len(set(nums)),name
 s.append(unit);return s

custom=[]
custom.append(block('TPS259827ONRGE','pulsarfab:TI_RGE0024M_VQFN24_2EP_4x4mm',
 [(1,'IN','power_in'),(2,'IN','power_in'),(3,'IN','power_in'),(16,'IN','power_in'),(25,'EP_IN','power_in'),(6,'EN_UVLO','input'),(4,'GND','power_in'),(5,'GND','power_in'),(14,'GND','power_in'),(26,'EP_GND','power_in')],
 [(17,'OUT','power_out'),(18,'OUT','passive'),(19,'OUT','passive'),(20,'OUT','passive'),(21,'OUT','passive'),(22,'OUT','passive'),(23,'OUT','passive'),(24,'OUT','passive'),(13,'PG','open_collector'),(9,'IMON','output'),(8,'ILIM','passive'),(15,'dVdT','passive'),(7,'ITIMER','passive'),(10,'RETRY_DLY','passive'),(11,'NRETRY','passive'),(12,'LDSTRT','input')],
 'https://www.ti.com/lit/ds/symlink/tps25982.pdf',step=3.81))
custom.append(block('TPS3700DDC',SOT6,[(5,'VDD','power_in'),(3,'INA+','input'),(4,'INB-','input'),(2,'GND','power_in')],[(1,'OUTA','open_collector'),(6,'OUTB','open_collector')],'https://www.ti.com/lit/ds/symlink/tps3700.pdf'))
custom.append(block('LM74700QDBV',SOT6,[(6,'ANODE','power_in'),(3,'EN','input'),(1,'VCAP','passive'),(2,'GND','power_in')],[(4,'CATHODE','input'),(5,'GATE','output')], 'https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf'))
custom.append(block('TPS2553DBV',SOT6,[(1,'IN','power_in'),(3,'EN','input'),(2,'GND','power_in')],[(6,'OUT','power_out'),(4,'~{FAULT}','open_collector'),(5,'ILIM','passive')], 'https://www.ti.com/lit/ds/symlink/tps2553.pdf'))
custom.append(block('TPS3808G33DBV',SOT6,[(6,'VDD','power_in'),(5,'SENSE','input'),(3,'~{MR}','input'),(2,'GND','power_in')],[(1,'~{RESET}','open_collector'),(4,'CT','passive')], 'https://www.ti.com/lit/ds/symlink/tps3808.pdf'))
left=[(p,'3V3_'+nm,'power_in') for p,nm in [(5,'A1'),(10,'A2'),(52,'A3'),(57,'A4'),(24,'CORE'),(46,'IO'),(64,'PLL')]]
left += [(25,'VDD18','power_out'),(62,'VDD18PLL','power_out'),(65,'EP_GND','power_in'),(63,'RBIAS','passive'),(61,'XTAL1','input'),(60,'XTAL2','output'),(43,'~{RESET}','input'),(44,'VBUS_DET','input')]
left += [(p,nm,'input' if p in (13,19) else 'bidirectional') for p,nm in [(13,'CFG2'),(42,'CFG1'),(41,'CFG0'),(45,'NONREM0'),(40,'NONREM1'),(34,'GANG_EN'),(50,'BOOST0'),(48,'BOOST1'),(19,'TEST')]]
left += [(p,'SWAP'+str(i),'bidirectional') for i,p in enumerate([51,49,47,33,31,17,15],1)]
right=[(59,'UP_DP','bidirectional'),(58,'UP_DM','bidirectional')]
dp=[2,4,7,9,12,54,56];dm=[1,3,6,8,11,53,55];pwr=[29,26,23,20,30,39,36];oc=[28,27,22,21,35,38,37]
for i in range(7):right += [(dp[i],f'DN{i+1}_DP','bidirectional'),(dm[i],f'DN{i+1}_DM','bidirectional'),(pwr[i],f'PWR{i+1}','output'),(oc[i],f'~{{OC{i+1}}}','input')]
right += [(p,'LED_B'+str(i),'output') for i,p in enumerate([32,18,16,14],4)]
assert sorted(p[0] for p in left+right)==list(range(1,66))
custom.append(block('USB2517-JZX','Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm',left,right,'https://ww1.microchip.com/downloads/en/DeviceDoc/00001598C.pdf',width=20.32,step=3.81))
(BASE/'hardware/lib/symbols/pulsarfab_hub.kicad_sym').write_text(dump([S('kicad_symbol_lib'),node('version',S('20241209')),node('generator',S('kicad_symbol_editor')),*custom])+'\n')

sheet_specs=[('Power input','power_input'),('DC supplies','supplies'),('Controller','controller'),('USB hub','usb_hub'),('Heaters','heaters')]
sheet_specs += [(f'DC outlet {i}','dc_outlet') for i in range(1,5)]
sheet_specs += [(f'USB port {i}','usb_port') for i in range(1,5)]
paths={name:'/'+rootid+'/'+uid('sheet:'+name) for name,file in sheet_specs}

def make(name,title,paper='A4'):
 return Sheet(name,title,[paths[n] for n,f in sheet_specs if f==name],paper)
R_CODES={'100k':'C25803','10k':'C25804','4.7k':'C23162','5.1k':'C23186','3.3k':'C22978','22k':'C31850','20k':'C4184','8.2k':'C25981','1k':'C21190','47':'C23182','43.2k':'C23053','12k':'C22790','24.9k':'C25962','150k':'C22807','332k':'C23139','220k':'C22961','470k':'C23178','249':'C22919','820':'C23253'}
C_CODES={'100n':'C14663','1u':'C15849','4.7u':'C19666','10u':'C138687','220n':'C64705','22u':'C12891','22n':'C21122','10n':'C1589','18p':'C342890','4.7n':'C1621'}
def put(s,ref,lib,x,y,value=None,fp=None,code='',angle=0,**kw):
 if not code and value:
  first=value.split(' / ')[0]
  if lib=='Device:R' and fp==RFP:code=R_CODES.get(first,'')
  if lib=='Device:C':code=C_CODES.get(first,'')
 return s.comp(ref,lib,x,y,value=value,fp=fp,angle=angle,fields=fields(code),**kw)
def R(s,ref,x,y,value,angle=0,code='',**kw):return put(s,ref,'Device:R',x,y,value,RFP,code,angle,**kw)
def C(s,ref,x,y,value='100n',fp=CFP,code='C14663',**kw):return put(s,ref,'Device:C',x,y,value,fp,code,**kw)
def named(s,ref,num,name,length=7.62):
 """Wire in the direction away from a pin, then place a local net label."""
 p=s.pins[ref][str(num)]; c=s.symbols[ref];cx,cy=map(float,child(c,'at')[1:3])
 if p[0]<cx: end=(round(p[0]-length,4),p[1]);a=180
 elif p[0]>cx:end=(round(p[0]+length,4),p[1]);a=0
 elif p[1]<cy:end=(p[0],round(p[1]-length,4));a=0
 else:end=(p[0],round(p[1]+length,4));a=0
 s.wire(p,end);s.label(name,end,a);return end
def branch(s,ref,lib,x,y,value,net1,net2,fp=None,code='',**kw):
 p=put(s,ref,lib,x,y,value,fp or (RFP if lib=='Device:R' else CFP),code,**kw)
 named(s,ref,1,net1,5.08);named(s,ref,2,net2,5.08);return p
def ports(s,entries,x=25.4,y=40.64):
 for i,(name,direction) in enumerate(entries):
  yy=snap(y+i*7.62);a=s.port(name,x,yy,direction);b=pt(x+20.32,yy);s.wire(a,b);s.label(name,b)
def powerflag(s,name,x,y,num):
 s.flag('#FLG'+str(num),pt(x,y));s.label(name,pt(x,y))
def nc_rest(s,ref,used):
 for num,p in s.pins[ref].items():
  if num not in {str(n) for n in used}:s.nc(p)

# Input connectors are mutually exclusive assembly options. The small barrel path
# has its own 5 A fuse; it never bypasses the fuse to the XT60 high-current rail.
s=make('power_input','Fused input and reverse-polarity protection','A3')
s.text('POWER INPUT | 12-18 V nominal | XT60 or barrel assembly option',20,16,2)
put(s,'J10','Connector_Generic:Conn_01x02',35.56,45.72,'XT60: 2=PLUS, 1=GND','pulsarfab:AMASS_XT60PW-M_Edge','C98732')
put(s,'J11','Connector:Barrel_Jack_Switch',35.56,86.36,'BARREL input / DNP','pulsarfab:BarrelJack_GCT_DCJ200_Edge','C5280493')
child(s.symbols['J11'],'dnp')[1]=S('yes')
put(s,'F10','Device:Fuse',78.74,45.72,'30A / upstream budget','pulsarfab:Fuse_S1032_10.3x3.2mm','C553917',90)
put(s,'F11','Device:Fuse',78.74,83.82,'5A / barrel only','Fuse:Fuse_Littelfuse-NANO2-451_453','C48467',90)
child(s.symbols['F11'],'dnp')[1]=S('yes')
s.wire(s.pins['J10']['2'],pt(20.32,48.26),pt(20.32,45.72),pt(20.32,30.48),pt(63.5,30.48),pt(63.5,45.72),s.pins['F10']['1'])
s.wire(s.pins['J11']['1'],s.pins['F11']['1'])
for ref,num in [('J10',1),('J11',2)]:named(s,ref,num,'GND')
s.nc(s.pins['J11']['3'])
for ref in ('F10','F11'):named(s,ref,2,'VIN_RAW')
put(s,'Q10','Transistor_FET:CSD18540Q5B',157.48,50.8,code='C86513')
put(s,'U10','pulsarfab_hub:LM74700QDBV',139.7,101.6,code='C2941042')
for n in [1,2,3]:named(s,'Q10',n,'VIN_RAW')
named(s,'Q10',5,'VIN');named(s,'Q10',4,'INPUT_GATE')
for n,name in [(6,'VIN_RAW'),(3,'VIN_RAW'),(1,'VCAP'),(2,'GND'),(4,'VIN'),(5,'INPUT_GATE')]:named(s,'U10',n,name)
branch(s,'C10','Device:C',93.98,119.38,'100n / 50V','VCAP','VIN_RAW',code='C14663')
branch(s,'D10','Device:D_Zener',218.44,68.58,'SMCJ18A','VIN','GND','Diode_SMD:D_SMC','C438102',angle=270)
branch(s,'C11','Device:C',248.92,68.58,'100n / 50V','VIN','GND',code='C14663')
branch(s,'C12','Device:C_Polarized',284.48,68.58,'470u / 35V','VIN','GND','Capacitor_THT:CP_Radial_D10.0mm_P5.00mm','C106703')
ports(s,[('VIN','output'),('GND','input')],330.2,50.8)
powerflag(s,'GND',259.08,124.46,10);powerflag(s,'VIN_RAW',279.4,124.46,11);powerflag(s,'VIN',304.8,124.46,12)
s.text('FIT J10 + F10 OR J11 + F11. Do not populate both input connector paths.\nXT60: provisional 25 A shared continuous budget; fuse, copper and temperature still require validation.\nBarrel: 5 A absolute TOTAL ceiling; 3.5 A provisional continuous budget after fuse derating. Use a current-limited supply.\nLM74700 + Q10 provides reverse-polarity / reverse-current protection. It is not an overvoltage disconnect.\nNever apply more than 18 V nominal. TVS pulse capability is not a sustained overvoltage rating.',25.4,162.56,1.5)
s.finish()

# Two identical 36 V-rated buck families keep heat away from the humidity sensor.
s=make('supplies','5 V USB and 3.3 V logic supplies','A3')
s.text('DC SUPPLIES | LMR33630ADDA, 400 kHz | 5 V / 3 A + 3.3 V logic',20,16,2)
ports(s,[('VIN','input'),('GND','input'),('V5','output'),('V3','output')],25.4,35.56)
for idx,(y,vin,vout,lval,fb) in enumerate([(60.96,'VIN','V5','8.2u / 10A sat','24.9k'),(177.8,'V5','V3','6.8u / 12A sat','43.2k')]):
 b=20+idx*10;u='U'+str(b);cx=134.62
 put(s,u,'Regulator_Switching:LMR33630ADDA',cx,y,code='C841384',fp='Package_SO:Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm')
 p=s.pins[u]
 # Input, enable, bypass, bootstrap, inductor, output bank and feedback are visual wires.
 named(s,u,2,vin);s.wire(p['3'],(109.22,p['3'][1]),(109.22,p['2'][1]),p['2'])
 for n in [1,9]:named(s,u,n,'GND')
 s.nc(p['4'])
 branch(s,'C'+str(b),'Device:C',83.82,y+17.78,'10u / 50V',vin,'GND','Capacitor_SMD:C_1210_3225Metric')
 branch(s,'C'+str(b+1),'Device:C',104.14,y+17.78,'220n / 50V',vin,'GND')
 c=C(s,'C'+str(b+2),119.38,y+30.48,'1u / 50V',code='')
 s.wire(p['6'],(119.38,p['6'][1]),c['1']);named(s,'C'+str(b+2),2,'GND')
 cb=put(s,'C'+str(b+3),'Device:C',165.1,y-12.7,'100n',CFP,'C14663',90)
 s.wire(p['7'],(p['7'][0],y-12.7),cb['1'])
 swx=187.96;s.wire(cb['2'],(swx,y-12.7),(swx,p['8'][1]),p['8'])
 ll=put(s,'L'+str(b),'Device:L',213.36,p['8'][1],lval,'pulsarfab:L_SXN_SMMS1050','C149543' if idx==0 else 'C149542',90)
 s.wire((swx,p['8'][1]),ll['1']);s.wire(ll['2'],(340.36,p['8'][1]));s.label(vout,(340.36,p['8'][1]))
 for j in range(4):
  cc=C(s,'C'+str(b+4+j),254+j*25.4,y+15.24,'22u / 25V','Capacitor_SMD:C_1206_3216Metric','')
  s.wire(cc['1'],(cc['1'][0],p['8'][1]));named(s,'C'+str(b+4+j),2,'GND')
 rtop=R(s,'R'+str(b),213.36,y+25.4,'100k',code='C25803');rbot=R(s,'R'+str(b+1),213.36,y+55.88,fb)
 s.wire(ll['2'],(238.76,ll['2'][1]),(238.76,y+10.16),(213.36,y+10.16),rtop['1'])
 s.wire(rtop['2'],rbot['1']);s.wire(p['5'],(177.8,p['5'][1]),(177.8,y+40.64),(213.36,y+40.64));named(s,'R'+str(b+1),2,'GND')
 powerflag(s,vout,355.6,y-2.54,20+idx)
s.text('Follow TI SNVSAN3F Table 9-2. 5 V uses nearest preferred 8.2 uH to the 8 uH example.\nPlace ceramic input/boot/VCC capacitors at the IC; keep SW copper compact and FB away from SW.\nUSB budget: 4 x 500 mA plus about 0.4 A for logic at full activity. Verify inductor saturation, MLCC bias,\ntransient response and regulator temperature before routing release.',25.4,254,1.27)
s.finish()

# MCU retains the original chip, SWD and I2C sensor. DC enables use plain GPIOs.
s=make('controller','STM32 controller and ambient sensor','A3')
s.text('CONTROLLER | 2 heater PWM + 4 DC enables / ADC current readings / faults',20,16,2)
put(s,'U1','pulsarfab:STM32G0B1KBU6',132.08,86.36,fp='Package_DFN_QFN:UFQFPN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm',code='C5159549')
gpio={7:'HTR0',8:'HTR1',11:'IMON1',12:'IMON2',13:'IMON3',14:'IMON4',15:'DC_EN1',16:'DC_EN2',17:'DC_EN3',1:'DC_EN4',27:'DC_PG1',28:'DC_PG2',29:'DC_PG3',20:'DC_PG4',22:'MCU_DM',23:'MCU_DP',19:'USB_ATTACH',24:'SWDIO',25:'SWCLK',30:'SCL',31:'SDA',4:'V3',5:'GND',33:'GND',6:'NRST'}
for n,name in gpio.items():named(s,'U1',n,name)
nc_rest(s,'U1',gpio)
for r,x,v in [('C1',68.58,'100n'),('C2',88.9,'4.7u / 16V')]:branch(s,r,'Device:C',x,48.26,v,'V3','GND',code='C14663' if r=='C1' else '')
branch(s,'C3','Device:C',68.58,96.52,'100n','NRST','GND',code='C14663')
branch(s,'R1','Device:R',203.2,48.26,'4.7k','V3','SCL')
branch(s,'R2','Device:R',226.06,48.26,'4.7k','V3','SDA')
put(s,'U2','Sensor_Humidity:SHT4x',218.44,93.98,'SHT40-AD1B-R2',code='C2909890')
for n,name in [(1,'SDA'),(2,'SCL'),(3,'V3'),(4,'GND')]:named(s,'U2',n,name)
branch(s,'C4','Device:C',264.16,91.44,'100n','V3','GND',code='C14663')
put(s,'J1','Connector_Generic:Conn_01x05',325.12,48.26,'SWD','Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical','C492404')
for n,name in enumerate(['V3','SWDIO','SWCLK','NRST','GND'],1):named(s,'J1',n,name)
entries=[('V3','input'),('GND','input'),('HTR0','output'),('HTR1','output'),('MCU_DP','bidirectional'),('MCU_DM','bidirectional'),('USB_ATTACH','input'),('SCL','output'),('SDA','bidirectional')]
ports(s,entries,25.4,147.32)
for ch in range(1,5):ports(s,[(f'DC_EN{ch}','output'),(f'IMON{ch}','input'),(f'DC_PG{ch}','input')],139.7+(ch-1)*63.5,157.48)
s.text('PA0/PA1: active-high TIM2 heater drive. PB0/PB1/PB2/PB9: static DC GPIO only (never PWM).\nPA4..PA7: ADC IMON1..4. PB3/PB4/PB5/PC6: active-low DC faults.\nPA9: internal hub port 1 enable (3.3 V). Attach USB only while high; disable UCPD dead-battery pull-down.\nSHT40 at 0x44; keep physically away from power components. New firmware pin map is required.',25.4,223.52,1.4)
s.finish()

# Two resistive heater outputs. Shared push-pull driver and pulldowns replace the
# original inverting pull-up circuit, eliminating its loss-of-3V3 turn-on path.
s=make('heaters','Two default-off heater outputs','A3')
s.text('HEATERS | active-high PWM, 5 V gate drive, resistive loads only',20,16,2)
ports(s,[('VIN','input'),('V5','input'),('GND','input'),('HTR0','input'),('HTR1','input'),('V3','input'),('SCL','input'),('SDA','bidirectional')],25.4,40.64)
put(s,'U50','Driver_FET:TC4427xOA',104.14,83.82,'TC4427AVOA713',code='C624944')
for n,name in [(2,'HTR0'),(4,'HTR1'),(6,'V5'),(3,'GND'),(7,'DRIVE0'),(5,'DRIVE1')]:named(s,'U50',n,name)
s.nc(s.pins['U50']['1']);s.nc(s.pins['U50']['8'])
branch(s,'C50','Device:C',93.98,38.1,'100n','V5','GND',code='C14663')
branch(s,'C51','Device:C',116.84,38.1,'1u / 50V','V5','GND')
for i in range(2):
 b=51+i*10;x=195.58+i*104.14
 branch(s,'R'+str(b),'Device:R',x-25.4,129.54,'10k',f'HTR{i}','GND',code='C25804')
 put(s,'Q'+str(b),'Transistor_FET:Q_NMOS_GDS',x,86.36,'AOD4184A','Package_TO_SOT_SMD:TO-252-2',code='C5370959')
 rr=R(s,'R'+str(b+1),x-25.4,86.36,'47',90)
 s.wire(rr['2'],s.pins['Q'+str(b)]['1']);named(s,'R'+str(b+1),1,f'DRIVE{i}')
 rg=R(s,'R'+str(b+2),x-12.7,111.76,'100k',code='C25803')
 s.wire(rg['1'],(x-12.7,86.36));named(s,'R'+str(b+2),2,'GND');named(s,'Q'+str(b),3,'GND')
 named(s,'Q'+str(b),2,f'HEATER{i}_LOW')
 put(s,'J'+str(b),'Connector_Generic:Conn_01x02',x+30.48,48.26,'HEATER '+str(i+1),'pulsarfab:TerminalBlock_KEFA_KF128_2P_P5.08mm','C474952')
 named(s,'J'+str(b),2,f'HEATER{i}_LOW')
 ff=put(s,'F'+str(b),'Device:Fuse',x,48.26,'7A heater fuse','Fuse:Fuse_Littelfuse-NANO2-451_453','C99548',90)
 s.wire(ff['2'],s.pins['J'+str(b)]['1']);named(s,'F'+str(b),1,'HTR_VIN')
 branch(s,'D'+str(b),'Device:D_Zener',x+33.02,99.06,'SMBJ20A',f'HEATER{i}_LOW','GND','Diode_SMD:D_SMB','C364296',angle=270)
put(s,'U51','Sensor_Energy:INA226',119.38,218.44,code='C49851')
put(s,'R50','Device:R',60.96,177.8,'2m / 3W / 1%','Resistor_SMD:R_2512_6332Metric','C2994640',90)
named(s,'R50',1,'VIN');named(s,'R50',2,'HTR_VIN')
for nn,net in [(10,'VIN'),(9,'HTR_VIN'),(8,'HTR_VIN'),(6,'V3'),(7,'GND'),(1,'GND'),(2,'GND'),(4,'SDA'),(5,'SCL')]:named(s,'U51',nn,net)
s.nc(s.pins['U51']['3'])
branch(s,'C52','Device:C',165.1,218.44,'100n','V3','GND',code='C14663')
powerflag(s,'HTR_VIN',208.28,218.44,51)
s.text('J51/J61 pin 1 = fused VIN; pin 2 = switched return. Do not bond switched return to system ground.\n10k input pulldowns + 100k gate pulldowns request OFF during reset or missing logic power.\n5 A/channel is a design target, subject to MOSFET, connector, fuse and copper thermal validation.\nUse low-frequency heater PWM; verify gate waveform and shutdown behavior during brownout.',233.68,182.88,1.27)
s.finish()

# Four identical current-monitored high-side outlets. No PWM input exists.
s=make('dc_outlet','5 A switched DC outlet','A3')
s.text('SWITCHED DC OUTLET | 12-18 V / 5 A service | hardware voltage inhibit / latched breaker',20,16,1.8)
def dcput(ref,lib,x,y,value=None,fp=None,code='',angle=0):
 refs=[ref[0]+str(100*i+int(ref[1:])%100) for i in range(1,5)]
 return put(s,ref,lib,x,y,value,fp,code,angle,refs=refs)
def dcr(ref,x,y,v,n1,n2,code=''):
 p=dcput(ref,'Device:R',x,y,v,RFP,code);named(s,ref,1,n1,5.08);named(s,ref,2,n2,5.08);return p
def dcc(ref,x,y,v,n1,n2,fp=CFP,code=''):
 p=dcput(ref,'Device:C',x,y,v,fp,code);named(s,ref,1,n1,5.08);named(s,ref,2,n2,5.08);return p
ports(s,[('VIN','input'),('V3','input'),('GND','input'),('ENABLE','input'),('CURRENT','output'),('PGOOD','output')],25.4,38.1)
dcput('U101','pulsarfab_hub:TPS259827ONRGE',213.36,99.06,code='C2155765')
mapping={**{n:'VIN' for n in [1,2,3,16,25]},**{n:'GND' for n in [4,5,14,26,10,11,12]},**{n:'OUT' for n in range(17,25)},6:'EN_SW',13:'PGOOD',9:'IMON_RAW',8:'ILIM',15:'DVDT'}
for n,name in mapping.items():named(s,'U101',n,name)
nc_rest(s,'U101',mapping) # ITIMER open = fastest overload response. RETRY_DLY grounded = latch off.
dcput('U102','pulsarfab_hub:TPS3700DDC',154.94,175.26,code='C33002')
for n,name in {5:'V3',3:'UV_SENSE',4:'OV_SENSE',2:'GND',1:'EN_SW',6:'EN_SW'}.items():named(s,'U102',n,name)
dcr('R101',83.82,139.7,'220k','VIN','UV_SENSE');dcr('R102',83.82,185.42,'10k','UV_SENSE','GND')
dcr('R103',111.76,139.7,'470k','VIN','OV_SENSE');dcr('R104',111.76,203.2,'10k','OV_SENSE','GND')
dcr('R105',264.16,200.66,'100k','EN_SW','GND')
dcr('R106',322.58,104.14,'10k','V3','PGOOD')
dcr('R107',241.3,200.66,'249 / 1%','ILIM','GND')
dcr('R108',289.56,172.72,'820 / 1%','IMON_RAW','GND')
dcput('R109','Device:R',320.04,149.86,'10k',RFP,'C25804',90);named(s,'R109',1,'IMON_RAW');named(s,'R109',2,'CURRENT')
dcput('R110','Device:R',231.14,175.26,'10k',RFP,'C25804',90);named(s,'R110',1,'ENABLE');named(s,'R110',2,'EN_SW')
dcc('C101',172.72,45.72,'100n / 50V','VIN','GND',code='C14663')
dcc('C102',294.64,68.58,'100n / 50V','OUT','GND',code='C14663')
dcc('C103',213.36,200.66,'4.7n / 50V','DVDT','GND')
dcc('C104',353.06,172.72,'10n','CURRENT','GND')
dcc('C105',154.94,220.98,'100n','V3','GND',code='C14663')
dcput('J101','Connector:Barrel_Jack_Switch',345.44,48.26,'5A DC / center +','pulsarfab:BarrelJack_GCT_DCJ200_Edge','C5280493')
named(s,'J101',1,'OUT');named(s,'J101',2,'GND');s.nc(s.pins['J101']['3'])
dcput('D101','Device:D_Schottky',373.38,104.14,'SS54','Diode_SMD:D_SMA','C22452',270);named(s,'D101',1,'OUT');named(s,'D101',2,'GND')
dcput('D102','Device:D_Zener',132.08,45.72,'SMBJ18A','Diode_SMD:D_SMB','C353379',270);named(s,'D102',1,'VIN');named(s,'D102',2,'GND')
# Visible divider, open-drain inhibit, power-pin bus and monitor/filter connections.
s.wire(s.pins['R101']['2'],s.pins['R102']['1']);s.wire((83.82,172.72),(127,172.72),s.pins['U102']['3'])
s.wire(s.pins['R103']['2'],s.pins['R104']['1']);s.wire((111.76,177.8),s.pins['U102']['4'])
for nn in [1,6]:s.wire(s.pins['U102'][str(nn)],(187.96,s.pins['U102'][str(nn)][1]))
s.wire((187.96,s.pins['U102']['1'][1]),(187.96,s.pins['U102']['6'][1]))
s.wire(s.pins['R110']['2'],(264.16,175.26),s.pins['R105']['1'])
for nn in [1,2,3,16,25]:s.wire(s.pins['U101'][str(nn)],(185.42,s.pins['U101'][str(nn)][1]))
s.wire((185.42,s.pins['U101']['1'][1]),(185.42,s.pins['U101']['25'][1]))
for nn in range(17,25):s.wire(s.pins['U101'][str(nn)],(256.54,s.pins['U101'][str(nn)][1]))
s.wire((256.54,s.pins['U101']['17'][1]),(256.54,s.pins['U101']['24'][1]))
s.wire((256.54,s.pins['U101']['17'][1]),(256.54,55.88),(294.64,55.88),s.pins['C102']['1'])
s.wire(s.pins['U101']['9'],(274.32,s.pins['U101']['9'][1]),(274.32,149.86),s.pins['R109']['1'])
s.wire(s.pins['R108']['1'],(289.56,149.86))
s.wire(s.pins['R109']['2'],(353.06,149.86),s.pins['C104']['1'])
s.text('TPS259827O: 249R gives 5.97 A nominal breaker threshold; 5 A service target needs tolerance/bench qualification.\nITIMER open: fastest overload response. Fast short trip ~2.1x setpoint. RETRY_DLY grounded: latch off.\nIMON: 246 uA/A x 820R = 0.20172 V/A (1.009 V at 5 A); 10k / 10n ADC filter. Calibrate each outlet.\nTPS3700 independently inhibits EN below ~9.2 V or above ~19.2 V; window recovery can re-enable an asserted GPIO.\nPGOOD is HIGH when ready; LOW also means OFF/startup/inhibit, not exclusively a latched current fault.\nEP25 = VIN, EP26 = GND. -15 C minimum junction rating accepted. No reverse blocking: do not backfeed OUT.\nSMBJ18A input TVS + SS54 output clamp need short loops and hot-plug/inductive-load bench validation.',25.4,241.3,1.27)
s.finish()

# Each external USB port has independent 500 mA service and a protected 5 V switch.
s=make('usb_port','USB 2.0 downstream port')
s.text('USB DOWNSTREAM | 500 mA service | independent power and overcurrent',20,16,1.8)
def usbput(ref,lib,x,y,value=None,fp=None,code='',angle=0):
 refs=[ref[0]+str(500+100*i+int(ref[1:])%100) for i in range(4)]
 return put(s,ref,lib,x,y,value,fp,code,angle,refs=refs)
ports(s,[('V5','input'),('GND','input'),('DP','bidirectional'),('DM','bidirectional'),('ENABLE','input'),('OVERCURRENT','output')],25.4,35.56)
usbput('U501','pulsarfab_hub:TPS2553DBV',121.92,55.88,code='C55266')
for n,name in [(1,'V5'),(3,'ENABLE'),(2,'GND'),(6,'VBUS'),(4,'OVERCURRENT'),(5,'ILIM')]:named(s,'U501',n,name)
usbput('R501','Device:R',83.82,101.6,'43.2k / 1%',RFP);named(s,'R501',1,'ILIM');named(s,'R501',2,'GND')
usbput('R502','Device:R',109.22,101.6,'100k',RFP,'C25803');named(s,'R502',1,'ENABLE');named(s,'R502',2,'GND')
usbput('C501','Device:C',177.8,40.64,'100n',CFP,'C14663');named(s,'C501',1,'V5');named(s,'C501',2,'GND')
usbput('C502','Device:C_Polarized',203.2,40.64,'150u / 10V / 20%','pulsarfab:CP_RVT_D6.3mm_L5.4mm','C970688');named(s,'C502',1,'VBUS');named(s,'C502',2,'GND')
usbput('J501','Connector:USB_A',243.84,99.06,'USB-A / 500mA','pulsarfab:USB_A_GCT_USB1046_Edge','C6307429')
for n,name in [(1,'VBUS'),(4,'GND'),('SH','GND')]:named(s,'J501',n,name)
usbput('U502','Power_Protection:USBLC6-2SC6',177.8,137.16,code='C7519')
for n,name in [(1,'DM'),(6,'DM'),(3,'DP'),(4,'DP'),(5,'VBUS'),(2,'GND')]:named(s,'U502',n,name)
named(s,'J501',2,'DM');named(s,'J501',3,'DP')
s.wire(s.pins['U501']['6'],(152.4,50.8),(152.4,20.32),(266.7,20.32),(266.7,76.2),(274.32,76.2),(274.32,93.98),s.pins['J501']['1'])
s.wire(s.pins['C502']['1'],(203.2,20.32))
usbput('C503','Device:C',231.14,40.64,'100n',CFP,'C14663');named(s,'C503',1,'VBUS');named(s,'C503',2,'GND')
s.text('TPS2553 active-high EN; FAULT is open-drain, pulled up inside the hub.\n43.2k sets about 0.60 A nominal limit; tolerance keeps the minimum above 500 mA.\nVBUS bulk 150 uF +/-20% gives at least 120 uF; verify startup droop.\nRoute 90-ohm differential pairs through the ESD package, without stubs.\nVBUS is supplied only from the local 5 V buck; never from the upstream host.',25.4,160.02,1.1)
s.finish()

# Hub support. Pin straps, unused-port disable, clock, regulator capacitors and
# upstream sensing are all explicit; no EEPROM is required for this configuration.
s=make('usb_hub','USB 2.0 hub and upstream interface','A2')
s.text('USB HUB | USB2517 | internal port 1 + external ports 2-5; ports 6/7 disabled',20,16,2)
put(s,'U40','pulsarfab_hub:USB2517-JZX',200.66,114.3,code='C1521556')
hubmap={**{p:'V3' for p in [5,10,52,57,24,46,64]},25:'V18_CORE',62:'V18_PLL',65:'GND',63:'RBIAS',61:'XTAL1',60:'XTAL2',43:'HUB_RESET',44:'VBUS_DET',59:'UP_DP',58:'UP_DM',13:'GND',19:'GND'}
for i in range(5):
 hubmap[dp[i]]='MCU_DP' if i==0 else f'USB{i}_DP';hubmap[dm[i]]='MCU_DM' if i==0 else f'USB{i}_DM'
 hubmap[pwr[i]]='USB_ATTACH' if i==0 else f'USB{i}_EN'
 hubmap[oc[i]]='V3' if i==0 else f'USB{i}_OC'
for p in [53,54,55,56]:hubmap[p]='DISABLE_'+str(p)
for p in [41,42,45,40,34,50,48,51,49,47,33,31,17,15]:hubmap[p]='STRAP_'+str(p)
hub_ends={n:named(s,'U40',n,name) for n,name in hubmap.items()}
# Show the seven common supply pins as a physical branch, keeping the two
# internal 1.8 V outputs separate below them.
s.wire(*(hub_ends[n] for n in [5,10,52,57,24,46,64]))
nc_rest(s,'U40',hubmap)
ports(s,[('V3','input'),('GND','input'),('MCU_DP','bidirectional'),('MCU_DM','bidirectional'),('USB_ATTACH','output')],25.4,35.56)
for i in range(1,5):ports(s,[(f'USB{i}_DP','bidirectional'),(f'USB{i}_DM','bidirectional'),(f'USB{i}_EN','output'),(f'USB{i}_OC','input')],345.44+(i-1)*58.42,203.2)
# Pull straps via resistors because several pins become LED outputs after reset.
strap=[41,42,45,40,34,50,48,51,49,47,33,31,17,15]
for i,p in enumerate(strap):
 x=55.88+(i%7)*38.1;y=228.6+(i//7)*53.34
 branch(s,'R'+str(901+i),'Device:R',x,y,'10k','V3' if p==45 else 'STRAP_'+str(p),'STRAP_'+str(p) if p==45 else 'GND',code='C25804')
for i,p in enumerate([53,54,55,56]):branch(s,'R'+str(915+i),'Device:R',345.44+i*30.48,149.86,'10k','V3','DISABLE_'+str(p),code='C25804')
branch(s,'R919','Device:R',142.24,55.88,'12k / 1%','RBIAS','GND')
put(s,'Y40','Device:Crystal_GND24',101.6,157.48,'24MHz / CL=12pF','Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm','C5181479')
for n,name in [(1,'XTAL1'),(3,'XTAL2'),(2,'GND'),(4,'GND')]:named(s,'Y40',n,name)
branch(s,'C901','Device:C',66.04,180.34,'18p / C0G','XTAL1','GND')
branch(s,'C902','Device:C',137.16,180.34,'18p / C0G','XTAL2','GND')
# Seven 100 nF bypasses plus separate core and PLL internal-regulator capacitors.
for i in range(7):branch(s,'C'+str(903+i),'Device:C',55.88+i*33.02,335.28,'100n','V3','GND',code='C14663')
for i,net in enumerate(['V3','V3','V18_CORE','V18_PLL']):branch(s,'C'+str(910+i),'Device:C',317.5+i*33.02,335.28,'1u / 50V',net,'GND')
# A voltage supervisor holds reset until the 3.3 V rail has settled.
put(s,'U41','pulsarfab_hub:TPS3808G33DBV',472.44,297.18,code='C43698')
for n,name in [(6,'V3'),(5,'V3'),(3,'V3'),(2,'GND'),(1,'HUB_RESET')]:named(s,'U41',n,name)
s.nc(s.pins['U41']['4']) # CT open: 20 ms reset delay per TI datasheet.
branch(s,'R920','Device:R',533.4,297.18,'10k','V3','HUB_RESET',code='C25804')
branch(s,'C914','Device:C',472.44,345.44,'100n','V3','GND',code='C14663')
# Upstream USB-C is data + VBUS sense only, with two independent Rd resistors.
put(s,'J40','Connector:USB_C_Receptacle_USB2.0_16P',350.52,66.04,'USB-C upstream','Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal','C3020560')
j=s.pins['J40']
jends={p:named(s,'J40',p,name) for p,name in [('A4','HOST_VBUS'),('A1','GND'),('SH','GND'),('A6','UP_DP'),('B6','UP_DP'),('A7','UP_DM'),('B7','UP_DM'),('A5','CC1'),('B5','CC2')]}
s.wire(jends['A6'],jends['B6']);s.wire(jends['A7'],jends['B7'])
for p in ['A8','B8']:s.nc(j[p])
branch(s,'R921','Device:R',406.4,50.8,'5.1k','CC1','GND',code='C23186')
branch(s,'R922','Device:R',431.8,50.8,'5.1k','CC2','GND',code='C23186')
branch(s,'R923','Device:R',482.6,50.8,'100k','HOST_VBUS','VBUS_DET',code='C25803')
branch(s,'R924','Device:R',482.6,96.52,'100k','VBUS_DET','GND',code='C25803')
branch(s,'C915','Device:C',518.16,50.8,'100n','HOST_VBUS','GND',code='C14663')
put(s,'U42','Power_Protection:USBLC6-2SC6',419.1,180.34,code='C7519')
for n,name in [(1,'UP_DM'),(6,'UP_DM'),(3,'UP_DP'),(4,'UP_DP'),(5,'HOST_VBUS'),(2,'GND')]:named(s,'U42',n,name)
for i in range(1,5):branch(s,'R'+str(924+i),'Device:R',345.44+(i-1)*30.48,101.6,'10k','V3',f'USB{i}_OC',code='C25804')
powerflag(s,'HOST_VBUS',553.72,76.2,40)
s.text('Straps: CFG=000 self-powered; NONREM=01 makes port 1 permanent; individual power/OC; normal polarity.\nUnused ports 6/7: both D+ and D- pulled to 3V3 through 10k; PWR outputs unused, OC inputs unused.\nVDD18 and VDD18PLL are separate INTERNAL regulator outputs: capacitors only; do not connect them together.\nSupervisor: 3.07 V threshold, 20 ms delay. Crystal caps start at 18 pF: verify actual board parasitics/drive level.\nKeep an uninterrupted ground plane under every USB pair. Verify 90-ohm geometry with the ordered stackup.',25.4,370.84,1.27)
s.finish()

# Root hierarchy: visible power branches plus named inter-block signal links.
from wired_schematic import n
o=Sheet(PROJECT,'System interconnect',['/'+rootid],'A2')
o.text('PULSARDEW HUB | 2 heaters + 4 monitored DC outlets + 4 USB 2.0 ports',20,16,2.5)
o.text('PROTOTYPE FLOORPLAN — routing, full-load thermal validation and new firmware are still required.',20,24,1.5)
page=2
root_ends={}
def root_sheet(title,file,x,y,w,entries):
 global page
 x,y=pt(x,y);w=snap(w);h=snap(15.24+len(entries)*5.08)
 sn=node('sheet',node('at',n(x),n(y)),node('size',n(w),n(h)),node('stroke',node('width',n(.1524)),node('type',S('default'))),node('fill',node('color',S('0'),S('0'),S('0'),S('0'))),node('uuid',uid('sheet:'+title)))
 for k,v,yy in [('Sheetname',title,y-2.54),('Sheetfile',file+'.kicad_sch',y+h+2.54)]:sn.append(node('property',k,v,node('at',n(x),n(yy),n(0)),node('effects',node('font',node('size',n(1.27),n(1.27))),node('justify',S('left')))))
 for i,(nm,typ,net) in enumerate(entries):
  p=pt(x,y+10.16+i*5.08)
  sn.append(node('pin',nm,S(typ),node('at',n(p[0]),n(p[1]),n(180)),node('effects',node('font',node('size',n(1.27),n(1.27))),node('justify',S('left'))),node('uuid',uid(title+nm))))
  a=pt(x-12.7,p[1]);o.wire(a,p);o.label(net,a,180);root_ends[(title,nm)]=a
 sn.append(node('instances',node('project',PROJECT,node('path','/'+rootid,node('page',str(page))))));page+=1;o.items.append(sn)
root_sheet('Power input','power_input',53.34,43.18,78.74,[('VIN','output','VIN'),('GND','input','GND')])
root_sheet('DC supplies','supplies',53.34,104.14,78.74,[(n,d,n) for n,d in [('VIN','input'),('GND','input'),('V5','output'),('V3','output')]])
root_sheet('Heaters','heaters',53.34,187.96,78.74,[(n,d,n) for n,d in [('VIN','input'),('V5','input'),('GND','input'),('HTR0','input'),('HTR1','input'),('V3','input'),('SCL','input'),('SDA','bidirectional')]])
ctrl=[(n,d,n) for n,d in [('V3','input'),('GND','input'),('HTR0','output'),('HTR1','output'),('MCU_DP','bidirectional'),('MCU_DM','bidirectional'),('USB_ATTACH','input'),('SCL','output'),('SDA','bidirectional')]]
for i in range(1,5):ctrl += [(f'DC_EN{i}','output',f'DC_EN{i}'),(f'IMON{i}','input',f'IMON{i}'),(f'DC_PG{i}','input',f'DC_PG{i}')]
root_sheet('Controller','controller',220.98,43.18,76.2,ctrl)
hh=[(n,d,n) for n,d in [('V3','input'),('GND','input'),('MCU_DP','bidirectional'),('MCU_DM','bidirectional'),('USB_ATTACH','output')]]
for i in range(1,5):hh += [(f'USB{i}_DP','bidirectional',f'USB{i}_DP'),(f'USB{i}_DM','bidirectional',f'USB{i}_DM'),(f'USB{i}_EN','output',f'USB{i}_EN'),(f'USB{i}_OC','input',f'USB{i}_OC')]
root_sheet('USB hub','usb_hub',220.98,190.5,76.2,hh)
for i in range(1,5):
 root_sheet(f'DC outlet {i}','dc_outlet',375.92,43.18+(i-1)*81.28,68.58,[('VIN','input','VIN'),('V3','input','V3'),('GND','input','GND'),('ENABLE','input',f'DC_EN{i}'),('CURRENT','output',f'IMON{i}'),('PGOOD','output',f'DC_PG{i}')])
 root_sheet(f'USB port {i}','usb_port',510.54,43.18+(i-1)*81.28,63.5,[('V5','input','V5'),('GND','input','GND'),('DP','bidirectional',f'USB{i}_DP'),('DM','bidirectional',f'USB{i}_DM'),('ENABLE','input',f'USB{i}_EN'),('OVERCURRENT','output',f'USB{i}_OC')])
# In the left column, make the input-to-supply/heater power paths visible.
# Crossings with other rail branches have no junction and remain separate nets.
for net,x,titles in [('VIN',20.32,['Power input','DC supplies','Heaters']),
                     ('GND',17.78,['Power input','DC supplies','Heaters']),
                     ('V5',25.4,['DC supplies','Heaters']),
                     ('V3',27.94,['DC supplies','Heaters'])]:
 points=[root_ends[(title,net)] for title in titles]
 o.wire((x,min(p[1] for p in points)),(x,max(p[1] for p in points)))
 for p in points:o.wire((x,p[1]),p)
o.text('RATINGS TO VALIDATE\n12-18 V nominal input\n4 x 5 A DC outlet targets\n2 x 5 A heater targets\n25 A shared XT60 budget\n3.5 A continuous barrel budget\nUSB: 500 mA per port\nNo PWM on DC outlets',25.4,281.94,1.5)
o.text('Same ground throughout.\nHigh-current and USB return paths\nare separated by placement.\nDo not backfeed DC outputs.',25.4,353.06,1.27)
o.finish()
pro=json.loads((BASE/'hardware/pulsardew/pulsardew.kicad_pro').read_text())
pro['sheets']=[[rootid,PROJECT]]+[[uid('sheet:'+n),n] for n,f in sheet_specs]
pro['meta']['filename']=PROJECT+'.kicad_pro'
pro.get('erc',{})['erc_exclusions']=[]
if not (OUT/(PROJECT+'.kicad_pro')).exists():
 (OUT/(PROJECT+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
print('Wrote 14 connected schematic pages in 8 files; PCB is not regenerated.')
