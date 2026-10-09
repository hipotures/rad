// Exact nonnegative finite-label min-sum variable elimination.
// Authored source only; build/run outputs belong in ignored work directories.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

struct Factor {
    std::vector<int> variables;
    std::vector<std::uint16_t> costs;
};
struct Decision {
    int variable;
    std::vector<int> neighbors;
    std::vector<std::uint16_t> choices;
};
struct Edge { int a, b, weight; };

std::size_t power(std::size_t base, int exponent) {
    std::size_t result = 1;
    while (exponent--) {
        if (result > std::numeric_limits<std::size_t>::max()/base)
            throw std::runtime_error("Finite factor index overflow");
        result *= base;
    }
    return result;
}

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("Expected one exact graph input path");
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("Cannot read graph input");
        int count, domain, constant;
        std::size_t maximum_entries;
        input >> count >> domain >> constant >> maximum_entries;
        if (count < 1 || domain < 1 || domain >= 65535)
            throw std::runtime_error("Invalid vertex/domain count");
        std::vector<std::uint16_t> distances(domain*domain);
        for (auto& x: distances) { int z; input >> z; x=z; }
        std::vector<std::vector<std::uint16_t>> unary(count,
            std::vector<std::uint16_t>(domain));
        std::vector<Factor> factors;
        for (int i=0; i<count; ++i) {
            for (auto& x: unary[i]) { int z; input >> z; x=z; }
            factors.push_back(Factor{{i}, unary[i]});
        }
        int edge_count;
        input >> edge_count;
        std::vector<Edge> edges(edge_count);
        for (auto& e: edges) {
            input >> e.a >> e.b >> e.weight;
            if (e.a>=e.b || e.a<0 || e.b>=count || e.weight<1)
                throw std::runtime_error("Invalid exact graph edge");
            Factor f;
            f.variables={e.a,e.b};
            f.costs.resize(domain*domain);
            for (int b=0; b<domain; ++b)
                for (int a=0; a<domain; ++a) {
                    int z=e.weight*distances[a*domain+b];
                    if (z>=65535) throw std::runtime_error("Initial factor charge overflow");
                    f.costs[a+domain*b]=z;
                }
            factors.push_back(std::move(f));
        }
        std::vector<int> order(count);
        for (auto& x: order) input >> x;
        if (!input) throw std::runtime_error("Truncated exact graph input");
        auto sorted=order;
        std::sort(sorted.begin(), sorted.end());
        for (int i=0; i<count; ++i)
            if (sorted[i]!=i) throw std::runtime_error("Elimination order is not a permutation");
        std::vector<Decision> decisions;
        std::size_t evaluations=0,peak_live_entries=0;
        int maximum_width=0;
        for (int variable: order) {
            std::vector<Factor> selected, remaining;
            std::set<int> neighbor_set;
            for (auto& f: factors) {
                if (std::find(f.variables.begin(),f.variables.end(),variable)!=f.variables.end()) {
                    for (int v: f.variables) if (v!=variable) neighbor_set.insert(v);
                    selected.push_back(std::move(f));
                } else remaining.push_back(std::move(f));
            }
            std::vector<int> neighbors(neighbor_set.begin(),neighbor_set.end());
            maximum_width=std::max(maximum_width,int(neighbors.size()));
            auto entries=power(domain,neighbors.size());
            if (entries>maximum_entries)
                throw std::runtime_error("Predeclared finite factor memory bound exceeded");
            Factor result{neighbors,std::vector<std::uint16_t>(entries)};
            Decision decision{variable,neighbors,std::vector<std::uint16_t>(entries)};
            // For one fixed neighboring assignment, each selected factor
            // index is offset + candidate_label * variable_stride.
            std::vector<std::vector<std::pair<int,std::size_t>>> coordinates;
            std::vector<std::size_t> variable_strides;
            for (const auto& f: selected) {
                std::size_t stride=1,variable_stride=0;
                std::vector<std::pair<int,std::size_t>> terms;
                for (int v: f.variables) {
                    if (v==variable) variable_stride=stride;
                    else {
                        auto it=std::find(neighbors.begin(),neighbors.end(),v);
                        if (it==neighbors.end()) throw std::runtime_error("Factor scope mismatch");
                        terms.emplace_back(it-neighbors.begin(),stride);
                    }
                    stride*=domain;
                }
                if (!variable_stride) throw std::runtime_error("Eliminated variable missing from factor");
                coordinates.push_back(std::move(terms));variable_strides.push_back(variable_stride);
            }
            std::vector<int> labels(neighbors.size());
            std::vector<std::size_t> offsets(selected.size());
            for (std::size_t index=0; index<entries; ++index) {
                auto left=index;
                for (auto& label: labels) { label=left%domain; left/=domain; }
                for (std::size_t j=0; j<selected.size(); ++j) {
                    offsets[j]=0;
                    for (auto [position,stride]: coordinates[j]) offsets[j]+=labels[position]*stride;
                }
                unsigned best=std::numeric_limits<unsigned>::max();
                int argmin=-1;
                for (int label=0; label<domain; ++label) {
                    unsigned cost=0;
                    for (std::size_t j=0; j<selected.size(); ++j)
                        cost+=selected[j].costs[offsets[j]+label*variable_strides[j]];
                    if (cost<best) { best=cost; argmin=label; }
                }
                if (best>=65535 || argmin<0) throw std::runtime_error("Min-sum factor charge overflow");
                result.costs[index]=best;decision.choices[index]=argmin;
                evaluations+=domain;
            }
            std::size_t live=entries*2;
            for (const auto& f: selected) live+=f.costs.size();
            for (const auto& f: remaining) live+=f.costs.size();
            for (const auto& d: decisions) live+=d.choices.size();
            peak_live_entries=std::max(peak_live_entries,live);
            remaining.push_back(std::move(result));factors=std::move(remaining);
            decisions.push_back(std::move(decision));
        }
        unsigned optimum=constant;
        for (const auto& f: factors) {
            if (!f.variables.empty() || f.costs.size()!=1)
                throw std::runtime_error("Incomplete variable elimination");
            optimum+=f.costs[0];
        }
        std::vector<int> assignment(count,-1);
        for (auto it=decisions.rbegin(); it!=decisions.rend(); ++it) {
            std::size_t index=0,stride=1;
            for (int v: it->neighbors) {
                if (assignment[v]<0) throw std::runtime_error("Decision reconstruction order mismatch");
                index+=stride*assignment[v];stride*=domain;
            }
            assignment[it->variable]=it->choices[index];
        }
        unsigned replay=constant;
        for (int i=0; i<count; ++i) replay+=unary[i][assignment[i]];
        for (auto e: edges) replay+=e.weight*distances[assignment[e.a]*domain+assignment[e.b]];
        if (replay!=optimum) throw std::runtime_error("Reconstructed assignment does not achieve exact optimum");
        std::cout << "{\"status\":\"EXACT FINITE MIN-SUM PASS\",\"optimum\":" << optimum
                  << ",\"maximum_width\":" << maximum_width
                  << ",\"candidate_cost_evaluations\":" << evaluations
                  << ",\"peak_live_uint16_entries\":" << peak_live_entries
                  << ",\"assignment\":[";
        for (int i=0; i<count; ++i) { if(i)std::cout << ',';std::cout << assignment[i]; }
        std::cout << "]}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';return 1;
    }
}
