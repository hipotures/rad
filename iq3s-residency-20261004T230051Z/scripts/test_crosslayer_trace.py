"""Synthetic regression for explicit victim layers and unchanged legacy trace decoding."""
import pathlib,tempfile,unittest
import numpy as np
from lab import ROOT,save
from trace_reader import Trace,ENTRY,LAYER,WINDOW,PROMOTION,PROMOTION_V2,REACH
class CrossLayerTrace(unittest.TestCase):
    def fixture(self,folder,version):
        p=str(pathlib.Path(folder)/'trace');initial=np.full((48,512),-1,np.int32)
        for l in range(48):initial[l,:10]=(l if l<25 else l-25)*10+np.arange(10)
        out_layer=1 if version==2 else 2;final=initial.copy();final[out_layer,3]=-1;final[2,20]=initial[out_layer,3]
        entries=np.zeros(480,ENTRY);layers=np.zeros(48,LAYER)
        for l in range(48):
            entries[l*10:(l+1)*10]['expert']=np.arange(10)
            entries[l*10:(l+1)*10]['slot']=final[l,:10]
            entries[l*10:(l+1)*10]['path']=np.where(final[l,:10]>=0,0,-1)
            layers[l]['window']=7;layers[l]['offset']=l*10;layers[l]['layer']=l;layers[l]['tokens']=1;layers[l]['k']=10
            for field in ['t0','t1','t2','t3','t4']:layers[l][field]=30+l*100
        windows=np.zeros(1,WINDOW);windows['number']=7;windows['T']=1;windows['produced']=1
        promotions=np.zeros(1,PROMOTION_V2 if version==2 else PROMOTION)
        for k,v in dict(window=7,issue=10,observed_ready=20,bytes=1024,layer=2,incoming=20,outgoing=3,slot=int(initial[out_layer,3])).items():promotions[k]=v
        if version==2:promotions['outgoing_layer']=out_layer;save(p+'-schema.json',{'version':2,'promotion_record_bytes':56,'cross_layer_victim':True})
        arrays={'initial':initial,'final':final,'initial-usage':np.zeros((48,512),np.float32),'final-usage':np.zeros((48,512),np.float32),'blob-bytes':np.full(48,1024,np.uint64),'slot-bytes-gpu0':np.full(250,1024,np.uint64),'slot-bytes-gpu1':np.full(230,1024,np.uint64),'entries':entries,'layers':layers,'windows':windows,'promotions':promotions,'reach':np.zeros(0,REACH),'output-ids':np.array([3],np.int32)}
        for key,a in arrays.items():a.tofile(p+'-'+key+'.bin')
        return p
    def test_legacy_same_layer(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'experiments/E012-compatible-diagnostic/v1') as folder:
            t=Trace(self.fixture(folder,1));self.assertEqual(t.validate()['state'],'PASS');self.assertEqual(t.schema['version'],1)
    def test_crosslayer_victim(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'experiments/E012-compatible-diagnostic/v1') as folder:
            t=Trace(self.fixture(folder,2));self.assertEqual(t.validate()['state'],'PASS');self.assertEqual(t.schema['version'],2)
    def test_wrong_victim_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'experiments/E012-compatible-diagnostic/v1') as folder:
            t=Trace(self.fixture(folder,2));t.promotions['outgoing_layer']=2;self.assertEqual(t.validate()['state'],'FAIL')
if __name__=='__main__':unittest.main()
