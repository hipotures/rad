import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from dependency_graph import span,union_length,conservative_counterfactual_bound
from protocol_rules import perturbation_gate,notify_tail
class GraphTests(unittest.TestCase):
 def test_wait_is_constraint(self):
  nodes=[('producer',10,[]),('gpu_pre',4,[]),('consumer',2,['producer','gpu_pre'])]
  self.assertEqual(span(nodes)[0],12);self.assertEqual(span(nodes,{'producer':3})[0],9)
 def test_shared_masks(self):
  nodes=[('ack',10,[]),('shared',15,[]),('resident',2,['ack']),('combine',1,['shared','resident'])]
  self.assertEqual(span(nodes)[0],16);self.assertEqual(span(nodes,{'ack':10})[0],16)
 def test_cpu_and_peer(self):
  nodes=[('ack',10,[]),('cpu',13,[]),('stage0',2,['ack','cpu']),('stage1',4,['stage0'])]
  self.assertEqual(span(nodes)[0],19);self.assertEqual(span(nodes,{'ack':9})[0],19)
 def test_union_no_double_count(self):self.assertEqual(union_length([(0,5),(2,7),(10,12)]),9)
 def test_missing_edge_not_zero(self):
  with self.assertRaises(ValueError):span([('consumer',2,['missing'])])
  self.assertEqual(conservative_counterfactual_bound([10],1),[0,1e-8])
 def test_fixed_scenario_and_symmetric_gate(self):
  self.assertEqual(notify_tail(100,80,10,15),15)
  for sign in (-1,1):self.assertFalse(perturbation_gate([{'decode_change_pct':sign*6,'wall_change_pct':0}]*3)['pass'])
if __name__=='__main__':unittest.main()
