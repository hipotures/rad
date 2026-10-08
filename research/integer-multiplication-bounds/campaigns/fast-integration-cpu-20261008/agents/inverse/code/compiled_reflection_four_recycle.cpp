// Independent-node reflection stress controls, using the retained native
// implementation's actual F_u rotations and computed-key radix repairs.
// This file tests the reflection interface beyond pairwise-coprime CRT leaves.
// It is a finite address/payload model, not a fixed-tape complexity benchmark.
#define main retained_native_tree_main
#include "compiled_crt_native_recycle.cpp"
#undef main

struct ReflectionResult {
    unsigned N = 0;
    Word T = 0, S = 0;
    std::size_t events = 0;
    Word inner = 0, rotations = 0, repairs = 0, repair_records = 0;
    Word wrong = 0, nonzero_invalid = 0;
    unsigned donor_bits = 0;
    unsigned recycled_U_high_bits = 0, recycled_T_bits = 0;
};

static unsigned reflection_bank_bits(unsigned targets, unsigned target_bits, unsigned Gout, unsigned Gin) {
    unsigned K = Gin == 1 ? 8 : (target_bits <= 5 ? 6 : 8);
    unsigned H = ((target_bits + K - 1) / K) * Gin;
    // High outer U bits and all outer T bits are available inside the exact
    // inner shear; only the live parity sources must stay outside scratch.
    unsigned controls_and_scratch = std::max(2 * targets * Gout, targets + 3 * H);
    unsigned full_top_guard = 3 * H + (Gin == 1 ? 3 : K - 2);
    return std::max(controls_and_scratch, full_top_guard);
}

static ReflectionResult four_targets(const std::vector<Word>& moduli,
                                    unsigned Gout, unsigned Gin,
                                    bool borrow_left_control,
                                    bool omit_inner, bool omit_outer) {
    require(moduli.size() == 2 || moduli.size() == 4, "recycling fixture needs two or four targets");
    unsigned target_bits = 0;
    for (Word modulus : moduli) target_bits += bits(modulus - 1);
    unsigned donor_bits = reflection_bank_bits(moduli.size(), target_bits, Gout, Gin);
    unsigned N = 1 + target_bits + donor_bits;
    require(N <= 25, "standalone finite memory cap is25 bits");
    Word T = Word(1) << N;
    Shapes current{{2, 1}};
    Word S = 2;
    for (Word modulus : moduli) {
        current.push_back(Shape{modulus, bits(modulus - 1)});
        S *= modulus;
    }
    current.push_back(Shape{Word(1) << donor_bits, donor_bits});
    S <<= donor_bits;
    auto ff = fields(current);
    std::vector<Word> initial(T, 0);
    for (Word a = 0; a < T; ++a) if (valid(a, current)) initial[a] = a + 1;
    Machine machine(N, initial);
    std::vector<Node> nodes;
    for (unsigned i = 0; i < moduli.size(); ++i)
        nodes.push_back(Node{0, i + 1, 2, moduli[i], moduli[i] - 1});
    // The same fixed left BIT controls every offset. Its copies are
    // read-only sources; it is not part of the legal inactive bank.
    auto donors = ff.back().p;
    if (borrow_left_control) donors.front() = ff.front().p.front();

    // Independent oracle: when the source BIT is one, decrement each VALID
    // digit, with zero wrapping to modulus-1. Invalid digits are fixed.
    std::vector<Word> expected(T, UINT64_MAX);
    for (Word a = 0; a < T; ++a) {
        Word z = a;
        if (a & 1) {
            unsigned at = 1;
            for (Word modulus : moduli) {
                unsigned width = bits(modulus - 1);
                Word y = (a >> at) & mask(width);
                if (y < modulus) {
                    Word v = y ? y - 1 : modulus - 1;
                    z = (z & ~(mask(width) << at)) | (v << at);
                }
                at += width;
            }
        }
        require(expected[z] == UINT64_MAX, "independent rotation oracle collision");
        expected[z] = initial[a];
    }
    bool used = compiled(machine, nodes, ff, donors, current, Gout, Gin,
                         omit_inner, omit_outer);
    require(used, "four-target program silently fell back to ordinary rotation");
    require(machine.payload == expected, "independent four-target rotation oracle mismatch");
    for (Word a = 0; a < T; ++a)
        require(valid(a, current) || machine.payload[a] == 0,
                "completed four-target boundary contains nonzero invalid padding");
    auto metric = machine.metrics.back();
    unsigned recycled_U_high = 0, recycled_T = 0, selected = 0;
    for (unsigned i = 0; i < donors.size() && selected < metric.scratch; ++i) {
        if (i < moduli.size() * Gout && i % Gout == 0) continue;
        ++selected;
        if (i < moduli.size() * Gout) ++recycled_U_high;
        else if (i < 2 * moduli.size() * Gout) ++recycled_T;
    }
    require(selected == metric.scratch, "reported recycled selector lacks scratch bits");
    std::size_t event_count = machine.events.size();
    machine.reverse();
    require(machine.payload == initial, "complete four-target reverse mismatch");
    return {N, T, S, event_count, machine.inner_calls, machine.raw_rotations,
            machine.radix_repairs, machine.radix_records, metric.wrong,
            metric.padding, donor_bits, recycled_U_high, recycled_T};
}

