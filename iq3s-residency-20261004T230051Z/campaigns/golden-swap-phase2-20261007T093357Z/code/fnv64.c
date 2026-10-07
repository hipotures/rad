/* Native tape FNV64 helper. Caller supplies the frozen substrate seed. */
#include <stdint.h>
#include <stddef.h>
uint64_t q4_fnv(const void *data, size_t length, uint64_t seed) {
    const unsigned char *bytes = (const unsigned char *)data;
    for (size_t i = 0; i < length; ++i) {
        seed ^= bytes[i];
        seed *= UINT64_C(1099511628211);
    }
    return seed;
}
