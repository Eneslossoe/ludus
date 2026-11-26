"""Sessiz video + soundtrack -> final MP4 (-14 LUFS, AAC 192k).

GitHub 100 MB sinirini asarsa ayrica sikistirilmis bir kopya uretir.
"""
import os
import subprocess

WORK = os.environ.get("ZK_WORK", "/home/user/work")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.path.join(ROOT, "output")
NAME = "gladyator_okulu_olsaydin"


def run(cmd):
    print(" ".join(cmd[:6]), "...", flush=True)
    subprocess.run(cmd, check=True)


def main():
    os.makedirs(OUTD, exist_ok=True)
    vid = os.path.join(WORK, "render", "video_noaudio.mp4")
    wav = os.path.join(WORK, "soundtrack.wav")
    full = os.path.join(WORK, NAME + ".mp4")
    # olcum -> kazanc -> limiter (tepe -1.5 dBFS, hedef -14 LUFS)
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    lufs = float([l for l in meas.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    gain = -14.0 - lufs + 0.6
    print(f"soundtrack {lufs:.1f} LUFS -> kazanc {gain:+.1f} dB")
    af = f"volume={gain:.2f}dB,alimiter=limit=0.68:attack=2:release=80:level=disabled"
    run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", full])
    size = os.path.getsize(full) / 1e6
    print(f"tam kalite: {full} ({size:.1f} MB)")
    gh = os.path.join(OUTD, NAME + "_github.mp4")
    if size > 95:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                    "default=nw=1:nk=1", full], capture_output=True, text=True).stdout)
        vbit = int((90e6 * 8 / dur - 160e3) / 1000)
        run(["ffmpeg", "-y", "-v", "error", "-i", full, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vbit}k",
             "-maxrate", f"{int(vbit * 1.5)}k", "-bufsize", f"{vbit * 2}k", "-pix_fmt", "yuv420p", "-c:a", "copy",
             "-movflags", "+faststart", gh])
    else:
        run(["cp", full, gh])
    print(f"github kopyasi: {gh} ({os.path.getsize(gh) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
