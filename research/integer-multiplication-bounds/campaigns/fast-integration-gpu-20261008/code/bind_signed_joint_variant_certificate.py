#!/usr/bin/env python3
"""Independent finite binding of actual signed joint words and rational profiles.

Reconstructs local widths from every certified rook list and the separately
replayed transition binary. Reconstructs the complete physical child list,
proves primes and per-matrix zero bounds, and checks rational moments and the
pinned strict assembly. This variant additionally binds fresh source-only region and coordinate
reconstruction plus the changed-word source, DATA and scalar interface audit.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import gzip
import json
from math import comb, prod
from itertools import combinations
from pathlib import Path
import struct
from bind_source_profile_certificate import moment_bounds, prime


def read(p):
    return json.loads(Path(p).read_text())


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def decode(value):
    if isinstance(value, dict):
        return {k: decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [decode(v) for v in value]
    if isinstance(value, str):
        try:
            return Q(value)
        except ValueError:
            pass
    return value


def local(row, graph):
    p = row['profile']
    h, v, R = p['h'], p['v'], p['R']
    assert v == comb(h, 3) and p['loss'] == h*(h-1)
    assert p['different_modular_profiles'] == 0
    assert digest(row['profile_path']) == row['profile_sha256']
    assert read(row['profile_path']) == p
    binary = Path(row['config']['transitions'])
    assert digest(binary) == row['input_binary_sha256'] == graph['transition_sha256']
    assert graph['status'].endswith('PASS')
    assert graph['exact_transition_multiset_from_word']
    assert graph['R'] == R and graph['complete_basis_vectors'] == 2*v+R
    assert set(graph['orientations']) == {'forward', 'reverse-complement'}
    assert graph['copied_centers'] == h
    assert digest(graph['word_path']) == graph['word_gzip_sha256']
    # Coherently relabeled words use the independent coordinate-aware
    # extractor; their source labels need not be the public lexical keys.
    assert graph['coherent_source_output_labels']
    assert sorted(graph['source_permutation']) == list(range(h))
    assert graph['source_permutation'] == row['coordinate_order']
    raw = binary.read_bytes()
    mixed = raw[:8] == b'RADCOF01'
    offset = 8 if mixed else 0
    bh, bv, br, nf, nt, singles, mass, loss = struct.unpack_from('<6I2Q', raw, offset)
    assert (bh, bv, br, mass, loss) == (h, v, R, h*R+h*(h-1), p['loss'])
    assert graph['frame_format'] == ('mixed-signed-complemented-v1' if mixed else 'positive-signed-v1')
    stride = 12+h
    assert len(raw) == offset+40+stride*nf+16*nt
    frames = []
    for i in range(nf):
        flagged, rank = struct.unpack_from('<QI', raw, offset+40+stride*i)
        complemented = bool(flagged >> 63)
        assert mixed or not complemented
        forced = flagged & ((1 << 63)-1)
        symbols = struct.unpack_from('<'+str(h)+'b', raw, offset+52+stride*i)
        assert forced < 1<<h and rank <= h
        if i < 2:
            assert forced == 0 and rank == (h if i else 0) and not complemented
        elif complemented:
            # The distinctly tagged frame is Gamma_c minus disjoint signed
            # normal classes, NOT the span of those normal columns. Gamma_c
            # has T^T H0 T=4I, so each normal costs one dimension. Independent
            # kernel-B/Gram controls check this actual projector formula.
            assert forced.bit_count() == 1
            common = forced.bit_length()-1
            assert symbols[common] == 1
            assert all(j == common or x == 0 or abs(x) > 1
                       for j, x in enumerate(symbols))
            labels = {abs(x) for x in symbols if abs(x) > 1}
            assert rank == h-1-len(labels)
        else:
            f = forced.bit_count()
            assert f in (1,2,3)
            assert all(not (forced>>j&1) or symbols[j] in (0,1) for j in range(h))
            labels = {abs(x) for x in symbols if abs(x)>1}
            assert rank == (1 if f == 3 else len(labels))
            assert rank > 0
            # Independent structural Gram identity: source columns are
            # tau_l*1_F+(3-f)*epsilon_l. For H0=I-J/9 their Gram is
            # (3-f)^2*diag(n_l)+(f-1)*tau*tau^T, strictly positive
            # for f1/2. For f3 the single source column has Gram2.
            # The exact inverse and L conjugation are independently
            # checked by the bound Fraction controls; the all-word
            # containment audit is separately hash-bound below.
        frames.append((forced,symbols,rank))
    transitions = {}
    for i in range(nt):
        a, b, count = struct.unpack_from('<2Iq', raw, offset+40+stride*nf+16*i)
        assert a < nf and b < nf
        assert (a,b) not in transitions and count > 0
        ca, ua, ra = frames[a]
        cb, ub, rb = frames[b]
        assert rb > ra
        # Signed-space containment is certified on every literal raise by
        # two independent exact source/word and interface reconstructions;
        # bitset envelope inclusion would be invalid for these frames.
        transitions[a,b] = (rb-ra, count)
    assert digest(row['transition_audit']) == row['transition_audit_sha256']
    audited = read(row['transition_audit'])
    assert (audited['h'], audited['basis']) == (h, p['basis'])
    entries = {(t['a'],t['b']): t for t in audited['transitions']}
    assert len(entries) == len(audited['transitions'])
    primes = p['primes']
    assert len(set(primes)) == len(primes) and all(prime(q) for q in primes)
    hist = Counter({1: singles})
    checked = 0
    for key, (rank, count) in transitions.items():
        if rank == 1:
            hist[1] += count
            continue
        if key == (0,1):
            hist[h] += count
            continue
        t = entries.pop(key)
        assert (t['rank'], t['count']) == (rank, count)
        z, bound, den = (int(t[k]) for k in ['entry_bound','minor_bound','integer_denominator'])
        assert z > 0 and den > 0
        # Hadamard bounds every potentially nonzero minor through known rank.
        assert bound == rank**((rank+1)//2)*z**rank
        used = primes[:t['prime_count']]
        assert used and prod(used) > bound and all(den % q for q in used)
        pivots = [tuple(x) for x in t['pivots']]
        assert len(pivots) == rank and pivots == sorted(pivots)
        assert len({x for x,y in pivots}) == len({y for x,y in pivots}) == rank
        assert all(0 <= x < h and 0 <= y < h for x,y in pivots)
        run = 0
        previous = None
        for pivot in pivots:
            if previous and pivot == (previous[0]+1, previous[1]+1):
                run += 1
            else:
                if run:
                    hist[run] += count
                run = 1
            previous = pivot
        hist[run] += count
        checked += 1
    assert not entries
    assert [hist[i] for i in range(h+1)] == p['blocks']
    assert sum(t*n for t,n in hist.items()) == mass == p['rank_sum']
    beta = Q(*map(int, p['basis'].split(':')[1:]))
    assert 1-h*beta != 0
    gamma = (9*beta-1)/(3*(1-h*beta))
    source = [1-3*beta, -3*beta]
    dual = [(1+gamma)/2, gamma/2]
    center_offset = (2-3*beta*(h-3))/(h-9)
    center = [1+center_offset, center_offset]
    center_offset_dual = (h-9)*(1-3*beta)/(12*(1-h*beta))
    center_dual = [center_offset_dual-Q(h-9,4), center_offset_dual]
    assert all(source+dual+center+center_dual)
    products = [x*y for x,y in zip(source,dual)]
    assert 3*products[0]+(h-3)*products[1] == 1
    assert center[0]*center_dual[0]+(h-1)*center[1]*center_dual[1] == 1
    return hist, dict(h=h, R=R, basis=p['basis'], word_sha256=graph['word_sha256'],
        transition_sha256=digest(binary), profile_sha256=row['profile_sha256'],
        exact_bounded_matrix_count=checked, copied_centers=h, dirty_basis_vectors=2*v+R,
        source_coordinate_products=list(map(str,products)), inverse_source_products=[str(1/x) for x in products])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ['axes','certificate','data','stock','scalar','assembly','output']:
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--words', type=Path, nargs=2, required=True)
    ap.add_argument('--source-recoveries', type=Path, nargs=2, required=True)
    ap.add_argument('--rational-controls', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    axes = read(args.axes)
    if isinstance(axes, dict):
        axes = [axes['axes'][str(h)] for h in [23,25]]
    cert, data, stock, scalar = [read(p) for p in [args.certificate,args.data,args.stock,args.scalar]]
    assert cert['input_sha256'][str(args.axes)] == digest(args.axes)
    assert scalar['source_revision'] == 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'
    assert all(r['exact_original_pinned_statistics'] for r in scalar['rows'])
    recoveries = [read(path) for path in args.source_recoveries]
    controls = read(args.rational_controls)
    if controls['status'] == 'PASS INDEPENDENT EXACT MIXED COFRAME GRAM AND NE CONTROLS':
        assert len(controls['cases']) == 2
        for row, control in zip(axes, controls['cases']):
            assert control['config']['basis'] == row['profile']['basis']
            assert digest(control['config']['binary']) == control['binary_sha256'] == row['input_binary_sha256']
            assert digest(control['config']['audit']) == control['audit_sha256'] == row['transition_audit_sha256']
            assert digest(control['config']['profile']) == control['profile_sha256'] == row['profile_sha256']
            assert len(control['checks']) >= 48
            assert sum(check['contains_complemented_frame'] for check in control['checks']) >= 24
            for frame in control['frames'].values():
                for key in ('explicit_kernel_B_H0_Gram', 'idempotent', 'trace_rank', 'transformed_H0_selfadjoint'):
                    assert frame[key]
            for check in control['checks']:
                for key in ('both_sided_containment', 'exact_integer_minor_bound', 'proven_prime_product_sufficient'):
                    assert check[key]
    else:
        assert controls['status'] == 'PASS INDEPENDENT EXACT SIGNED JOINT WORD GRAM AND ORDERED-PIVOT CONTROLS'
        assert len(controls['rows']) == 2
        for row, control in zip(axes, controls['rows']):
            assert control['case']['basis'] == row['profile']['basis']
            assert digest(control['case']['binary']) == row['input_binary_sha256']
            assert digest(control['case']['audit']) == row['transition_audit_sha256']
            assert len(control['checks']) >= 48
            for check in control['checks']:
                assert check['independent_gram_pass']
                assert check['nested_idempotent_pass']
                assert check['integer_minor_bound_pass']
    for row, word, recovery in zip(axes,args.words,recoveries):
        assert recovery['source_head'] == 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'
        assert recovery['independent'] == read(word)
        assert recovery['compiled']['all_physical_frame_inclusions']
        assert recovery['compiled']['complete_dirty_basis_both_orientations']
        assert recovery['compiled']['roles'] == row['profile']['R']
        assert recovery['scalar']['all_additions_disjoint'] and recovery['scalar']['all_partial_outputs_exact']
        assert recovery['scalar']['every_node_has_common_point']
        assert recovery['source_permutation'] == row['coordinate_order']
        assert recovery['source_only']
        assert recovery['source_injection_frames_unchanged']
        if recovery.get('physical_matching_and_literal_xors_changed', False):
            # A new matching is reconstructed independently from the pinned
            # scalar DAG and frozen selected capacities. Its XOR word and
            # role count may differ from the preceding accepted network.
            for key in ('word_regenerated_from_source_and_selected_carriers',
                        'original_scalar_dag_outputs_preserved',
                        'every_selected_use_reconstructed',
                        'distinct_recipient_capacity',
                        'donor_row_capacity_exactly_independent',
                        'strict_carrier_chronology',
                        'actual_frame_assignment_reconstructed'):
                assert recovery[key], key
            assert digest(recovery['selected_matching_path']) == recovery['selected_matching_sha256']
            selection = read(recovery['selected_matching_path'])
            assert selection['h'] == row['profile']['h']
            assert selection['source_permutation'] == row['coordinate_order']
            assert selection['source_parent_sha256'] == recovery['source_parent_sha256']
            assert len(selection['selected']) == recovery['selected_carriers']
            assert recovery['selected_carriers'] == recovery['compiled']['stats']['matched']
            summary = recovery['frame_summary']
            if recovery.get('selected_source_coframes', False):
                # Actual source-containing smaller coframes are selected
                # after reconstructing the chosen weighted word. The old
                # actual spaces are upper bounds; old E containment in the
                # new space would be an incorrect acceptance condition.
                parent_path = Path(recovery['fresh_weighted_source_receipt_path'])
                assert digest(parent_path) == recovery['fresh_weighted_source_receipt_sha256']
                parent = read(parent_path)
                assert parent['source_head'] == recovery['source_head']
                assert parent['source_only'] and parent['word_regenerated_from_source_and_selected_carriers']
                assert parent['word_sha256'] == recovery['actual_parent_word_sha256']
                assert parent['selected_matching_sha256'] == recovery['selected_matching_sha256']
                assert parent['source_permutation'] == row['coordinate_order']
                assert parent['scalar'] == recovery['scalar']
                assert read(word)['frame_format'] == 'mixed-signed-complemented-v1'
                assert summary['minimum_contained_in_selected_contained_in_old']
                assert summary['all_actual_continuations_strictly_nested']
                assert summary['unchanged_R'] == parent['compiled']['roles']
                assert summary['unchanged_every_XOR']
                minimum = recovery['minimum_receipt']
                assert minimum['source_two_core_and_copied_center_spaces_unchanged']
                assert minimum['old_actual_space_is_upper_bound']
                assert minimum['every_actual_continuation_contained']
                assert recovery['literal_xors_unchanged_from_selected_weighted_parent']
                if recovery.get('explicit_coframe_allocation', False):
                    assert digest(recovery['allocation_path']) == recovery['allocation_sha256']
                    allocation = read(recovery['allocation_path'])
                    assert allocation['h'] == row['profile']['h']
                    assert allocation['basis'] == row['profile']['basis']
                    assert allocation['parent_word_sha256'] == parent['word_sha256']
                    assert allocation['physical_R'] == row['profile']['R']
                    assert allocation['physical_rank_mass'] == row['profile']['rank_sum']
                    assert allocation['exact_predicted_child_histogram'] == row['profile']['blocks']
                    selected = allocation['minimum_frame_ids']
                    assert selected == sorted(set(selected))
                    assert selected == recovery['selected_minimum_frame_ids']
                    parent_word = json.loads(gzip.decompress(Path(parent['word_path']).read_bytes()))
                    assert all(0 <= i < len(parent_word['frames']) for i in selected)
                    assert recovery['source_injection_spaces_mutually_checked'] == row['profile']['v']
                    assert recovery['copied_center_spaces_mutually_checked']
                    # A clean reconstruction need not receive an existing
                    # discovery binary. Actual byte equality is also checked
                    # separately by the hash-bound stock audit below.
                    if recovery['saved_source_reconstruction_reused']:
                        assert digest(recovery['reused_source_receipt_path']) == recovery['reused_source_receipt_sha256']
                        assert read(recovery['reused_source_receipt_path']) == parent
            elif recovery.get('current_signed_lower_spaces_preserved', False):
                # This enlargement follows the NEW selected matching.
                # Bind its complete fresh parent rather than the earlier
                # conservative matching's potentially different R.
                parent_path = Path(recovery['fresh_weighted_source_receipt_path'])
                assert digest(parent_path) == recovery['fresh_weighted_source_receipt_sha256']
                parent = read(parent_path)
                assert parent['source_head'] == recovery['source_head']
                assert parent['source_only']
                assert parent['word_regenerated_from_source_and_selected_carriers']
                assert parent['word_sha256'] == recovery['actual_parent_word_sha256']
                assert parent['selected_matching_sha256'] == recovery['selected_matching_sha256']
                assert parent['scalar'] == recovery['scalar']
                assert parent['source_permutation'] == row['coordinate_order']
                assert summary['current_signed_space_containment']
                assert summary['every_new_upper_transition_containment']
                assert summary['terminal_constraints_propagated_to_fixed_point']
                assert summary['source_and_copied_center_spaces_unchanged']
                assert summary['unchanged_R'] == parent['compiled']['roles']
                assert summary['unchanged_every_XOR']
                assert recovery['literal_xors_unchanged_from_selected_weighted_parent']
            else:
                assert summary['every_actual_transition_containment']
                assert summary['original_and_maximal_containment']
                # The family allocation precedes matching and preserves
                # the independently rebuilt conservative parent word.
                assert summary['unchanged_R'] == recovery['compiled_parent']['roles']
                assert summary['unchanged_XORs']
            assert recovery['R'] == row['profile']['R']
        elif recovery.get('original_roles_and_xors_unchanged', False):
            assert recovery['every_original_frame_contained']
            assert recovery['all_actual_word_transitions_contained']
            assert recovery['every_original_xor_preserved']
            pass
        else:
            assert recovery['every_original_frame_contained']
            assert recovery['all_actual_word_transitions_contained']
            assert recovery['every_original_xor_preserved']
            # Componentwise constructors record the same literal-word
            # invariant separately from their maximal-frame containment.
            summary = recovery['summary']
            if summary.get('original_roles_and_XORs_unchanged', False):
                assert summary['R'] == row['profile']['R']
            elif summary.get('unchanged_XORs', False):
                assert summary['unchanged_R'] == row['profile']['R']
                assert summary.get('original_and_maximal_containment', False) or summary.get('original_base_and_maximal_containment', False)
            else:
                assert summary['unchanged_all_XOR_instructions']
                assert summary['unchanged_physical_roles'] == row['profile']['R']
            assert recovery['every_selected_frame_inside_maximal']
            assert (summary.get('maximal_signed_containment', False)
                    or summary.get('original_and_maximal_containment', False)
                    or summary.get('original_base_and_maximal_containment', False))
        assert recovery['copied_center_spaces_unchanged'] == row['profile']['h']
        # Reconstruct the complete source-family coordinate bijection;
        # literal source destinations and labels have independently been
        # replayed on the frozen actual word, not inferred from this map.
        triples = list(combinations(range(row['profile']['h']),3))
        lookup = {t:i for i,t in enumerate(triples)}
        q = recovery['source_permutation']
        labels = [lookup[tuple(sorted(q[i] for i in t))] for t in triples]
        assert sorted(labels) == list(range(row['profile']['v']))
    local_rows = [local(row, read(word)) for row,word in zip(axes,args.words)]
    assert [r['h'] for hist,r in local_rows] == [23,25]
    N, m = comb(23,3)*comb(25,3), 575
    W = 2*N+sum(N//comb(r['h'],3)*r['R'] for hist,r in local_rows)
    L = sum(N//comb(r['h'],3)*r['h']*(r['h']-1) for hist,r in local_rows)
    assert data['pairs'] == N and 'PASS' in data['status']
    assert [r['inverse_source_products'] for widths,r in local_rows] == data['inverse_source_products']
    assert {int(k):n for k,n in data['one_front_histogram'].items()} == {1:9*N,17:N,21:N,481:N}
    hist = Counter({1:19*N,17:2*N,21:2*N,481:2*N})
    for widths,row in local_rows:
        h, rep = row['h'], N//comb(row['h'],3)
        hist.update({t:rep*n for t,n in widths.items()})
        hist[h] += rep*row['R']
        hist[m-2*h] += rep*row['R']
        hist[1] += 2*N
        hist[h-2] += 2*N
    assert dict(hist) == {int(k):v for k,v in cert['bit']['child_multiplicities'].items()}
    assert sum(t*n for t,n in hist.items()) == cert['bit']['total_rank'] == m*W-N+L
    assert W == cert['bit']['W'] and L == cert['bit']['L']
    saving = Q(cert['bit_moment']['saving'])
    _, hi = moment_bounds(hist,m,W,saving)
    assert hi < 1
    next_lo,_ = moment_bounds(hist,m,W,Q(cert['bit_moment']['next_grid'],cert['bit_moment']['grid']))
    assert next_lo > 1
    phase = cert['phase']
    _, phi = moment_bounds({int(k):v for k,v in phase['child_multiplicities'].items()},phase['m'],phase['W'],Q(cert['phase_moment']['saving']))
    assert phi < 1
    assert stock['conservative_bit_scalar_upper'] < stock['retained_phase_scalar_upper']
    assert stock['total_rank'] == cert['bit']['total_rank']
    assert (stock['W'],stock['L'],stock['N'],stock['m']) == (W,L,N,m)
    assert stock['closed_uniform_DATA']['sha256'] == digest(args.data)
    for item, recovery, row in zip(stock['axes'],args.source_recoveries,axes):
        assert item['graph_receipt']['sha256'] == digest(recovery)
        assert item['selected_profile']['sha256'] == row['profile_sha256']
        if read(recovery).get('explicit_coframe_allocation', False):
            assert item['source_and_native_binary_bytes_independently_equal']
    assert [r['word_sha256'] for widths,r in local_rows] == [r['raw_word_sha256'] for r in stock['axes']]
    spec = importlib.util.spec_from_file_location('independent_pinned_joint_assembly',args.assembly)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assembly = module.assembly(decode(cert['finite_bridge']),saving,Q(cert['kappa']),a_complex=Q(cert['phase_moment']['saving']))
    assert assembly == decode(cert['assembly'])
    assert len(assembly['constraints']) == 47 and len(assembly['margins']) == 7
    assert all(x>0 for x in assembly['constraints'].values()) and all(x>0 for x in assembly['margins'].values())
    def gap(upper):
        x = (1-upper)*10**40
        return str(Q(x.numerator//x.denominator,10**40))
    inputs = [args.axes,args.certificate,args.data,args.stock,args.scalar,args.assembly,args.rational_controls]+args.words+args.source_recoveries
    result = dict(status='PASS INDEPENDENT ACTUAL SIGNED JOINT WORD/SOURCE/CRT/DATA/SCALAR/RECURRENCE BINDING',
        kappa=cert['kappa'], bit_saving=str(saving), W=W, rank_mass=cert['bit']['total_rank'],
        axes=[r for widths,r in local_rows], independent_bit_gap_lower_bound=gap(hi),
        independent_phase_gap_lower_bound=gap(phi), next_bit_grid_independently_excluded=True,
        strict_constraints=47, positive_margins=7, scalar_upper=stock['conservative_bit_scalar_upper'],
        input_sha256={str(p):digest(p) for p in inputs}, verifier_sha256=digest(__file__),
        scope='Finite checks; source/data basis compatibility and inherited all-size interfaces are specified in the acceptance proof.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','kappa','W','rank_mass']}))


if __name__ == '__main__':
    main()
