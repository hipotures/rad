// Exact finite payload/address controls, not a fixed-tape complexity benchmark.
// Every repaired F_u executes its actual ten rotations/twelve swaps. Repairs
// evaluate reversed programs and stable binary radix-sort the extracted tags.
// Only bits in existing inactive node coordinates are used as dirty banks.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using Word=uint64_t;
using Fn=std::function<Word(Word)>;
using Pred=std::function<bool(Word)>;
static void require(bool ok,const char* msg){if(!ok)throw std::runtime_error(msg);}
static Word mask(unsigned n){require(n<63,"word width exceeds native finite-model cap");return (Word(1)<<n)-1;}
static unsigned bits(Word n){unsigned b=0;while(n){++b;n>>=1;}return b;}
struct Bits {
  std::vector<unsigned> p; Word selected=0;
  Bits()=default;
  explicit Bits(std::vector<unsigned> q):p(std::move(q)){for(auto i:p)selected|=Word(1)<<i;}
  Word get(Word a)const{Word v=0;for(unsigned i=0;i<p.size();++i)v|=((a>>p[i])&1)<<i;return v;}
  Word put(Word v)const{Word a=0;for(unsigned i=0;i<p.size();++i)a|=((v>>i)&1)<<p[i];return a;}
  Word replace(Word a,Word v)const{return (a&~selected)|put(v);}
};
struct Shape{Word s;unsigned width;};
using Shapes=std::vector<Shape>;
static Shape shape(const std::vector<Word>& g){Shape a{1,0};for(auto s:g){a.s*=s;a.width+=bits(s-1);}return a;}
static bool valid(Word a,const Shapes& ss){for(auto s:ss){if((a&mask(s.width))>=s.s)return false;a>>=s.width;}return true;}
static std::vector<Bits> fields(const Shapes& ss){std::vector<Bits> r;unsigned at=0;for(auto s:ss){std::vector<unsigned> p;for(unsigned i=0;i<s.width;++i)p.push_back(at++);r.emplace_back(p);}return r;}
static Word inverse_mod(Word a,Word m){int64_t x=0,y=1,b=m;while(a){int64_t q=b/a,n=b%a;b=a;a=n;n=x-q*y;x=y;y=n;}require(b==1,"noncoprime CRT moduli");x%=int64_t(m);if(x<0)x+=m;return Word(x);}
static Word pack(const std::vector<Word>& values,const std::vector<unsigned>& widths){Word result=0;unsigned at=0;for(unsigned i=0;i<values.size();++i){result|=values[i]<<at;at+=widths[i];}return result;}
static std::vector<Word> unpack(Word value,const std::vector<unsigned>& widths){std::vector<Word> out;for(auto w:widths){out.push_back(value&mask(w));value>>=w;}return out;}
static std::pair<std::vector<Word>,std::vector<Word>> add(
 const std::vector<Word>& yy,const std::vector<Word>& tt,const std::vector<Word>& f,
 const std::vector<unsigned>& widths,unsigned G,bool reverse){
 unsigned total=0;std::vector<unsigned> joined;std::vector<Word> y=yy,t=tt,c,word;
 std::vector<unsigned> guard(y.size(),G);
 for(unsigned i=0;i<y.size();++i){joined.push_back(widths[i]+G);total+=widths[i]+G;c.push_back(y[i]<f[i]);}
 if(reverse)t=unpack((pack(t,guard)+pack(c,guard))&mask(G*y.size()),guard);
 for(unsigned i=0;i<y.size();++i)word.push_back(y[i]|(t[i]<<widths[i]));
 Word amount=pack(f,joined),v=pack(word,joined);
 auto after=unpack((reverse?v-amount:v+amount)&mask(total),joined);c.clear();
 for(unsigned i=0;i<y.size();++i){y[i]=after[i]&mask(widths[i]);t[i]=after[i]>>widths[i];c.push_back(y[i]<f[i]);}
 if(!reverse)t=unpack((pack(t,guard)-pack(c,guard))&mask(G*y.size()),guard);
 return {y,t};
}
struct Event {char kind='m';Fn f,inv;Pred bad;Shapes old,next;};
struct Metric {unsigned nodes,donor,Ybits,UT,scratch,Gout,Gin,K;Word wrong,padding;};
struct Machine {
 unsigned N;std::vector<Word> payload;std::vector<Event> events;std::vector<Metric> metrics;
 Word inner_calls=0,raw_rotations=0,radix_repairs=0,radix_records=0;
 Machine(unsigned n,std::vector<Word> p):N(n),payload(std::move(p)){}
 void map_payload(const Fn& f){std::vector<Word> out(payload.size(),UINT64_MAX);for(Word a=0;a<payload.size();++a){Word z=f(a);if(!(z<out.size()&&out[z]==UINT64_MAX))throw std::runtime_error("nonbijective native map at "+std::to_string(a));out[z]=payload[a];}payload.swap(out);}
 void repair_payload(const Pred& bad,const Fn& key){
   std::vector<std::pair<Word,Word>> rows;std::vector<Word> holes;
   for(Word a=0;a<payload.size();++a)if(bad(a)){Word z=key(a);if(!(z<payload.size()&&bad(z)))throw std::runtime_error("repair escaped bad set at "+std::to_string(a));rows.emplace_back(z,payload[a]);holes.push_back(a);}
   std::vector<std::pair<Word,Word>> tmp(rows.size());
   for(unsigned bit=0;bit<N;++bit){size_t z=0;for(auto row:rows)z+=!((row.first>>bit)&1);size_t lo=0,hi=z;for(auto row:rows)tmp[((row.first>>bit)&1)?hi++:lo++]=row;rows.swap(tmp);}
   for(size_t i=0;i<rows.size();++i){require(rows[i].first==holes[i],"duplicate/missing computed repair key");payload[holes[i]]=rows[i].second;}
   ++radix_repairs;radix_records+=rows.size();
 }
 void embedding_payload(const Shapes& old,const Shapes& next){std::vector<Word> out(payload.size(),0);Word source=0,count=0;for(Word a=0;a<out.size();++a)if(valid(a,next)){while(source<payload.size()&&!valid(source,old)){require(payload[source]==0,"nonzero old padding deleted");++source;}require(source<payload.size(),"source exhausted during joint embedding");out[a]=payload[source++];++count;}while(source<payload.size()){require(!valid(source,old)&&payload[source]==0,"unconsumed source in joint embedding");++source;}payload.swap(out);}
 void permutation(Fn f,Fn inv){map_payload(f);events.push_back(Event{'m',std::move(f),std::move(inv),{}, {}, {}});}
 void repair(Pred bad,Fn key,Fn inverse_key){repair_payload(bad,key);events.push_back(Event{'r',std::move(key),std::move(inverse_key),std::move(bad),{}, {}});}
 void embedding(Shapes old,Shapes next){embedding_payload(old,next);events.push_back(Event{'e',{}, {}, {},std::move(old),std::move(next)});}
 void reverse(){unsigned count=0;for(auto it=events.rbegin();it!=events.rend();++it){if(it->kind=='m')map_payload(it->inv);else if(it->kind=='r')repair_payload(it->bad,it->inv);else embedding_payload(it->next,it->old);if(++count%40==0)std::cout<<"{\"inverse_events_completed\":"<<count<<",\"total\":"<<events.size()<<"}\n"<<std::flush;}}
};
static Fn compose(std::vector<Event> events,bool reverse){return [events=std::move(events),reverse](Word a){if(reverse){for(auto it=events.rbegin();it!=events.rend();++it){require(it->kind!='e',"embedding in local inverse");if(it->kind=='m'||it->bad(a))a=it->inv(a);}}else for(const auto& e:events){require(e.kind!='e',"embedding in local forward");if(e.kind=='m'||e.bad(a))a=e.f(a);}return a;};}
struct Op{char kind;unsigned target,control;int sign;};
static std::vector<Op> ops(){std::vector<Op> f={{'r',2,0,1},{'s',1,3,0},{'r',3,3,1},{'s',1,3,0},{'r',2,1,1},{'s',1,3,0},{'r',3,4,-1},{'s',1,3,0}},r=f;r.insert(r.end(),{{'s',0,3,0},{'r',3,2,1},{'s',0,3,0}});r.insert(r.end(),f.begin(),f.end());r.insert(r.end(),{{'s',0,3,0},{'r',3,2,-1},{'s',0,3,0}});return r;}
static void fanout(Machine& machine,const std::vector<unsigned>& ybits,const std::vector<unsigned>& ubits,
 const std::vector<unsigned>& scratch,const std::vector<unsigned>& owners,unsigned K,unsigned G,bool omit){
 unsigned total=ybits.size(),slots=(total+K-1)/K,H=slots*G;
 require(scratch.size()>=3*H,"insufficient original inner scratch");
 std::vector<unsigned> scratch_used(scratch.begin(),scratch.begin()+3*H),middle=ybits;
 middle.insert(middle.end(),ubits.begin(),ubits.end());
 for(unsigned bit=0;bit<machine.N;++bit)if(std::find(middle.begin(),middle.end(),bit)==middle.end()&&std::find(scratch_used.begin(),scratch_used.end(),bit)==scratch_used.end())middle.push_back(bit);
 require(middle.size()+3*H==machine.N,"inner layout lost/duplicated a bit");
 if(G>1)require(total+K-1<=middle.size(),"missing full high guard for generalized inner digits");
 Bits U(std::vector<unsigned>(scratch_used.begin(),scratch_used.begin()+H)),T(std::vector<unsigned>(scratch_used.begin()+H,scratch_used.begin()+2*H)),Y(middle),B(std::vector<unsigned>(scratch_used.begin()+2*H,scratch_used.end()));
 auto operation=ops();unsigned middle_width=middle.size();
 for(unsigned rho=0;rho<std::min(K,total);++rho){
   std::vector<unsigned> active,targets,sources,physical_targets,physical_sources;
   for(unsigned i=0;i<slots;++i)if(rho+i*K<total){active.push_back(i);targets.push_back(rho+i*K);sources.push_back(total+owners[rho+i*K]);physical_targets.push_back(ybits[rho+i*K]);physical_sources.push_back(ubits[owners[rho+i*K]]);}
   auto raw=[=](Word a,bool reverse){std::vector<Word> q={U.get(a),T.get(a),Y.get(a),B.get(a)};std::vector<unsigned> widths={H,H,middle_width,H};
     auto offset=[&](unsigned kind){int64_t result=0;for(unsigned j=0;j<active.size();++j){unsigned i=active[j],target=targets[j];Word u=(q[0]>>(i*G))&mask(G),t=(q[1]>>(i*G))&mask(G);if(kind<=1)result+=int64_t(u&1)*(kind==0?int64_t(2*t):1-int64_t(2*t))*(int64_t(1)<<target);else if(kind==2)result+=int64_t((q[2]>>sources[j])&1)<<(i*G);else result+=int64_t(((q[2]>>target)&1)^(kind==4?(u&1):0))<<(i*G);}return result;};
     for(unsigned k=0;k<operation.size();++k){const auto& op=operation[reverse?operation.size()-1-k:k];if(op.kind=='s')std::swap(q[op.target],q[op.control]);else{int64_t delta=offset(op.control)*op.sign*(reverse?-1:1);q[op.target]=(q[op.target]+Word(delta))&mask(widths[op.target]);}}
     return U.put(q[0])|T.put(q[1])|Y.put(q[2])|B.put(q[3]);};
   Fn f=[raw](Word a){return raw(a,false);},inv=[raw](Word a){return raw(a,true);};
   Pred bad=[=](Word a){Word u=U.get(a),t=T.get(a),y=Y.get(a);for(unsigned j=0;j<active.size();++j){unsigned i=active[j],target=targets[j];Word ud=(u>>(i*G))&mask(G),td=(t>>(i*G))&mask(G);if(ud==mask(G)||td==mask(G))return true;Word guard=(y>>target)&mask(G==1?5:K);guard>>=1;Word lo=2*(Word(1)<<G),hi=(Word(1)<<(G==1?4:K-1))-lo;if(guard<lo||guard>=hi)return true;}return false;};
   Fn toggle=[=](Word a){Word change=0;for(unsigned j=0;j<physical_targets.size();++j)change|=((a>>physical_sources[j])&1)<<physical_targets[j];return a^change;};
   machine.permutation(f,inv);if(!omit)machine.repair(bad,[=](Word a){return toggle(inv(a));},[=](Word a){return f(toggle(a));});
   ++machine.inner_calls;machine.raw_rotations+=10;
 }
}
struct Node{unsigned left,right;Word sl,sr,mu;};
static bool compiled(Machine& machine,const std::vector<Node>& nodes,const std::vector<Bits>& ff,
 const std::vector<unsigned>& donors,const Shapes& current,unsigned Gout,unsigned Gin,bool omit_inner,bool omit_outer){
 unsigned m=nodes.size();std::vector<unsigned> yy,owners,widths;
 for(unsigned i=0;i<m;++i){const auto& target=ff[nodes[i].right];widths.push_back(target.p.size());for(auto bit:target.p){yy.push_back(bit);owners.push_back(i);}}
 unsigned K=Gin==1||Gin>=3?8:(yy.size()<=5?6:8),H=((yy.size()+K-1)/K)*Gin,need=std::max(2*Gout*m,m+3*H);
 if(donors.size()<need)return false;
 std::vector<unsigned> ubits(donors.begin(),donors.begin()+Gout*m),tbits(donors.begin()+Gout*m,donors.begin()+2*Gout*m),scratch,parity_sources;
 for(unsigned i=0;i<m;++i)parity_sources.push_back(ubits[Gout*i]);
 for(auto bit:donors)if(std::find(parity_sources.begin(),parity_sources.end(),bit)==parity_sources.end()&&scratch.size()<3*H)scratch.push_back(bit);
 require(scratch.size()==3*H,"recycled scratch does not avoid all live parity sources");
 Bits U(ubits),T(tbits);std::vector<unsigned> guards(m,Gout);
 auto values=[=](Word a){std::vector<Word> y;for(auto n:nodes)y.push_back(ff[n.right].get(a));return y;};
 auto put_values=[=](Word a,const std::vector<Word>& y){for(unsigned i=0;i<m;++i)a=ff[nodes[i].right].replace(a,y[i]);return a;};
 auto offsets=[=](Word a){std::vector<Word> f;for(auto n:nodes){Word left=ff[n.left].get(a);f.push_back(left<n.sl?n.mu*left%n.sr:0);}return f;};
 auto bounds=[=](Word a,unsigned phase){auto f=offsets(a);std::vector<std::pair<Word,Word>> bs;for(unsigned i=0;i<m;++i)bs.emplace_back(phase==2?f[i]:0,phase==1?f[i]:nodes[i].sr);return bs;};
 auto before=machine.payload;size_t start=machine.events.size();
 auto conditional=[&](unsigned phase){fanout(machine,yy,parity_sources,scratch,owners,K,Gin,omit_inner);
   auto add_map=[=](Word a,bool reverse){auto bs=bounds(a,phase);std::vector<Word> f;Word control=U.get(a);for(unsigned i=0;i<m;++i)f.push_back(((control>>(Gout*i))&1)?(bs[i].first+bs[i].second)&mask(widths[i]):0);auto result=add(values(a),unpack(T.get(a),guards),f,widths,Gout,reverse);return T.replace(put_values(a,result.first),pack(result.second,guards));};
   machine.permutation([=](Word a){return add_map(a,false);},[=](Word a){return add_map(a,true);});};
 for(unsigned phase=0;phase<3;++phase){conditional(phase);
   auto load=[=](Word a,bool reverse){auto bs=bounds(a,phase);auto y=values(a);std::vector<Word> p;for(unsigned i=0;i<m;++i)p.push_back(bs[i].first<=y[i]&&y[i]<bs[i].second);Word offset=pack(p,guards),value=U.get(a);return U.replace(a,(reverse?value-offset:value+offset)&mask(Gout*m));};
   machine.permutation([=](Word a){return load(a,false);},[=](Word a){return load(a,true);});conditional(phase);machine.permutation([=](Word a){return load(a,true);},[=](Word a){return load(a,false);});
 }
 std::vector<Event> raw(machine.events.begin()+start,machine.events.end());Fn f=compose(raw,false),inv=compose(raw,true);
 auto ideal=[=](Word a,bool reverse){auto f=offsets(a),y=values(a);for(unsigned i=0;i<m;++i)if(y[i]<nodes[i].sr)y[i]=(y[i]+(reverse?nodes[i].sr-f[i]:f[i]))%nodes[i].sr;return put_values(a,y);};
 Pred bad=[=](Word a){for(auto v:unpack(U.get(a),guards))if(v==mask(Gout))return true;for(auto v:unpack(T.get(a),guards))if(v==mask(Gout))return true;return false;};
 std::vector<Word> expected(before.size(),UINT64_MAX);for(Word a=0;a<before.size();++a)expected[ideal(a,false)]=before[a];Word wrong=0,padding=0;
 for(Word a=0;a<expected.size();++a){wrong+=expected[a]!=machine.payload[a];padding+=machine.payload[a]!=0&&!valid(a,current);}
 if(!omit_outer)machine.repair(bad,[=](Word a){return ideal(inv(a),false);},[=](Word a){return f(ideal(a,true));});
 require(machine.payload==expected,"completed compiled node differs from modular rotation");
 machine.metrics.push_back(Metric{m,unsigned(donors.size()),unsigned(yy.size()),2*Gout*m,3*H,Gout,Gin,K,wrong,padding});
 std::cout<<"{\"compiled_nodes\":"<<m<<",\"wrong_before_outer_repair\":"<<wrong<<",\"nonzero_invalid_before_outer_repair\":"<<padding<<",\"events\":"<<machine.events.size()<<"}\n"<<std::flush;
 return true;
}
static void ordinary(Machine& machine,Node n,const std::vector<Bits>& ff){auto f=[=](Word a,bool reverse){Word left=ff[n.left].get(a),y=ff[n.right].get(a),offset=left<n.sl?n.mu*left%n.sr:0;if(y>=n.sr)return a;y=(y+(reverse?n.sr-offset:offset))%n.sr;return ff[n.right].replace(a,y);};machine.permutation([=](Word a){return f(a,false);},[=](Word a){return f(a,true);});}
struct Result{unsigned N,levels;Word S,T;size_t events;std::vector<Metric> metrics;Word inner,rotations,repairs,repair_records;};
static Result run(const std::vector<Word>& primes,unsigned Gout,unsigned Gin,bool bank_leaf,bool omit_inner,bool omit_outer){
 unsigned N=0;Word S=1;for(auto p:primes){N+=bits(p-1);S*=p;}require(N<=24,"finite native memory cap is24 bits");Word T=Word(1)<<N;
 std::vector<Word> initial(T,0);for(Word k=0;k<S;++k)initial[k]=k+1;Machine machine(N,initial);
 std::vector<std::vector<Word>> groups{primes};unsigned level=0;
 while(std::any_of(groups.begin(),groups.end(),[](const auto& g){return g.size()>1;})){
   Shapes old,next;std::vector<std::vector<Word>> ng;std::vector<Node> nodes;
   for(auto g:groups){old.push_back(shape(g));if(g.size()==1)ng.push_back(g);else{unsigned at=bank_leaf&&level==0?g.size()-1:g.size()/2;std::vector<Word> left(g.begin(),g.begin()+at),right(g.begin()+at,g.end());unsigned i=ng.size();ng.push_back(left);ng.push_back(right);Word sl=shape(left).s,sr=shape(right).s;nodes.push_back(Node{i,i+1,sl,sr,inverse_mod(sl,sr)});}}
   for(auto g:ng){next.push_back(shape(g));}
   machine.embedding(old,next);auto ff=fields(next);std::vector<bool> done(next.size(),false);
   std::vector<std::vector<Node>> batches;if(nodes.size()>1)batches.push_back(nodes);for(auto n:nodes)batches.push_back({n});
   for(auto batch:batches){batch.erase(std::remove_if(batch.begin(),batch.end(),[&](auto n){return done[n.left];}),batch.end());if(batch.empty())continue;std::vector<bool> active(next.size(),false);for(auto n:batch)active[n.left]=active[n.right]=true;std::vector<unsigned> donors;for(unsigned i=0;i<ff.size();++i)if(!active[i])donors.insert(donors.end(),ff[i].p.begin(),ff[i].p.end());if(compiled(machine,batch,ff,donors,next,Gout,Gin,omit_inner,omit_outer))for(auto n:batch)done[n.left]=true;}
   for(auto n:nodes)if(!done[n.left])ordinary(machine,n,ff);
   for(Word a=0;a<T;++a){require(machine.payload[a]==0||valid(a,next),"nonzero padding at completed depth");}
   groups=ng;++level;std::cout<<"{\"forward_CRT_level\":"<<level<<",\"records\":"<<T<<",\"compiled_batches\":"<<machine.metrics.size()<<"}\n"<<std::flush;
 }
 std::vector<Word> expected(T,0),mu;Word prefix=1;for(auto s:primes){mu.push_back(inverse_mod(prefix,s));prefix*=s;}
 for(Word k=0;k<S;++k){Word a=0;unsigned at=0;for(unsigned i=0;i<primes.size();++i){a|=(mu[i]*k%primes[i])<<at;at+=bits(primes[i]-1);}expected[a]=k+1;}
 require(machine.payload==expected,"full triangular CRT leaf oracle mismatch");std::cout<<"{\"full_CRT_leaf_oracle\":\"PASS\",\"events\":"<<machine.events.size()<<"}\n"<<std::flush;machine.reverse();require(machine.payload==initial,"full reverse scalar padding mismatch");require(!machine.metrics.empty(),"family never used actual masked F_u");
 return Result{N,level,S,T,machine.events.size(),machine.metrics,machine.inner_calls,machine.raw_rotations,machine.radix_repairs,machine.radix_records};
}
int main(int argc,char** argv){std::string family="five-bank",output;unsigned Gout=1,Gin=1;bool omit_inner=false,omit_outer=false;for(int i=1;i<argc;++i){std::string a=argv[i];if(a=="--family"&&i+1<argc)family=argv[++i];else if(a=="--output"&&i+1<argc)output=argv[++i];else if(a=="--outer-guard"&&i+1<argc)Gout=std::stoul(argv[++i]);else if(a=="--inner-guard"&&i+1<argc)Gin=std::stoul(argv[++i]);else if(a=="--omit-inner-repair")omit_inner=true;else if(a=="--omit-outer-repair")omit_outer=true;else{std::cerr<<"unknown argument "<<a<<"\n";return 2;}}
 std::vector<Word> primes;bool bank_leaf=true;if(family=="four-balanced"){primes={3,5,7,11};bank_leaf=false;}else if(family=="five-bank")primes={3,5,7,11,17};else if(family=="guard2-bank")primes={3,5,7,11,131};else if(family=="guard3-bank")primes={3,5,7,11,2053};else if(family=="inner2outer2-bank")primes={3,5,7,11,521};else if(family=="inner2-three")primes={3,5,257};else if(family=="six-balanced"){primes={3,5,7,11,13,17};bank_leaf=false;}else{std::cerr<<"unknown family\n";return 2;}
 require(Gout>=1&&Gout<=3&&Gin>=1&&Gin<=2,"unsupported finite dirty digit width");auto started=std::chrono::steady_clock::now();std::string status="PASS",error;Result r{};r.S=1;for(auto prime:primes){r.N+=bits(prime-1);r.S*=prime;}r.T=Word(1)<<r.N;try{r=run(primes,Gout,Gin,bank_leaf,omit_inner,omit_outer);if(omit_inner||omit_outer){status="NEGATIVE_CONTROL_UNEXPECTED_PASS";error="omitted mandatory repair unexpectedly passed";}}catch(const std::exception& e){status=(omit_inner||omit_outer)?"EXPECTED_NEGATIVE":"FAIL";error=e.what();}
 double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();std::ofstream out(output);require(bool(out),"cannot open native certificate output");out<<"{\n  \"status\":\""<<status<<"\",\n  \"family\":\""<<family<<"\",\n  \"outer_guard_bits\":"<<Gout<<",\n  \"inner_guard_bits\":"<<Gin<<",\n  \"omitted_inner_repair\":"<<(omit_inner?"true":"false")<<",\n  \"omitted_outer_repair\":"<<(omit_outer?"true":"false")<<",\n  \"error\":\""<<error<<"\",\n  \"address_bits\":"<<r.N<<",\n  \"allocated_records\":"<<r.T<<",\n  \"valid_records\":"<<r.S<<",\n  \"added_address_bits\":0,\n  \"forward_levels\":"<<r.levels<<",\n  \"events\":"<<r.events<<",\n  \"actual_F_u_calls\":"<<r.inner<<",\n  \"actual_F_u_rotations\":"<<r.rotations<<",\n  \"actual_radix_repairs_forward_and_inverse\":"<<r.repairs<<",\n  \"actual_radix_record_sum\":"<<r.repair_records<<",\n  \"full_leaf_oracle\":"<<(status=="PASS"?"true":"false")<<",\n  \"full_reverse_pipeline\":"<<(status=="PASS"?"true":"false")<<",\n  \"wall_seconds\":"<<seconds<<",\n  \"workers\":1,\n  \"native_threads\":1,\n  \"compiled_batches\":[";
 for(size_t i=0;i<r.metrics.size();++i){auto m=r.metrics[i];if(i)out<<",";out<<"{\"active_nodes\":"<<m.nodes<<",\"donor_available_bits\":"<<m.donor<<",\"target_bit_sum\":"<<m.Ybits<<",\"borrowed_U_T_bits\":"<<m.UT<<",\"borrowed_inner_bits\":"<<m.scratch<<",\"inner_spacing\":"<<m.K<<",\"wrong_before_outer_repair\":"<<m.wrong<<",\"nonzero_invalid_before_outer_repair\":"<<m.padding<<"}";}out<<"]\n}\n";out.close();std::cout<<"{\"status\":\""<<status<<"\",\"wall_seconds\":"<<seconds<<"}\n";return status=="PASS"||status=="EXPECTED_NEGATIVE"?0:1;
}
