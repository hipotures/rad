// Distinguish zero-padding blindness from exact outer repair containment.
// This finite diagnostic tags EVERY original address, including invalid slots.
#define main retained_native_tree_main
#include "compiled_crt_native_recycle.cpp"
#undef main

static Word desired(Word a, const std::vector<Bits>& ff) {
    if (!(a & 1)) return a;
    for (unsigned i = 1; i <= 2; ++i) {
        Word period = i == 1 ? 2 : 3, value = ff[i].get(a);
        if (value < period)
            a = ff[i].replace(a, value ? value - 1 : period - 1);
    }
    return a;
}

int main(int argc, char** argv) {
    std::string mode = "completed", output;
    for (int i = 1; i < argc; ++i) {
        std::string option = argv[i];
        if (option == "--mode" && i + 1 < argc) mode = argv[++i];
        else if (option == "--output" && i + 1 < argc) output = argv[++i];
        else { std::cerr << "unknown argument\n"; return 2; }
    }
    require(!output.empty(), "fresh output is required");
    require(mode == "completed" || mode == "omit-inner" || mode == "raw-fanout",
            "unknown exploratory mode");
    auto start = std::chrono::steady_clock::now();
    unsigned N = 19, bank = 15, Gout = 2, Gin = 3;
    Word T = Word(1) << N;
    Shapes current{{2,1},{2,1},{3,2},{Word(1)<<bank,bank}};
    auto ff = fields(current);
    auto donors = ff.back().p;
    std::vector<Word> initial(T), expected(T, UINT64_MAX);
    std::iota(initial.begin(), initial.end(), Word(1));
    Machine machine(N, initial);
    std::vector<Node> nodes{{0,1,2,2,1},{0,2,2,3,2}};
    std::string error;
    bool returned = false;
    try {
        if (mode == "raw-fanout") {
            std::vector<unsigned> parity{donors[0],donors[2]}, scratch;
            for (unsigned bit : donors)
                if (bit != parity[0] && bit != parity[1] && scratch.size() < 9)
                    scratch.push_back(bit);
            std::vector<unsigned> target{ff[1].p[0],ff[2].p[0],ff[2].p[1]};
            std::vector<unsigned> owner{0,1,1};
            fanout(machine,target,parity,scratch,owner,8,Gin,true);
            for (Word a = 0; a < T; ++a) {
                Word z = a;
                for (unsigned i = 0; i < target.size(); ++i)
                    z ^= ((a >> parity[owner[i]]) & 1) << target[i];
                require(expected[z] == UINT64_MAX, "fanout oracle collision");
                expected[z] = a + 1;
            }
        } else {
            for (Word a = 0; a < T; ++a) expected[desired(a,ff)] = a + 1;
            compiled(machine,nodes,ff,donors,current,Gout,Gin,
                     mode == "omit-inner",false);
        }
        returned = true;
    } catch (const std::exception& exception) {
        error = exception.what();
    }
    Word wrong = 0, wrong_valid = 0, wrong_invalid = 0;
    Word first = UINT64_MAX;
    for (Word a = 0; a < T; ++a) if (machine.payload[a] != expected[a]) {
        ++wrong;
        (valid(a,current) ? wrong_valid : wrong_invalid)++;
        if (first == UINT64_MAX) first = a;
    }
    bool reversed = false;
    std::string inverse_error;
    try {
        machine.reverse();
        reversed = machine.payload == initial;
    } catch (const std::exception& exception) { inverse_error = exception.what(); }
    double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - start).count();
    std::ofstream out(output);
    require(bool(out),"cannot open fresh result");
    out << "{\n  \"status\":\"EXPLORATORY_COMPLETE\",\n"
        << "  \"mode\":\"" << mode << "\",\n"
        << "  \"scope\":\"All physical addresses uniquely tagged; including invalid padding; no asymptotic claim\",\n"
        << "  \"address_bits\":" << N << ",\n"
        << "  \"allocated_records\":" << T << ",\n"
        << "  \"all_addresses_tagged\":true,\n"
        << "  \"target_moduli\":[2,3],\n"
        << "  \"outer_guard_bits\":2,\n  \"inner_guard_bits\":3,\n"
        << "  \"compiled_function_returned\":" << (returned ? "true" : "false") << ",\n"
        << "  \"compiled_error\":\"" << error << "\",\n"
        << "  \"wrong_payload_records\":" << wrong << ",\n"
        << "  \"wrong_valid_destinations\":" << wrong_valid << ",\n"
        << "  \"wrong_invalid_destinations\":" << wrong_invalid << ",\n"
        << "  \"first_wrong_destination\":";
    if (first == UINT64_MAX) out << "null"; else out << first;
    out << ",\n  \"full_literal_reverse_recovers_all_tags\":" << (reversed ? "true" : "false") << ",\n"
        << "  \"inverse_error\":\"" << inverse_error << "\",\n"
        << "  \"events\":" << machine.events.size() << ",\n"
        << "  \"actual_F_u_calls\":" << machine.inner_calls << ",\n"
        << "  \"actual_F_u_rotations\":" << machine.raw_rotations << ",\n"
        << "  \"actual_radix_repairs_forward_and_inverse\":" << machine.radix_repairs << ",\n"
        << "  \"actual_radix_record_sum\":" << machine.radix_records << ",\n"
        << "  \"wall_seconds\":" << seconds << ",\n"
        << "  \"workers\":1,\n  \"native_threads\":1\n}\n";
    std::cout << "{\"mode\":\"" << mode << "\",\"wrong\":" << wrong
              << ",\"seconds\":" << seconds << "}\n";
    return 0;
}
