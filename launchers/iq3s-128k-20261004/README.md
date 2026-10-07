# IQ3_S 128K launchers

Run exactly one launcher at a time. Stop it with Ctrl+C before switching.
All three serve on 0.0.0.0:8080, with chat at http://SERVER_IP:8080/ and OpenAI API at http://SERVER_IP:8080/v1.
Max context is 131072, including input and output. Model weights and old benchmark configs remain unchanged.

- start-helper-priority.sh: local algorithm patch, best historical 128K median TG 125.1 tok/s; PP 2355.7.
- start-layer-split-v0138.sh: pristine v0.1.38, historical median TG 120.5, best single run 130.3; PP 5707.1.
- start-layer-split-v0139-pcie028.sh: pristine frozen v0.1.39 binary strata-original, historical median TG 118.0; PP 5741.3.

Historical timings used max-context 262144, not 131072. These new 128K configs have not been loaded or speed-tested.
Layer split remains auto (historically K=25); selected K and auto expert slots may change at 128K. Helper numeric capacities remain identical to its benchmark.
MTP=4/min-p=0.5, INT8 KV, KV resident=32768 and all other engine args are copied from the respective saved configs.
Suffix lookup is OFF explicitly for the two helper/modern benchmark configs; the v0.1.38 historical config retains its default lookup behavior.
No benchmark prompt policy is injected into user requests. No telemetry collector is launched.
Extra server arguments can be appended, for example --port 8081.
Logs are in logs/; manifest.json records original configs and verified binary hashes.