int main(int argc, char** argv) {
    std::string family = "mixed-small", output;
    unsigned Gout = 1, Gin = 1;
    bool borrow_left = false, omit_inner = false, omit_outer = false;
    for (int i = 1; i < argc; ++i) {
        std::string option = argv[i];
        if (option == "--family" && i + 1 < argc) family = argv[++i];
        else if (option == "--output" && i + 1 < argc) output = argv[++i];
        else if (option == "--outer-guard" && i + 1 < argc) Gout = std::stoul(argv[++i]);
        else if (option == "--inner-guard" && i + 1 < argc) Gin = std::stoul(argv[++i]);
        else if (option == "--borrow-left-control") borrow_left = true;
        else if (option == "--omit-inner-repair") omit_inner = true;
        else if (option == "--omit-outer-repair") omit_outer = true;
        else { std::cerr << "unknown argument " << option << '\n'; return 2; }
    }
    std::vector<Word> moduli;
    if (family == "mixed-small") moduli = {2, 3, 4, 5};
    else if (family == "two-small") moduli = {2, 3};
    else if (family == "odd-wide") moduli = {3, 5, 7, 11};
    else { std::cerr << "unknown family\n"; return 2; }
    require(!output.empty(), "an explicit fresh certificate path is required");
    auto started = std::chrono::steady_clock::now();
    ReflectionResult result;
    unsigned target_bits = 0;
    for (Word modulus : moduli) target_bits += bits(modulus - 1);
    result.donor_bits = reflection_bank_bits(moduli.size(), target_bits, Gout, Gin);
    result.N = 1 + target_bits + result.donor_bits;
    result.T = Word(1) << result.N;
    result.S = 2 * (Word(1) << result.donor_bits);
    for (Word modulus : moduli) result.S *= modulus;
    std::string status = "PASS", error;
    bool negative = borrow_left || omit_inner || omit_outer;
    try {
        result = four_targets(moduli, Gout, Gin, borrow_left, omit_inner, omit_outer);
        if (negative) { status = "UNEXPECTED_NEGATIVE_PASS"; error = "invalid contract unexpectedly passed"; }
    } catch (const std::exception& exception) {
        error = exception.what();
        bool contract_failure = error.find("repair escaped bad set at ") == 0 ||
            error == "completed compiled node differs from modular rotation" ||
            error == "independent four-target rotation oracle mismatch" ||
            error == "complete four-target reverse mismatch";
        status = negative && contract_failure ? "EXPECTED_NEGATIVE" : "FAIL";
    }
    double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    std::ofstream out(output);
    require(bool(out), "cannot open explicit certificate output");
    out << "{\n  \"status\":\"" << status << "\",\n"
        << "  \"scope\":\"Exact completed inner shears recycle outer U high bits and outer T; finite full-payload map, not tape complexity\",\n"
        << "  \"family\":\"" << family << "\",\n"
        << "  \"target_moduli\":[";
    for (unsigned i = 0; i < moduli.size(); ++i) { if (i) out << ','; out << moduli[i]; }
    out << "],\n  \"target_count\":" << moduli.size()
        << ",\n  \"outer_guard_bits\":" << Gout
        << ",\n  \"inner_guard_bits\":" << Gin
        << ",\n  \"borrowed_left_control\":" << (borrow_left ? "true" : "false")
        << ",\n  \"omitted_inner_repair\":" << (omit_inner ? "true" : "false")
        << ",\n  \"omitted_outer_repair\":" << (omit_outer ? "true" : "false")
        << ",\n  \"error\":\"" << error << "\",\n"
        << "  \"address_bits\":" << result.N
        << ",\n  \"allocated_records\":" << result.T
        << ",\n  \"valid_tagged_records\":" << result.S
        << ",\n  \"original_bank_bits\":" << result.donor_bits
        << ",\n  \"recycled_outer_U_high_bits\":" << result.recycled_U_high_bits
        << ",\n  \"recycled_outer_T_bits\":" << result.recycled_T_bits
        << ",\n  \"added_address_bits\":0,\n"
        << "  \"events\":" << result.events
        << ",\n  \"actual_F_u_calls\":" << result.inner
        << ",\n  \"actual_F_u_rotations\":" << result.rotations
        << ",\n  \"actual_radix_repairs_forward_and_inverse\":" << result.repairs
        << ",\n  \"actual_radix_record_sum\":" << result.repair_records
        << ",\n  \"wrong_before_outer_repair\":" << result.wrong
        << ",\n  \"nonzero_invalid_before_outer_repair\":" << result.nonzero_invalid
        << ",\n  \"independent_rotation_oracle\":" << (status == "PASS" ? "true" : "false")
        << ",\n  \"full_reverse_pipeline\":" << (status == "PASS" ? "true" : "false")
        << ",\n  \"wall_seconds\":" << seconds
        << ",\n  \"workers\":1,\n  \"native_threads\":1\n}\n";
    std::cout << "{\"status\":\"" << status << "\",\"seconds\":" << seconds << "}\n";
    return status == "PASS" || status == "EXPECTED_NEGATIVE" ? 0 : 1;
}
