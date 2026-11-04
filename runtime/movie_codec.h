// Host decoders for the movie formats libvpx does not cover: H.264 video to packed NV12 and AAC audio to interleaved
// 16-bit PCM. Windows: Media Foundation's H.264 and AAC decoder transforms (movie_codec_win.c). Elsewhere every open
// fails (movie_codec_sdl.c), and ov_movie.c answers "unsupported" as before.
#pragma once
#include <stdint.h>

typedef struct MovieCodec MovieCodec;
enum { MC_H264 = 1, MC_AAC = 2 };

// H.264: a = width, b = height, csd0/csd1 the SPS and PPS (Annex B or bare NAL units; may be NULL when the stream
// carries them). AAC: a = sample rate, b = channels, csd0 the AudioSpecificConfig (may be NULL: AAC-LC is assumed).
// NULL on failure, with the reason in err.
MovieCodec *mc_open(int kind, int a, int b, const uint8_t *csd0, int n0, const uint8_t *csd1, int n1, char *err,
                    int errn);
// One compressed access unit with its presentation time (us). 1 taken, 0 the decoder holds output to pull first,
// -1 error (mc_error).
int mc_feed(MovieCodec *c, const uint8_t *p, int n, int64_t us);
// One decoded frame into dst: 1 with *bytes and *us set, 0 none ready (feed more), -1 error. A frame larger than cap is
// an error.
int mc_pull(MovieCodec *c, uint8_t *dst, int cap, int *bytes, int64_t *us);
void mc_drain(MovieCodec *c);   // end of stream: the frames still held come out of mc_pull
void mc_flush(MovieCodec *c);   // drop everything held (a seek); the next input starts a new stream
void mc_close(MovieCodec *c);
const char *mc_error(const MovieCodec *c);
const char *mc_backend(void);   // "Media Foundation", or "none"
