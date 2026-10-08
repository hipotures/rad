// Exact finite ordered profile certificate for changed negative-basis pairs.
// Matrices are integers after multiplying the actual scaled corner by 66.
// A complete successful replay at one prime proves selected prefix minors
// nonzero. Zero minors are proved using a product of successful distinct
// primes larger than the independently retained Hadamard bound.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <boost/multiprecision/cpp_int.hpp>
using boost::multiprecision::cpp_int;
using Triple=std::array<uint8_t,3>;
constexpr int a=23,b=25,d=47;
int64_t mul(int64_t x,int64_t y,int64_t p){return x*y%p;}
int64_t power(int64_t x,int64_t n,int64_t p){int64_t out=1;for(;n;n>>=1,x=mul(x,x,p))if(n&1)out=mul(out,x,p);return out;}
bool prime(int64_t p){if(p<2)return false;if(!(p&1))return p==2;for(int64_t i=3;i*i<=p;i+=2)if(p%i==0)return false;return true;}
std::array<int,d> rows,cols,pivots;
// -1 means an unlucky selected pivot; 0 contradicts a proposed zero; 1 passes.
int replay(const Triple&T,const Triple&S,int64_t p,int&failed_row,int&failed_col,int64_t&zero_checks){
 int64_t x[a],y[b],M[d][d];bool available[d];
 for(int i=0;i<a;i++)x[i]=(i==T[0]||i==T[1]||i==T[2])?78:-858;
 for(int i=0;i<b;i++)y[i]=(i==S[0]||i==S[1]||i==S[2])?77:-924;
 for(int i=0;i<d;i++){available[i]=true;for(int j=0;j<d;j++){
  int64_t z=-66;if(rows[i]==cols[j])z+=x[rows[i]];if(i%b==(528+j)%b)z+=y[i%b];assert(std::abs(z)<=1848);M[i][j]=(z%p+p)%p;
 }}
 zero_checks=0;
 for(int i=0;i<d;i++){
  int c=pivots[i];int64_t value=M[i][c];assert(available[c]);
  if(!value){failed_row=i;failed_col=c;return -1;}
  for(int j=c+1;j<d;j++)if(available[j]){if(M[i][j]){failed_row=i;failed_col=j;return 0;}zero_checks++;}
  available[c]=false;int64_t inverse=power(value,p-2,p);
  for(int r=i+1;r<d;r++)if(M[r][c]){
   int64_t ratio=mul(M[r][c],inverse,p);
   for(int j=0;j<d;j++)if(available[j]&&M[i][j]){int64_t z=M[r][j]-mul(ratio,M[i][j],p);M[r][j]=z<0?z+p:z;}
   M[r][c]=0;
  }
 }
 return 1;
}
int main(int argc,char**argv){
 assert(argc==4);int part=std::stoi(argv[2]),parts=std::stoi(argv[3]);assert(parts>0&&part>=0&&part<parts);
 std::ifstream input(argv[1],std::ios::binary);uint32_t count;input.read(reinterpret_cast<char*>(&count),4);assert(count==192596);
 for(int i=0;i<a;i++)rows[i]=cols[i]=i;rows[a]=a-1;cols[a]=0;for(int i=0;i<a;i++)rows[a+1+i]=cols[a+1+i]=i;
 pivots[0]=46;for(int i=1;i<=21;i++)pivots[i]=i+24;for(int i=22;i<=26;i++)pivots[i]=46-i;
 for(int i=27;i<=45;i++)pivots[i]=i-26;pivots[46]=0;
 std::vector<int64_t> primes;for(int64_t p=2147483647;primes.size()<25;p-=2)if(prime(p))primes.push_back(p);
 cpp_int bound=1;for(int i=0;i<24;i++)bound*=47;for(int i=0;i<47;i++)bound*=1848;
 uint32_t checked=0;int64_t successful_replays=0,unlucky_replays=0,total_zeros=0;size_t maximum_primes_needed=0;
 std::vector<std::array<int64_t,5>> unlucky;
 for(uint32_t k=0;k<count;k++){
  uint32_t index;Triple T,S;input.read(reinterpret_cast<char*>(&index),4);input.read(reinterpret_cast<char*>(T.data()),3);input.read(reinterpret_cast<char*>(S.data()),3);assert(input);
  if(k%parts!=uint32_t(part))continue;
  cpp_int product=1;size_t attempts=0;
  for(int64_t p:primes){
   attempts++;int row=-1,col=-1;int64_t zeros=0;int status=replay(T,S,p,row,col,zeros);
   if(status==0){std::cerr<<"EXACT PROFILE CONTRADICTION index="<<index<<" row="<<row<<" col="<<col<<" prime="<<p<<"\n";return 2;}
   if(status<0){unlucky_replays++;unlucky.push_back({index,row,col,p,k});continue;}
   product*=p;successful_replays++;total_zeros+=zeros;
   if(product>bound)break;
  }
  if(product<=bound){std::cerr<<"INSUFFICIENT ZERO MODULUS index="<<index<<"\n";return 3;}
  maximum_primes_needed=std::max(maximum_primes_needed,attempts);checked++;
  if(checked%10000==0)std::cerr<<"Exact exceptional profiles "<<checked<<" part "<<part<<"\n";
 }
 char extra;assert(!input.read(&extra,1));assert(checked==(count+parts-1-part)/parts);
 std::cout<<"{\"status\":\"EXACT COMPLETE EXCEPTION PART PROFILE\",\"part\":"<<part<<",\"parts\":"<<parts<<",\"input_pairs\":"<<count<<",\"checked_pairs\":"<<checked<<",\"null_profile\":[1,21,1,1,1,1,1,19,1],\"integer_matrix_scale\":66,\"entry_absolute_bound\":1848,\"minor_absolute_bound\":\""<<bound<<"\",\"successful_replays\":"<<successful_replays<<",\"zero_minor_modular_checks\":"<<total_zeros<<",\"unlucky_replays\":"<<unlucky_replays<<",\"maximum_primes_attempted\":"<<maximum_primes_needed<<",\"primality_trial_division\":true,\"primes\":[";
 for(size_t i=0;i<primes.size();i++){if(i)std::cout<<",";std::cout<<primes[i];}std::cout<<"],\"unlucky\":[";
 for(size_t i=0;i<unlucky.size();i++){if(i)std::cout<<",";auto x=unlucky[i];std::cout<<"["<<x[0]<<","<<x[1]<<","<<x[2]<<","<<x[3]<<","<<x[4]<<"]";}std::cout<<"]}\n";
}
