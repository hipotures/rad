# Parallel queue startup failure

The four-worker joint-order queue failed before executing a configuration under Python3.14 forkserver bootstrap because its top-level process-pool code had no main guard. The complete nonsecret traceback remains external and will be gzip-published. No measurements from this attempt are reported. The corrected runner uses an explicit fork context on Linux; a new attempt is required before claiming a parallel reproduction.
