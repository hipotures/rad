"""Repair only missing first-head capture in a new diagnostic source/build."""
import pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1])
subprocess.run([sys.executable,str(root/'scripts/patch_diagnostic_direct_parts.py'),str(src)],check=True)
p=src/'src/program/generate.cpp';t=p.read_text()
old='                int a = 0;\n                while (a < T - 1 && window[(size_t) a + 1] == outv[(size_t) a]) ++a;'
new='''                if(first_window && strata::research::trace.enabled) {
                    std::vector<float> lab_logits((size_t)ver.vocab());
                    if(!ver.copy_logits(0,lab_logits.data())) {std::printf("ERR lab first head copy failed\\n");return 1;}
                    strata::research::trace.file(strata::research::trace.prefix+"-request"+std::to_string(strata::research::trace.request)+"-first-logits.bin",lab_logits);
                }
'''+old
assert t.count(old)==1;p.write_text(t.replace(old,new))
print('Diagnostic-only first-head capture repair; clean candidate unchanged')
