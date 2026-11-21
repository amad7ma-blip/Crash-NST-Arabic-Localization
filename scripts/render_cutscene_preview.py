"""Render a verified 1920x1080 preview MP4 for any localized cutscene directly from installed update.pak."""
import argparse
import array
import importlib.util
import math
import os
import shutil
import struct
import subprocess
import sys
import wave

from PIL import Image, ImageDraw, ImageFont

WS = r'C:\Users\Admin\.gemini\antigravity\scratch\crash-nst-arabic'
GAME_ARCH = r'C:\Program Files (x86)\Steam\steamapps\common\Crash Bandicoot - N Sane Trilogy\archives'
EXTRACTED_AUDIO = os.path.join(WS, 'workspace', 'extracted', 'cutscene_audio')
REPORTS_DIR = os.path.join(WS, 'reports')
LOGS_DIR = os.path.join(WS, 'workspace', 'logs')

FFMPEG = (
    r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages'
    r'\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe'
    r'\ffmpeg-9.0.2-essentials_build\bin\ffmpeg.exe'
)

sys.path.insert(0, os.path.join(WS, 'workspace', 'scripts'))
from nst_alchemy import IgaArchiveV11, IgzDoc
from arabic_shaper import shape_arabic_text
from cutscene_subtitles_data import ALL_CUTSCENE_GROUPS

_spec = importlib.util.spec_from_file_location(
    'build27', os.path.join(WS, 'workspace', 'scripts', '27_build_full_arabic_update.py')
)
_b27 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b27)

SFX_STREAM_MAP = {
    'Crash1_Intro_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_C1_Intro,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_C1_Intro_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
    'Crash2_Intro_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_CB2_Intro,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_CB2_Intro_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
    'Crash2_Outro_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_CB2_Outro,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_CB2_Outro_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
    'Crash2_Outro100_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_CB2_Outro_100,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_CB2_Outro_100_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
    'Crash3_Intro_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_CB3_Intro,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_CB3_Intro_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
    'Crash3_BossOutro_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_CB3_Outro,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_CB3_Outro_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
    'Crash3_Outro100_Cinematic': (
        'sound_streams/wavs/Cutscene/CS_CB3_Outro_100,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
        'sound_streams/wavs/Cutscene/CS_CB3_Outro_100_LR,Streaming_Cutscenes_bank,NoLoc,48000,40,0,1.snd',
    ),
}


def extract_fsb5_mp3(snd_bytes: bytes, dst_mp3: str) -> str:
    """Extract raw MP3 payload from an Alchemy .snd wrapping an FSB5 (mode=11) stream."""
    off = snd_bytes.find(b'FSB5')
    assert off >= 0, 'FSB5 header not found'
    _magic, ver, _n_samples, shdr_sz, name_sz, data_sz, mode = struct.unpack_from('<4sIIIIII', snd_bytes, off)
    assert ver == 1 and mode == 11, f'Unexpected FSB5 ver={ver} mode={mode}'
    payload_start = off + 60 + shdr_sz + name_sz
    payload = snd_bytes[payload_start:payload_start + data_sz]
    for i in range(min(128, len(payload) - 1)):
        if payload[i] == 0xFF and (payload[i + 1] & 0xE0) == 0xE0:
            payload = payload[i:]
            break
    with open(dst_mp3, 'wb') as f:
        f.write(payload)
    return dst_mp3


