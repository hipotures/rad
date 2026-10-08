import RaD.PositiveMixing
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Algebra.BigOperators.Fin

/-! Exact boundary witnesses: these expose the scope of the main theorem. -/
namespace RaD.PositiveMixing

/-- Row mass exactly one excludes strict contraction, but permits equality. -/
theorem identity_boundary :
    Admissible (fun (_ _ : Fin 1) => (1 : ℝ)) ∧
    (∀ i : Fin 1, step (fun _ _ => (1 : ℝ)) (fun _ => 2) i = 2) := by
  constructor
  · constructor
    · intro i j
      norm_num
    · intro i
      norm_num
  · intro i
    norm_num [step]

/-- Dropping the row-mass hypothesis really permits positive contraction. -/
theorem subunit_row_counterexample :
    (∀ i : Fin 1, step (fun _ _ => (1 / 2 : ℝ)) (fun _ => 1) i < 1) := by
  intro i
  norm_num [step]

/-- Signed entries can invalidate the obstruction even with unit row sums. -/
def signedMatrix (i j : Fin 2) : ℝ :=
  if i = 0 then (if j = 0 then 2 else -1)
  else (if j = 0 then 3 else -2)

def positiveVector (i : Fin 2) : ℝ := if i = 0 then 1 else 2

theorem signed_cost_counterexample :
    (∀ i : Fin 2, 0 < positiveVector i) ∧
    (∀ i : Fin 2, (∑ j, signedMatrix i j) = 1) ∧
    (∀ i : Fin 2, step signedMatrix positiveVector i < positiveVector i) := by
  constructor
  · intro i
    fin_cases i <;> norm_num [positiveVector]
  · constructor
    · intro i
      fin_cases i <;> norm_num [signedMatrix, Fin.sum_univ_two]
    · intro i
      fin_cases i <;> norm_num [step, signedMatrix, positiveVector, Fin.sum_univ_two]

/-- A negative potential invalidates the minimum-coordinate argument. -/
theorem negative_potential_counterexample :
    Admissible (fun (_ _ : Fin 1) => (2 : ℝ)) ∧
    (∀ i : Fin 1, step (fun _ _ => (2 : ℝ)) (fun _ => -1) i < -1) := by
  constructor
  · constructor
    · intro i j
      norm_num
    · intro i
      norm_num
  · intro i
    norm_num [step]

end RaD.PositiveMixing
