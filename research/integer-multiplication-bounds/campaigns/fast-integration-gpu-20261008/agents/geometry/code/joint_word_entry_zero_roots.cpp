// Exact rational entry-zero loci of actual executed-word transitions.
// Reuses our rational projector builder at beta=0; beta=0 is only an
// internal algebraic reference, not an admissible source basis.
// Entry loci are discovery: a zero entry does not certify a better NE flag.
#define main parameter_profile_program
#include "parameter_joint_word_profiles.cpp"
#undef main
#include <set>
#include <tuple>

using Triple=std::array<I,3>;
struct Pattern {V weighted_entries=0,distinct_entries=0;std::map<std::string,V>strata;U a=0,b=0,i=0,j=0;};
cpp_int square_root(cpp_int n){assert(n>=0);if(n==0)return 0;cpp_int x=cpp_int(1)<<((bits(n)+1)/2);while(true){cpp_int y=(x+n/x)/2;if(y>=x)return x;x=y;}}
std::pair<cpp_int,cpp_int> rational(cpp_int n,cpp_int d){assert(d!=0);if(d<0){d=-d;n=-n;}cpp_int g=gcd(n,d);return {n/g,d/g};}
bool admissible(U h,const cpp_int&n,const cpp_int&d){return d-h*n!=0&&n!=0&&d-3*n!=0&&9*n-d!=0&&2*d-3*(h-3)*n!=0&&(h-7)*d-3*(h-3)*n!=0&&2*d-3*(h-1)*n!=0;}
std::vector<std::pair<cpp_int,cpp_int>> roots(const Triple&c){
 std::vector<std::pair<cpp_int,cpp_int>>out;cpp_int a=c[2],b=c[1],z=c[0];
 if(a==0){if(b!=0)out.push_back(rational(-z,b));return out;}
 cpp_int delta=b*b-4*a*z;if(delta<0)return out;cpp_int s=square_root(delta);if(s*s!=delta)return out;
 out.push_back(rational(-b+s,2*a));if(s!=0)out.push_back(rational(-b-s,2*a));return out;
}
int main(int argc,char**argv){
 assert(argc==3);auto start=std::chrono::steady_clock::now();std::ifstream in(argv[1],std::ios::binary);U header[6];read_array(in,header);U h=header[0],nf=header[3],nt=header[4];V mass,loss;in.read(reinterpret_cast<char*>(&mass),8);in.read(reinterpret_cast<char*>(&loss),8);assert(h==23||h==25);
 std::vector<Frame>frames(nf);std::vector<V>cover(nf);for(U id=0;id<nf;id++){auto&f=frames[id];in.read(reinterpret_cast<char*>(&f.forced),8);in.read(reinterpret_cast<char*>(&cover[id]),8);in.read(reinterpret_cast<char*>(&f.rank),4);f.symbols.assign(h,0);U next=2;for(U i=0;i<h;i++)if(f.forced>>i&1)f.symbols[i]=1;else if(cover[id]>>i&1)f.symbols[i]=next++;make_matrix(f,h,0,1,id<2?id:2);}
 std::map<Triple,Pattern>patterns;V matrices=0,entry_count=0;I largest=0;
 for(U at=0;at<nt;at++){
  U a,b;I count;in.read(reinterpret_cast<char*>(&a),4);in.read(reinterpret_cast<char*>(&b),4);in.read(reinterpret_cast<char*>(&count),8);assert(a<nf&&b<nf&&count>0);assert(frames[b].rank>frames[a].rank);U rank=frames[b].rank-frames[a].rank;if(rank<2)continue;
  auto&A=frames[a];auto&B=frames[b];cpp_int den=A.den/gcd(A.den,B.den)*B.den;std::vector<I>M(h*h),row(h),col(h);I total=0;cpp_int limit=cpp_int(1)<<40;
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){cpp_int z=B.numerator[i*h+j]*(den/B.den)-A.numerator[i*h+j]*(den/A.den);assert(z>-limit&&z<limit);I v=z.convert_to<I>();M[i*h+j]=v;row[i]+=v;col[j]+=v;total+=v;}
  std::string stratum=std::to_string(a<2?0:popcount64(A.forced))+"->"+std::to_string(b<2?0:popcount64(B.forced))+":r"+std::to_string(rank)+(A.forced==B.forced?":same-core":":changed-core");
  for(U i=0;i<h;i++)for(U j=0;j<h;j++){
   I v=M[i*h+j];Triple p={v,row[i]-col[j]-I(h)*v,I(h)*col[j]-total};I g=std::gcd(std::gcd(p[0],p[1]),p[2]);if(!g)continue;for(I&x:p)x/=g;for(int k=2;k>=0;k--)if(p[k]){if(p[k]<0)for(I&x:p)x=-x;break;}
   for(I x:p)largest=std::max(largest,I(std::abs(x)));auto&rec=patterns[p];rec.weighted_entries+=count;rec.distinct_entries++;rec.strata[stratum]+=count;if(rec.distinct_entries==1){rec.a=a;rec.b=b;rec.i=i;rec.j=j;}entry_count++;
  }matrices++;
 }
 assert(in);std::ofstream out(argv[2]);assert(out);out<<"{\"status\":\"EXACT RATIONAL ENTRY-ZERO LOCI DISCOVERY\",\"h\":"<<h<<",\"R\":"<<header[2]<<",\"rank_mass\":"<<mass<<",\"matrices\":"<<matrices<<",\"nonzero_entry_polynomials\":"<<entry_count<<",\"unique_polynomials\":"<<patterns.size()<<",\"largest_normalized_coefficient\":"<<largest<<",\"patterns\":[";bool first=true;
 for(auto&[p,r]:patterns){auto rr=roots(p);if(rr.empty())continue;if(!first)out<<",";first=false;out<<"{\"coefficients\":["<<p[0]<<","<<p[1]<<","<<p[2]<<"],\"weighted_entries\":"<<r.weighted_entries<<",\"distinct_entries\":"<<r.distinct_entries<<",\"example\":["<<r.a<<","<<r.b<<","<<r.i<<","<<r.j<<"],\"strata\":{";bool fs=true;for(auto&[s,n]:r.strata){if(!fs)out<<",";fs=false;out<<"\""<<s<<"\":"<<n;}out<<"},\"rational_roots\":[";bool fr=true;for(auto&[n,d]:rr){if(!fr)out<<",";fr=false;out<<"{\"numerator\":\""<<n<<"\",\"denominator\":\""<<d<<"\",\"admissible\":"<<(admissible(h,n,d)?"true":"false")<<"}";}out<<"]}";}
 out<<"],\"seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<",\"scope\":\"All individual matrix entry zeros only. Rational higher-minor zero loci and recursive-width benefits require separate exact checks. Native projector reference beta0 is not a source-admissible construction.\"}\n";
 std::cout<<"h="<<h<<" matrices="<<matrices<<" unique_polynomials="<<patterns.size()<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"\n";
}