def render_transparent_line(text: str, glyphs: dict, atlas: Image.Image) -> Image.Image:
    """Blit one shaped LTR-ordered Arabic line directly onto a transparent RGBA canvas."""
    line_h = int(round(max((g['h'] for g in glyphs.values()), default=48))) + 16
    total_w = 16.0
    for ch in text:
        if ch == ' ':
            total_w += 14.0
        elif ord(ch) in glyphs:
            g = glyphs[ord(ch)]
            total_w += max(1.0, g['kl'] + g['w'] + g['kr'])
        else:
            total_w += 18.0
    canvas = Image.new('RGBA', (max(int(math.ceil(total_w)) + 8, 24), line_h), (0, 0, 0, 0))
    x = 8.0
    base_y = 6
    for ch in text:
        if ch == ' ':
            x += 14.0
            continue
        g = glyphs.get(ord(ch))
        if g is None:
            x += 18.0
            continue
        x += g['kl']
        gw = g['x1'] - g['x0']
        gh = g['y1'] - g['y0']
        if gw > 0 and gh > 0:
            crop = atlas.crop((g['x0'], g['y0'], g['x1'], g['y1']))
            canvas.alpha_composite(crop, (max(0, int(round(x))), base_y))
        x += g['w'] + g['kr']
    return canvas


