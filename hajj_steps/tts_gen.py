import sherpa_onnx, wave, numpy as np, json, os
from script3d import LINES
d='../meeqat_video/tts/vits-piper-ar_JO-kareem-medium/'
tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=d+'ar_JO-kareem-medium.onnx',tokens=d+'tokens.txt',data_dir=d+'espeak-ng-data'),num_threads=4)))
os.makedirs('work/tts3',exist_ok=True); dur={}; SP=float(os.environ.get('SPEED','1.2'))
for k,t in LINES.items():
    a=tts.generate(t,sid=0,speed=SP); s=np.array(a.samples,dtype=np.float32)
    idx=np.where(np.abs(s)>0.01)[0]; s=s[max(0,idx[0]-1764):idx[-1]+1764] if len(idx) else s
    s=s/max(1e-6,np.abs(s).max())*0.9
    w=wave.open(f'work/tts3/{k}.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(a.sample_rate); w.writeframes((s*32767).astype('int16').tobytes()); w.close()
    dur[k]=len(s)/a.sample_rate
json.dump(dur,open('work/durations3.json','w'),indent=1); print(round(sum(dur.values()),1),{k:round(v,1) for k,v in dur.items()})
