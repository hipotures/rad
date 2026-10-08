import Mathlib.Data.Finset.Max
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

/-!
# Positive type mixing cannot strictly contract every positive coordinate

Formalizes the finite nonnegative-matrix lemma in
`reports/transfers/positive-type-mixing.md` at research commit d1ef326f.
There is no integer-multiplication complexity claim in this module.
-/

open scoped BigOperators

namespace RaD.PositiveMixing

variable {ι : Type*} [Fintype ι]

/-- The actual finite weighted sum, not an assumed matrix interface. -/
def step (M : ι → ι → ℝ) (c : ι → ℝ) (i : ι) : ℝ :=
  ∑ j, M i j * c j

/-- The two explicit hypotheses of the obstruction. -/
def Admissible (M : ι → ι → ℝ) : Prop :=
  (∀ i j, 0 ≤ M i j) ∧ (∀ i, 1 ≤ ∑ j, M i j)

/-- Apply a finite list of complete levels, with the rightmost level first. -/
def word : List (ι → ι → ℝ) → (ι → ℝ) → (ι → ℝ)
  | [], c => c
  | M :: levels, c => step M (word levels c)

/-- Nonnegative row weights preserve pointwise vector inequalities. -/
theorem step_monotone (M : ι → ι → ℝ) (hM : ∀ i j, 0 ≤ M i j)
    (c d : ι → ℝ) (hcd : ∀ i, c i ≤ d i) :
    ∀ i, step M c i ≤ step M d i := by
  intro i
  exact Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_left (hcd j) (hM i j))

/-- A nonnegative constant lower bound survives each admissible level. -/
theorem step_lower_bound (M : ι → ι → ℝ) (hM : Admissible M)
    (c : ι → ℝ) (r : ℝ) (hr : 0 ≤ r) (hc : ∀ i, r ≤ c i) :
    ∀ i, r ≤ step M c i := by
  intro i
  change r ≤ ∑ j, M i j * c j
  calc
    r = 1 * r := (one_mul r).symm
    _ ≤ (∑ j, M i j) * r := mul_le_mul_of_nonneg_right (hM.2 i) hr
    _ = ∑ j, M i j * r := Finset.sum_mul _ _ _
    _ ≤ ∑ j, M i j * c j :=
      Finset.sum_le_sum (fun j _ => mul_le_mul_of_nonneg_left (hc j) (hM.1 i j))

/-- The lower bound survives every finite number of possibly different levels. -/
theorem word_lower_bound (levels : List (ι → ι → ℝ))
    (c : ι → ℝ) (r : ℝ) (hr : 0 ≤ r) :
    (∀ M ∈ levels, Admissible M) → (∀ i, r ≤ c i) →
      ∀ i, r ≤ word levels c i := by
  induction levels with
  | nil =>
      intro _ hc
      exact hc
  | cons M levels ih =>
      intro hlevels hc
      have hM : Admissible M := hlevels M (by simp)
      have htail : ∀ A ∈ levels, Admissible A := by
        intro A hA
        exact hlevels A (by simp only [List.mem_cons]; exact Or.inr hA)
      exact step_lower_bound M hM (word levels c) r hr (ih htail hc)

/-- A minimal positive coordinate cannot strictly decrease through the word. -/
theorem word_has_nondecreasing_coordinate [Nonempty ι]
    (levels : List (ι → ι → ℝ)) (hlevels : ∀ M ∈ levels, Admissible M)
    (c : ι → ℝ) (hc : ∀ i, 0 < c i) :
    ∃ i, c i ≤ word levels c i := by
  classical
  obtain ⟨i, _, hmin⟩ :=
    Finset.exists_min_image (Finset.univ : Finset ι) c Finset.univ_nonempty
  refine ⟨i, ?_⟩
  exact word_lower_bound levels c (c i) (le_of_lt (hc i)) hlevels
    (fun j => hmin j (Finset.mem_univ j)) i

/-- No strict positive supersolution exists, even after level alternation. -/
theorem word_no_positive_strict_contraction [Nonempty ι]
    (levels : List (ι → ι → ℝ)) (hlevels : ∀ M ∈ levels, Admissible M)
    (c : ι → ℝ) (hc : ∀ i, 0 < c i) :
    ¬ (∀ i, word levels c i < c i) := by
  intro hcontract
  obtain ⟨i, hi⟩ := word_has_nondecreasing_coordinate levels hlevels c hc
  exact (not_lt_of_ge hi) (hcontract i)

/-- The single-level statement used by the research note. -/
theorem no_positive_strict_contraction [Nonempty ι]
    (M : ι → ι → ℝ) (hM : Admissible M)
    (c : ι → ℝ) (hc : ∀ i, 0 < c i) :
    ¬ (∀ i, step M c i < c i) := by
  have hlevels : ∀ A ∈ [M], Admissible A := by
    intro A hA
    have heq : A = M := by simpa using hA
    subst A
    exact hM
  simpa only [word] using word_no_positive_strict_contraction [M] hlevels c hc

/-- Additional nonnegative conversion work cannot remove this obstruction. -/
theorem added_work_no_positive_strict_contraction [Nonempty ι]
    (levels : List (ι → ι → ℝ)) (hlevels : ∀ M ∈ levels, Admissible M)
    (c : ι → ℝ) (hc : ∀ i, 0 < c i)
    (work : ι → ℝ) (hwork : ∀ i, 0 ≤ work i) :
    ¬ (∀ i, word levels c i + work i < c i) := by
  intro hcontract
  obtain ⟨i, hi⟩ := word_has_nondecreasing_coordinate levels hlevels c hc
  have hpaid : c i ≤ word levels c i + work i :=
    hi.trans (le_add_of_nonneg_right (hwork i))
  exact (not_lt_of_ge hpaid) (hcontract i)

end RaD.PositiveMixing
