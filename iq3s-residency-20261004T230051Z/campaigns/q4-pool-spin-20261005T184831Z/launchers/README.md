# Selected frozen Q4 CPU-pool baseline

USE_100US

```bash
cd /srv/ai/research/iq3s-residency-20261004T230051Z/campaigns/q4-pool-spin-20261005T184831Z/launchers
./start-32k.sh --host 0.0.0.0 --port 8080
# or, one server at a time
./start-128k.sh --host 0.0.0.0 --port 8080
./stop.sh
```

Use one server at a time. Ctrl-C or stop.sh stops the identified owned process. --check prints/verifies config without starting inference. Source0.1.39, K24/.28, frozen binarySHA verified; model data pathv0132 does not select an old runtime. Logs are streamed and persisted under manual/.
