// movie_codec.h off Windows: no H.264 or AAC decoder yet, so every open fails and the movie stays "unsupported".
#include <stdio.h>

#include "movie_codec.h"

MovieCodec *mc_open(int kind, int a, int b, const uint8_t *csd0, int n0, const uint8_t *csd1, int n1, char *err,
                    int errn) {
    (void)kind, (void)a, (void)b, (void)csd0, (void)n0, (void)csd1, (void)n1;
    snprintf(err, (size_t)errn, "no host H.264/AAC decoder on this OS");
    return NULL;
}
int mc_feed(MovieCodec *c, const uint8_t *p, int n, int64_t us) { (void)c, (void)p, (void)n, (void)us; return -1; }
int mc_pull(MovieCodec *c, uint8_t *dst, int cap, int *bytes, int64_t *us) {
    (void)c, (void)dst, (void)cap, (void)bytes, (void)us;
    return -1;
}
void mc_drain(MovieCodec *c) { (void)c; }
void mc_flush(MovieCodec *c) { (void)c; }
void mc_close(MovieCodec *c) { (void)c; }
const char *mc_error(const MovieCodec *c) { (void)c; return "no host decoder"; }
const char *mc_backend(void) { return "none"; }
