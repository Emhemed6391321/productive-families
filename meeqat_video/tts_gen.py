import sherpa_onnx, wave, numpy as np, json, os, sys
from script import LINES
d='tts/vits-piper-ar_JO-kareem-medium/'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=d+'ar_JO-kareem-medium.onnx',tokens=d+'tokens.txt',data_dir=d+'espeak-ng-data'),num_threads=4))
tts=sherpa_onnx.OfflineTts(cfg)
os.makedirs('tts/out',exist_ok=True); dur={}
SPEED=float(os.environ.get('SPEED','0.95'))
for k,t in LINES.items():
    a=tts.generate(t,sid=0,speed=SPEED)
    s=np.array(a.samples,dtype=np.float32)
    # trim silence at the ends, keep 80ms
    thr=0.01; idx=np.where(np.abs(s)>thr)[0]
    if len(idx): s=s[max(0,idx[0]-1764):idx[-1]+1764]
    s=s/ max(1e-6,np.abs(s).max())*0.9
    w=wave.open(f'tts/out/{k}.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(a.sample_rate);w.writeframes((s*32767).astype('int16').tobytes());w.close()
    dur[k]=len(s)/a.sample_rate
json.dump(dur,open('tts/durations.json','w'),indent=1)
print(sum(dur.values()), {k:round(v,1) for k,v in dur.items()})
