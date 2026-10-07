#pragma once
#include <cstdint>
namespace strata::research {
constexpr int TapeLayers=48,TapeK=10,TapeT=4,TapeDrafts=3;
struct TapeRoutes { int32_t ids[48][40]; float weights[48][40]; int32_t mtp_ids[3][10]; float mtp_weights[3][10]; int32_t drafts[3]; float probs[3]; };
struct TapePage { int32_t mode; int32_t seen[51]; int32_t disagreements[51]; int32_t nonfinite; TapeRoutes routes; float activation[51][8]; };
void tape_route(TapePage* page,int layer,int row_offset,int n,int32_t* ids,float* weights,const float* activation,void* stream);
void tape_mtp_head(TapePage* page,int step,int32_t* out,float* prob,void* stream);
}
