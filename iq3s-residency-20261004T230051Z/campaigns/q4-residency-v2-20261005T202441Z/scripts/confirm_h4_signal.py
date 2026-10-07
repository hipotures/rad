"""Predeclared H4 coverage transfer: three long contexts and three whole-task holdouts."""
from campaign import C,point,status,save,load

def main():
    with (C/'DECISIONS.md').open('a') as f:
        f.write('\nH4 selected for bounded signal transfer before runtime integration: on dev code its charged-spare ready persistent publications213 exceed H1118; H8 has weaker membership and an additional size-class spare. No predictor/calibration refit after held-out results. Collect H4 at3 long profiles and3 existing independent holdouts, once each, diagnostic-only.\n')
    for profile in ['32k','128k','256k']:point('cost-h4',profile,1,True)
    for payload in ['hold-code','hold-structured','hold-math']:point('cost-h4','32k',1,True,payload)
    status('B_H4_TRANSFER_COLLECTED',phase='B',running=None,next_exact_action='Analyze H4 transfer, freeze at most2 runtime finalists and write Phase B')
if __name__=='__main__':main()
