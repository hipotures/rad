from pathlib import Path
import shutil,subprocess,json,time,os,sys
R=Path(__file__).resolve().parent;repo=Path('/srv/ai/strata-v0.1.32');data=Path('/srv/ai/models/strata-v0132');pack=Path('/srv/ai/models/strata/packs/ud-q4_k_xl-v0132');gguf=Path('/srv/ai/models/strata/models/UD-Q4_K_XL')
sys.path.insert(0,str(repo));import setup
assert not pack.exists(),'New packdestination already exists; inspect before proceeding'
assert not (data/'mtp').exists(),'MTP destination already exists; inspect before proceeding'
data.mkdir(exist_ok=True);shutil.copytree('/srv/ai/models/strata/mtp',data/'mtp',copy_function=shutil.copy2)
env=dict(os.environ,STRATA_GGUF_PY=str(repo/'third_party/llama.cpp-pinned/gguf-py'))
assert not setup.mtp_corrupt(data/'mtp',env),'Existing copied MTP fails upstream tensor verification; no download permitted'
with (R/'logs/local-pack.log').open('w') as f:
 cmd=[str(repo/'.venv/bin/python'),str(repo/'tools/iq_pack.py'),'--gguf',str(gguf/'Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf'),'--out',str(pack),'--compat-bf16']
 f.write('COMMAND '+json.dumps(cmd)+'\n');f.flush();subprocess.run(cmd,cwd=repo,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
assert not (pack/'experts.bin').exists()
(data/'packs').mkdir(exist_ok=True);(data/'packs/unsloth-ud-q4_k_xl').symlink_to(pack,target_is_directory=True)
cmd=[str(repo/'.venv/bin/python'),str(repo/'setup.py'),'--setup','--family','unsloth','--model','UD-Q4_K_XL','--gpu','0','--context','65536','--kv','int8','--vision','none','--experimental-speed-projection','off','--gguf-dir',str(gguf),'--data-dir',str(data),'--yes','--no-start']
with (R/'logs/official-local-setup.log').open('w') as f:
 f.write('COMMAND '+json.dumps(cmd)+'\n');f.flush();p=subprocess.run(cmd,cwd=repo,env=env,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,'Official localsetup failed; inspect log; no model fetch requested'
assert not (pack/'experts.bin').exists()
(R/'raw/local-setup-terminal.json').write_text(json.dumps({'status':'COMPLETE','ended':time.time(),'command':cmd,'model_revision':'38bb39ee97821de2c9009abb7e93950eec396e66','HEAD':'c499bd102e7a4135c0de389dcfe38c399759ccc8','version':'0.1.32','build_variant':'default','pack':str(pack),'mtp':str(data/'mtp/rt'),'native_shards':str(gguf),'note':'Independent newpack and copied verifiedMTP; oldpack/MTP untouched; no engine/model download required; official --gguf-dir flow.'},indent=2))
print('Localsetup complete, no engine started',flush=True)
