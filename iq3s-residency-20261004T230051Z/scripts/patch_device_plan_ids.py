"""Preserve each layer's routed IDs when the GPU can run ahead of the host."""
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
def edit(path, old, new, count=1):
    path = source / path
    text = path.read_text()
    if text.count(old) != count:
        raise RuntimeError(f'Unexpected anchor count in {path}: {old[:80]}')
    path.write_text(text.replace(old, new, count))

header = 'include/strata/core/verify.hpp'
cpp = 'src/core/verify.cpp'
edit(header, '    bool device_plan_ = false;',
     '    bool device_plan_ids_ = false;       ///< Local serial-layer-split experiment; stable per-layer IDs\n'
     '    int32_t* h_plan_ids_ = nullptr;\n'
     '    int32_t* m_plan_ids_ = nullptr;\n'
     '    bool device_plan_ = false;')
edit(cpp, '    void* hosts[] = {h_tok_, h_step_, h_pos_, h_commit_, h_ple_, h_out_, h_x_, h_ids_, h_w_, h_seq_, h_flag_, h_ymiss_,',
     '    if (device_plan_ids_) { if (skip_) cudaFree(skip_); if (slot_off_d_) cudaFree(slot_off_d_); }\n'
     '    void* hosts[] = {h_plan_ids_, h_tok_, h_step_, h_pos_, h_commit_, h_ple_, h_out_, h_x_, h_ids_, h_w_, h_seq_, h_flag_, h_ymiss_,')
edit(cpp, '    // E-6: a layer whose routed experts are all resident is planned on the device',
     '''    const char* lab_ids = std::getenv("STRATA_LAB_PLAN_IDS");
    device_plan_ids_ = lab_ids && lab_ids[0] == '1';
    if (device_plan_ids_ && (all_resident_ || remote_opt_ || (lb_ == 0 && le_ == g.n_layers))) {
        err = "lab plan IDs: only the frozen serial mixed-cache layer-split path is supported";
        return false;
    }
    // E-6: a layer whose routed experts are all resident is planned on the device''')
edit(cpp, '    if (all_resident_ || device_plan_) {\n        bool ok2 = true;',
     '''    if (device_plan_ids_ && !device_plan_) {
        err = "lab plan IDs: STRATA_VERIFY_DEVICE_PLAN=1 is required";
        return false;
    }
    if (device_plan_ids_) {
        const size_t bytes = (size_t)(le_ - lb_) * (size_t)max_t_ * (size_t)ss.k * sizeof(int32_t);
        if (!mapped(bytes, (void**)&h_plan_ids_, (void**)&m_plan_ids_)) {
            err = "lab plan IDs: mapped per-layer ID allocation failed";
            return false;
        }
        std::fprintf(stderr, "strata lab plan IDs: stage [%lld,%lld), %zu mapped CPU bytes; device slot offsets %zu bytes plus64 skip bytes\\n",
                     (long long)lb_, (long long)le_, bytes, (size_t)hits.n_slots * sizeof(unsigned long long));
    }
    if (all_resident_ || device_plan_) {
        bool ok2 = true;''')
edit(cpp, '        if (!ok2) { cudaGetLastError(); all_resident_ = false; device_plan_ = false; }',
     '''        if (!ok2) {
            cudaGetLastError();
            if (device_plan_ids_) { err = "lab plan IDs: device-plan allocation failed"; return false; }
            all_resident_ = false; device_plan_ = false;
        }''')
# The following guard goes after the complete G declaration, including its comment.
edit(cpp, '    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");',
     '''    if (device_plan_ids_ && (G != 1 || batch_rec_)) {
        err = "lab plan IDs: split-token groups and concurrent slots are outside the validated experiment";
        return false;
    }
    static const bool dec_batch = [] { const char* v = std::getenv("STRATA_DEC_BATCH");''')
edit(cpp, '                                     m_x_ + tb * N, m_ids_ + tb * K, m_seq_, cs);',
     '''                                     m_x_ + tb * N,
                                     device_plan_ids_ ? m_plan_ids_ + (size_t)(l - lb_) * (size_t)max_t_ * K + tb * K
                                                      : m_ids_ + tb * K,
                                     m_seq_, cs);''')
edit(cpp, '            pool(user, h_x_ + (size_t) tb * g.n_embd, h_ids_ + (size_t) tb * ss.k, n, ss.k,',
     '''            pool(user, h_x_ + (size_t) tb * g.n_embd,
                 device_plan_ids_ ? h_plan_ids_ + (size_t)(l - lb_) * (size_t)max_t_ * (size_t)ss.k + (size_t)tb * ss.k
                                  : h_ids_ + (size_t)tb * ss.k,
                 n, ss.k,''')
edit(cpp, 'bool Verifier::init_slots(const std::vector<SessionState*>& slots, std::string& err) {',
     '''bool Verifier::init_slots(const std::vector<SessionState*>& slots, std::string& err) {
    if (device_plan_ids_) { err = "lab plan IDs: concurrent slot mode is not supported"; return false; }''')
print('Applied opt-in stable routed IDs for the frozen serial device-plan experiment', flush=True)