def render_shaped_multiline_scaled(
    shaped_text: str,
    glyphs: dict,
    atlas: Image.Image,
    scale: float,
) -> Image.Image:
    """Render an already-shaped multiline string onto a scaled transparent RGBA surface."""
    line_imgs = [render_transparent_line(ln, glyphs, atlas) for ln in shaped_text.split('\n')]
    w = max(im.width for im in line_imgs)
    line_step = int(round(line_imgs[0].height * 0.88))
    h = line_step * (len(line_imgs) - 1) + line_imgs[-1].height
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    cy = 0
    for im in line_imgs:
        out.alpha_composite(im, ((w - im.width) // 2, cy))
        cy += line_step
    sw = max(1, int(round(out.width * scale)))
    sh = max(1, int(round(out.height * scale)))
    return out.resize((sw, sh), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', default='Crash3_BossOutro_Cinematic')
    parser.add_argument('--copy-desktop', action='store_true')
    args = parser.parse_args()

    grp = next((g for g in ALL_CUTSCENE_GROUPS if g['name'] == args.scene), None)
    assert grp is not None, f'Unknown scene: {args.scene}'

    os.makedirs(EXTRACTED_AUDIO, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Calculate full scene duration from shot definitions
    total_dur = max(s['shot_start_global'] + s['shot_dur'] for s in grp['specs'])

    # Extract English VO + optional surround SFX streams from scene archive
    vo_mp3 = os.path.join(EXTRACTED_AUDIO, f"{args.scene}_gen_en.mp3")
    with IgaArchiveV11(os.path.join(GAME_ARCH, grp['archive'])) as ap:
        if not os.path.exists(vo_mp3):
            vo_cand = [e.logical_name for e in ap.entries if '_gen_en,' in e.logical_name and e.logical_name.endswith('.snd')]
            assert vo_cand, f'No English VO stream found in {grp["archive"]}'
            extract_fsb5_mp3(ap.read(vo_cand[0]), vo_mp3)

        sfx_inputs = []
        if args.scene in SFX_STREAM_MAP:
            c_path, lr_path = SFX_STREAM_MAP[args.scene]
            sfx_c = extract_fsb5_mp3(ap.read(c_path), os.path.join(EXTRACTED_AUDIO, f'{args.scene}_sfx_center.mp3'))
            sfx_lr = extract_fsb5_mp3(ap.read(lr_path), os.path.join(EXTRACTED_AUDIO, f'{args.scene}_sfx_lr.mp3'))
            sfx_inputs = [sfx_c, sfx_lr]

    mixed_wav = os.path.join(EXTRACTED_AUDIO, f'{args.scene}_mixed_preview.wav')
    if sfx_inputs:
        cmd = [
            FFMPEG, '-y',
            '-i', vo_mp3,
            '-i', sfx_inputs[0],
            '-i', sfx_inputs[1],
            '-filter_complex',
            f'[0:a]apad=whole_dur={total_dur:.2f},volume=1.10[vo];'
            f'[1:a]apad=whole_dur={total_dur:.2f},volume=0.45[c];'
            f'[2:a]apad=whole_dur={total_dur:.2f},volume=0.55[lr];'
            '[vo][c][lr]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[out]',
            '-map', '[out]',
            '-ar', '48000', '-ac', '2',
            mixed_wav,
        ]
    else:
        cmd = [
            FFMPEG, '-y',
            '-i', vo_mp3,
            '-af', f'apad=whole_dur={total_dur:.2f},volume=1.05',
            '-ar', '48000', '-ac', '2',
            mixed_wav,
        ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with wave.open(mixed_wav, 'rb') as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        raw_pcm = array.array('h')
        raw_pcm.frombytes(wf.readframes(wf.getnframes()))
    pcm_mono = [abs(raw_pcm[i]) / 32768.0 for i in range(0, len(raw_pcm), nch)]

    fps = 30
    total_frames = int(round(total_dur * fps))

    # Read actual installed Arabic fonts & injected ui/Sub_*_en.lng directly from archives/update.pak!
    pak_path = os.path.join(GAME_ARCH, 'update.pak')
    with IgaArchiveV11(pak_path) as ua:
        geek_glyphs, geek_atlas = _b27.extract_bitmap_font_glyphs(ua.read('fonts/GeekSpeak_Outline.igz'))
        info_glyphs, info_atlas = _b27.extract_bitmap_font_glyphs(ua.read('fonts/ProximaNova-Info.igz'))

        timeline = []
        for shot_idx, shot in enumerate(grp['specs'], start=1):
            for cue in shot['cues']:
                t0 = shot['shot_start_global'] + cue['t_local']
                dur = cue['dur']
                t1 = t0 + dur
                lng_doc = IgzDoc(ua.read(f"ui/{cue['id']}_en.lng"))
                shaped_from_pak = lng_doc.strings[0]
                sub_img = render_shaped_multiline_scaled(shaped_from_pak, geek_glyphs, geek_atlas, scale=0.45)
                spk_img = render_shaped_multiline_scaled(shape_arabic_text(cue['speaker'], wrap_width=50), info_glyphs, info_atlas, scale=0.60)
                timeline.append({
                    'id': cue['id'],
                    'shot': f'Shot {shot_idx:02d}',
                    't0': t0,
                    't1': t1,
                    'dur': dur,
                    'sub_img': sub_img,
                    'spk_img': spk_img,
                })

    W, H = 1920, 1080
    base_bg = Image.new('RGBA', (W, H), (14, 18, 28, 255))
    bg_draw = ImageDraw.Draw(base_bg)
    bg_draw.rectangle([0, 0, W, 110], fill=(9, 12, 20, 255))
    bg_draw.rectangle([0, H - 270, W, H], fill=(10, 13, 22, 255))
    bg_draw.line([(120, 110), (W - 120, 110)], fill=(45, 70, 110, 255), width=2)
    bg_draw.line([(120, H - 270), (W - 120, H - 270)], fill=(55, 85, 130, 255), width=2)

    header_ar = f"كراش بانديكوت: الثلاثية المرممة — {grp['title_ar']}"
    title_img = render_shaped_multiline_scaled(shape_arabic_text(header_ar, wrap_width=100), info_glyphs, info_atlas, scale=0.62)
    base_bg.alpha_composite(title_img, ((W - title_img.width) // 2, 34))

    no_speech_badge = render_shaped_multiline_scaled(
        shape_arabic_text('[ مؤثرات وموسيقى المشهد ]', wrap_width=60),
        info_glyphs,
        info_atlas,
        scale=0.52,
    )

    out_mp4 = os.path.join(REPORTS_DIR, f'{args.scene}_Arabic_Preview.mp4')
    proc = subprocess.Popen(
        [
            FFMPEG, '-y',
            '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps),
            '-i', 'pipe:0',
            '-i', mixed_wav,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            out_mp4,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        ui_font = ImageFont.load_default(size=22)
    except TypeError:
        ui_font = ImageFont.load_default()

    # Save mid-points of first 3 cues for visual spot inspection
    sample_fidxs = {int(round(((c['t0'] + c['t1']) * 0.5) * fps)): os.path.join(LOGS_DIR, f"{args.scene}_sample_{i}.png") for i, c in enumerate(timeline[:3])}

    n_bars = 72
    samples_per_frame = sr // fps

    for fidx in range(total_frames):
        t = fidx / fps
        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        prog_w = int((t / total_dur) * (W - 240))
        draw.rectangle([120, 126, W - 120, 134], fill=(28, 36, 54, 255))
        if prog_w > 0:
            draw.rectangle([120, 126, 120 + prog_w, 134], fill=(255, 165, 45, 255))
        draw.text(
            (130, 146),
            f"{t:05.2f}s / {total_dur:05.2f}s   |   {args.scene} ({len(timeline)} cues from update.pak)",
            font=ui_font,
            fill=(150, 175, 210, 255),
        )

        s0 = max(0, min(len(pcm_mono) - samples_per_frame, fidx * samples_per_frame))
        win = pcm_mono[s0:s0 + samples_per_frame]
        step_b = max(1, len(win) // n_bars)
        bar_w = 18
        gap = 4
        start_x = (W - (n_bars * (bar_w + gap) - gap)) // 2
        mid_y = 460
        for bi in range(n_bars):
            sl = win[bi * step_b:(bi + 1) * step_b]
            lvl = sum(sl) / len(sl) if sl else 0.0
            bh = max(4, min(210, int(lvl * 900)))
            bx = start_x + bi * (bar_w + gap)
            color = (255, 175, 55, 255) if lvl > 0.05 else (70, 135, 215, 255)
            draw.rounded_rectangle([bx, mid_y - bh, bx + bar_w, mid_y + bh], radius=4, fill=color)

        active = next((c for c in timeline if c['t0'] <= t <= c['t1']), None)
        if active is not None:
            dt = t - active['t0']
            fade_in = min(0.10, active['dur'] * 0.25)
            fade_out_s = max(fade_in + 0.10, active['dur'] - 0.15)
            if dt < fade_in and fade_in > 0:
                alpha = dt / fade_in
            elif dt > fade_out_s and (active['dur'] - fade_out_s) > 0:
                alpha = max(0.0, (active['dur'] - dt) / (active['dur'] - fade_out_s))
            else:
                alpha = 1.0

            sub_img = active['sub_img']
            spk_img = active['spk_img']
            if alpha < 0.999:
                r, g, b, a_ch = sub_img.split()
                sub_img = Image.merge('RGBA', (r, g, b, a_ch.point(lambda p: int(p * alpha))))
                r2, g2, b2, a2 = spk_img.split()
                spk_img = Image.merge('RGBA', (r2, g2, b2, a2.point(lambda p: int(p * alpha))))

            frame.alpha_composite(spk_img, ((W - spk_img.width) // 2, 748))
            frame.alpha_composite(sub_img, ((W - sub_img.width) // 2, 915 - sub_img.height // 2))
            draw.text((W - 430, 146), f"{active['shot']}  |  {active['id']}", font=ui_font, fill=(255, 200, 90, 255))
        else:
            frame.alpha_composite(no_speech_badge, ((W - no_speech_badge.width) // 2, 895))

        if fidx in sample_fidxs:
            frame.save(sample_fidxs[fidx])

        proc.stdin.write(frame.convert('RGB').tobytes())

    proc.stdin.close()
    rc = proc.wait()
    assert rc == 0, f'FFmpeg failed with exit code {rc}'
    print(f'PREVIEW MP4 READY: {out_mp4} ({os.path.getsize(out_mp4):,} B)')

    if args.copy_desktop:
        desktop_dst = os.path.join(os.path.expanduser('~'), 'Desktop', os.path.basename(out_mp4))
        shutil.copy2(out_mp4, desktop_dst)
        print(f'COPIED TO DESKTOP: {desktop_dst} (sha256={_b27.sha256_file(desktop_dst)})')


if __name__ == '__main__':
    main()
