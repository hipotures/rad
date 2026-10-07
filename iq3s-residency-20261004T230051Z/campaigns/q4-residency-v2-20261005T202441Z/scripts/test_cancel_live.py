"""Intentional client cancellation, late copy drain, then a valid next request."""
from campaign import C,load,save,V2Session,guard
from lab import api
import json,socket,time,urllib.request

def main():
    guard();path=C/'correctness/early-client-cancel';assert not path.exists(),'Preserve previous cancellation attempt'
    cfg=load(C/'configs/early-delayed-32k.json');cfg['env']['STRATA_Q4_EARLY_LOG']=str(path/'early-events')
    cfg['build_variant']='early-client-cancel';cfg['headline_instrumentation']='DIAGNOSTIC_ONLY intentional client disconnect with5000us copy delay'
    with V2Session(C,cfg,path,'32k',port=18136) as s:
        warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID'
        payload=load(C/'inputs/warmup.json');payload['max_tokens']=4096
        save(path/'raw/cancel-request.json',payload);s.capture_requests+=1
        request=urllib.request.Request(s.url+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        started=time.time();chunks=[]
        with urllib.request.urlopen(request,timeout=120) as response:
            for line in response:
                if line.startswith(b'data:') and line[5:].strip()!=b'[DONE]':
                    chunk=json.loads(line[5:]);chunks.append({'elapsed_s':time.time()-started,'chunk':chunk})
                    if len(chunks)>=16:
                        # Deliberately close the owned client while the native request runs.
                        response.fp.raw._sock.shutdown(socket.SHUT_RDWR)
                        break
        save(path/'raw/cancel-stream-prefix.json',chunks)
        deadline=time.time()+60;idle=False
        while time.time()<deadline:
            metrics=api(s.url,'/metrics') or {}
            if (metrics.get('live') or {}).get('state')=='idle':idle=True;break
            time.sleep(.2)
        assert idle,'Cancelled request did not drain within60s'
        idle_after_s=time.time()-started
        cancelled_ids=path/'raw/output-ids-request2.json'
        completed_after_disconnect=load(cancelled_ids) if cancelled_ids.exists() else None
        after=api(s.url,'/metrics');save(path/'raw/after-cancel-metrics.json',after)
        text=(path/'logs/engine.log').read_text()
        assert 'Q4_EARLY_FATAL' not in text and 'Q4_EARLY_WORKER_FAIL' not in text
        # The next request exercises restored residency plus worker/state reuse.
        next_request=s.request('warmup','after-cancel','warmup')
        assert next_request['state']=='VALID' and next_request['actual_output_tokens']==64 and next_request['actual_engine_input_verified']
        assert (path/'early-events-request2.jsonl').exists(),'Cancellation must execute request-end early drain/restore'
        save(path/'results.json',{'PASS':True,'diagnostic_only':True,'intentional_cancel':True,'client_chunks_before_disconnect':len(chunks),
            'idle_observed_within_s':idle_after_s,'warmup':warm,'next_request':next_request,
            'captured_output_ids_after_disconnect':len(completed_after_disconnect) if completed_after_disconnect is not None else None,
            'limits':'Client disconnect after16SSE messages, not16tokens. Service may finish rather than interrupt native generation; the capture records emitted IDs observed by the common wrapper, not unconsumed native work. Copy delay exercises late/pending drain; exact worker state at disconnect was not instrumented. No headlineTG from cancellation.'})
    save(C/'phase-c/cancellation-test.json',load(path/'results.json'))
    print('CLIENT_CANCEL_DRAIN_NEXT_REQUEST_PASS',flush=True)

if __name__=='__main__':main()
