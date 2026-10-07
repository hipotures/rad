"""v1.1: repair only float validation discovered by source audit before runtime."""
import pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]);subprocess.run([sys.executable,str(root/'scripts/patch_persistent_runtime.py'),str(src)],check=True)
p=src/'src/program/generate.cpp';s=p.read_text();assert s.count('o.adapt_decay != .7 ||')==1;p.write_text(s.replace('o.adapt_decay != .7 ||','o.adapt_decay != .7f ||'))
