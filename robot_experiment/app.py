import streamlit as st
import pandas as pd
import random
import io
from datetime import datetime
from pathlib import Path

# 始终相对于 app.py 本身所在目录定位素材，无论在哪里运行
BASE_DIR   = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"
AUDIO_DIR  = BASE_DIR / "audio"

def find_file(folder, stem, exts):
    """查找文件：支持两种结构：
    1. 直接文件：audio/cognitive.wav 或 images/A01.png.jpg
    2. 文件夹内：audio/cognitive.wav/Q6_HH_M.mp3.wav（文件夹以 stem 命名，里面任意文件）
    """
    if not folder.exists():
        return None

    def _search(directory, inside_stem_dir=False):
        for f in sorted(directory.iterdir()):
            if f.is_file():
                if inside_stem_dir:
                    # 在 stem 命名的文件夹里，接受任何音频/图片文件
                    for ext in exts:
                        if f.name.endswith(ext):
                            return f
                    return f  # 兜底返回文件夹里第一个文件
                name = f.name
                for ext in exts:
                    if name == stem + ext or name.startswith(stem + ext + "."):
                        return f
                if name.startswith(stem) and name != stem:
                    return f
        subdirs = sorted(
            [d for d in directory.iterdir() if d.is_dir()],
            key=lambda d: (0 if d.name.startswith(stem) else 1, d.name)
        )
        for sub in subdirs:
            result = _search(sub, inside_stem_dir=sub.name.startswith(stem))
            if result:
                return result
        return None

    return _search(folder)


st.set_page_config(
    page_title="机器人声音外观匹配研究",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans SC', sans-serif; }
.progress-wrap { background:#e8e8e8; border-radius:8px; height:8px; width:100%; margin:8px 0 4px 0; }
.progress-fill { background:linear-gradient(90deg,#2563EB,#7C3AED); border-radius:8px; height:8px; }
.progress-text { text-align:right; font-size:12px; color:#9CA3AF; margin:0 0 16px 0; }
.scene-card {
    background:linear-gradient(135deg,#EFF6FF,#F5F3FF);
    border-left:4px solid #2563EB; border-radius:0 12px 12px 0;
    padding:16px 20px; margin:12px 0; font-size:15px; line-height:1.7; color:#1e3a5f;
}
.audio-hint {
    background:#FEF9C3; border:1px solid #F59E0B; border-radius:8px;
    padding:10px 16px; font-size:13px; color:#78350F; margin:12px 0;
}
.scale-label { display:flex; justify-content:space-between; font-size:12px; color:#9CA3AF; margin:-8px 0 16px 0; }
.q-title { font-size:14px; font-weight:500; color:#374151; margin-bottom:2px; }
.divider { border:none; border-top:1px solid #E5E7EB; margin:20px 0; }
.page-header { text-align:center; padding:24px 0 8px 0; }
.page-header h1 { font-size:22px; font-weight:700; color:#111827; }
.page-header p { font-size:14px; color:#6B7280; }
.download-box {
    background:linear-gradient(135deg,#ECFDF5,#EFF6FF);
    border:2px solid #10B981; border-radius:16px;
    padding:28px 24px; text-align:center; margin:24px 0;
}
.stButton > button {
    background:linear-gradient(90deg,#2563EB,#7C3AED);
    color:white; border:none; border-radius:10px;
    padding:12px 32px; font-size:15px; font-weight:500; width:100%;
    font-family:'Noto Sans SC',sans-serif;
}
[data-testid="stDownloadButton"] > button {
    background:linear-gradient(90deg,#059669,#0284C7) !important;
    color:white; border:none; border-radius:12px;
    padding:16px 32px; font-size:17px; font-weight:700; width:100%;
    font-family:'Noto Sans SC',sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── 刺激材料（A卷18组）────────────────────────────────────────
STIMULI = [
    {"id":"S01","scene_type":"cognitive","appearance_id":"A01","voice_id":"cognitive",
     "scene_text":"您正在政务服务中心办理社保手续，需要机器人帮助您快速查询所需材料清单和办理流程，要求信息准确、回答简洁。"},
    {"id":"S02","scene_type":"cognitive","appearance_id":"A03","voice_id":"emotional",
     "scene_text":"您正在政务服务中心办理社保手续，需要机器人帮助您快速查询所需材料清单和办理流程，要求信息准确、回答简洁。"},
    {"id":"S03","scene_type":"cognitive","appearance_id":"A05","voice_id":"balanced",
     "scene_text":"您正在政务服务中心办理社保手续，需要机器人帮助您快速查询所需材料清单和办理流程，要求信息准确、回答简洁。"},
    {"id":"S04","scene_type":"cognitive","appearance_id":"A02","voice_id":"cognitive",
     "scene_text":"您正在政务服务中心办理社保手续，需要机器人帮助您快速查询所需材料清单和办理流程，要求信息准确、回答简洁。"},
    {"id":"S05","scene_type":"cognitive","appearance_id":"A04","voice_id":"emotional",
     "scene_text":"您正在政务服务中心办理社保手续，需要机器人帮助您快速查询所需材料清单和办理流程，要求信息准确、回答简洁。"},
    {"id":"S06","scene_type":"cognitive","appearance_id":"A06","voice_id":"balanced",
     "scene_text":"您正在政务服务中心办理社保手续，需要机器人帮助您快速查询所需材料清单和办理流程，要求信息准确、回答简洁。"},
    {"id":"S07","scene_type":"mixed","appearance_id":"A04","voice_id":"cognitive",
     "scene_text":"您正在医院咨询慢性病用药报销政策，希望机器人既能准确解释政策条款，也能以较为亲和的方式回应您的疑问和担忧。"},
    {"id":"S08","scene_type":"mixed","appearance_id":"A06","voice_id":"emotional",
     "scene_text":"您正在医院咨询慢性病用药报销政策，希望机器人既能准确解释政策条款，也能以较为亲和的方式回应您的疑问和担忧。"},
    {"id":"S09","scene_type":"mixed","appearance_id":"A02","voice_id":"balanced",
     "scene_text":"您正在医院咨询慢性病用药报销政策，希望机器人既能准确解释政策条款，也能以较为亲和的方式回应您的疑问和担忧。"},
    {"id":"S10","scene_type":"mixed","appearance_id":"A05","voice_id":"cognitive",
     "scene_text":"您正在医院咨询慢性病用药报销政策，希望机器人既能准确解释政策条款，也能以较为亲和的方式回应您的疑问和担忧。"},
    {"id":"S11","scene_type":"mixed","appearance_id":"A01","voice_id":"emotional",
     "scene_text":"您正在医院咨询慢性病用药报销政策，希望机器人既能准确解释政策条款，也能以较为亲和的方式回应您的疑问和担忧。"},
    {"id":"S12","scene_type":"mixed","appearance_id":"A03","voice_id":"balanced",
     "scene_text":"您正在医院咨询慢性病用药报销政策，希望机器人既能准确解释政策条款，也能以较为亲和的方式回应您的疑问和担忧。"},
    {"id":"S13","scene_type":"emotional","appearance_id":"A06","voice_id":"cognitive",
     "scene_text":"您独自在外就医，因手续复杂感到焦虑，希望机器人能耐心陪伴解释，给予情绪上的安抚和鼓励。"},
    {"id":"S14","scene_type":"emotional","appearance_id":"A02","voice_id":"emotional",
     "scene_text":"您独自在外就医，因手续复杂感到焦虑，希望机器人能耐心陪伴解释，给予情绪上的安抚和鼓励。"},
    {"id":"S15","scene_type":"emotional","appearance_id":"A04","voice_id":"balanced",
     "scene_text":"您独自在外就医，因手续复杂感到焦虑，希望机器人能耐心陪伴解释，给予情绪上的安抚和鼓励。"},
    {"id":"S16","scene_type":"emotional","appearance_id":"A03","voice_id":"cognitive",
     "scene_text":"您独自在外就医，因手续复杂感到焦虑，希望机器人能耐心陪伴解释，给予情绪上的安抚和鼓励。"},
    {"id":"S17","scene_type":"emotional","appearance_id":"A05","voice_id":"emotional",
     "scene_text":"您独自在外就医，因手续复杂感到焦虑，希望机器人能耐心陪伴解释，给予情绪上的安抚和鼓励。"},
    {"id":"S18","scene_type":"emotional","appearance_id":"A01","voice_id":"balanced",
     "scene_text":"您独自在外就医，因手续复杂感到焦虑，希望机器人能耐心陪伴解释，给予情绪上的安抚和鼓励。"},
]

SCENE_LABELS = {
    "cognitive": "🧠 认知主导型场景",
    "mixed":     "⚖️ 混合需求型场景",
    "emotional": "💛 情感主导型场景"
}

def init_state():
    defs = {
        "page":"consent", "pid":f"P{datetime.now().strftime('%m%d%H%M%S')}",
        "gender":None,"age_group":None,"ai_use":None,
        "order":None,"trial_idx":0,"responses":[],
    }
    for k,v in defs.items():
        if k not in st.session_state:
            st.session_state[k]=v

init_state()

def show_progress(idx, total):
    pct = int(idx/total*100)
    st.markdown(f"""
    <div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>
    <p class="progress-text">第 {idx+1} 组 / 共 {total} 组</p>""", unsafe_allow_html=True)

def to_csv_bytes():
    rows = [{
        "participant_id": st.session_state.pid,
        "gender":         st.session_state.gender,
        "age_group":      st.session_state.age_group,
        "ai_use":         st.session_state.ai_use,
        "timestamp":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stimulus_id":    r["stimulus_id"],
        "scene_type":     r["scene_type"],
        "appearance_id":  r["appearance_id"],
        "voice_id":       r["voice_id"],
        "match_score":    r["scores"][0],
        "scene_fit_score":r["scores"][1],
        "warmth_score":   r["scores"][2],
        "competence_score":r["scores"][3],
        "adoption_score": r["scores"][4],
    } for r in st.session_state.responses]
    buf = io.BytesIO()
    pd.DataFrame(rows).to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()

# ── 知情同意 ──────────────────────────────────────────────────
def page_consent():
    st.markdown('<div class="page-header"><h1>🤖 服务机器人声音外观匹配研究</h1><p>参与者知情同意书</p></div>',
                unsafe_allow_html=True)
    st.markdown("""
**感谢您参与本研究！**

本研究旨在了解用户在不同服务场景下，对服务机器人**声音与外观匹配程度**的主观感知。

**实验内容**：共 18 组「场景 + 机器人图片 + 语音」，每组评分 5 个维度，预计耗时 **8–12 分钟**。

**数据说明**：全程匿名，仅用于学术研究。填完后请点击**下载数据文件**发送给研究者。

**设备要求**：请使用耳机或音箱，在安静环境中完成。
""")
    if st.checkbox("✅ 我已阅读上述说明，同意参与本研究"):
        if st.button("开始参与 →"):
            st.session_state.page = "info"; st.rerun()

# ── 基本信息 ──────────────────────────────────────────────────
def page_info():
    st.markdown('<div class="page-header"><h1>基本信息</h1><p>仅用于样本描述，不涉及隐私</p></div>',
                unsafe_allow_html=True)
    g  = st.radio("您的性别", ["男","女","其他/不便透露"])
    a  = st.radio("您的年龄段", ["18岁以下","18–25岁","26–35岁","36–45岁","46岁及以上"])
    u  = st.radio("是否使用过智能语音助手或服务机器人？",
                  ["经常使用","偶尔使用","很少使用","从未使用"])
    if st.button("下一步 →"):
        st.session_state.gender=g; st.session_state.age_group=a; st.session_state.ai_use=u
        st.session_state.page="audio_check"; st.rerun()

# ── 音频检查 ──────────────────────────────────────────────────
def page_audio_check():
    st.markdown('<div class="page-header"><h1>🎧 音频检查</h1><p>请确认能清晰听到音频后再开始</p></div>',
                unsafe_allow_html=True)
    st.info("请调整音量至适中，播放测试音频：")
    p = find_file(AUDIO_DIR, "cognitive", [".wav", ".mp3"])
    if p:
        fmt = "audio/mp3" if str(p).endswith(".mp3") else "audio/wav"
        st.audio(p.read_bytes(), format=fmt)
    else:
        st.warning(f"⚠️ 未找到音频文件（cognitive.wav），请确认已上传到 audio/ 文件夹。")
    ans = st.radio("您能清晰听到音频吗？", ["✅ 是，可以听到","❌ 否，听不到"])
    if "✅" in ans:
        if st.button("确认，开始实验 →"):
            order = list(range(len(STIMULI))); random.shuffle(order)
            st.session_state.order=order; st.session_state.page="experiment"; st.rerun()
    else:
        st.error("请检查耳机/音箱设置后重试。")

# ── 正式实验 ──────────────────────────────────────────────────
def page_experiment():
    total = len(STIMULI)
    idx   = st.session_state.trial_idx
    if idx >= total:
        st.session_state.page="finish"; st.rerun(); return

    stim = STIMULI[st.session_state.order[idx]]
    show_progress(idx, total)

    st.markdown(f"**{SCENE_LABELS.get(stim['scene_type'],'')}**")
    st.markdown(f'<div class="scene-card">{stim["scene_text"]}</div>', unsafe_allow_html=True)

    img = find_file(IMAGES_DIR, stim['appearance_id'], [".png", ".jpg", ".jpeg"])
    if img and img.is_file():
        c1,c2,c3 = st.columns([1,2,1])
        with c2: st.image(str(img), use_container_width=True)
    else:
        st.warning(f"⚠️ 图片未找到：images/{stim['appearance_id']}.png")

    st.markdown('<div class="audio-hint">👂 请先播放音频，听完后再作答 ↓</div>', unsafe_allow_html=True)
    aud = find_file(AUDIO_DIR, stim['voice_id'], [".wav", ".mp3"])
    if aud and aud.is_file():
        fmt = "audio/mp3" if str(aud).endswith(".mp3") else "audio/wav"
        st.audio(aud.read_bytes(), format=fmt)
    else:
        st.warning(f"⚠️ 音频未找到：audio/{stim['voice_id']}.*，请确认已上传。")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### 请根据视听感受评分（1=完全不同意，7=完全同意）")

    qs = [
        ("q1","① 该机器人的声音与外观是**协调匹配**的"),
        ("q2","② 这个组合**适合当前服务场景**"),
        ("q3","③ 我感受到该机器人具有**亲和、温暖**的感觉"),
        ("q4","④ 该机器人给人**专业、可靠**的感觉"),
        ("q5","⑤ 我**愿意接受**该机器人提供的服务"),
    ]
    scores = []
    for key, label in qs:
        st.markdown(f'<div class="q-title">{label}</div>', unsafe_allow_html=True)
        v = st.slider("", 1, 7, 4, key=f"{stim['id']}_{key}", label_visibility="collapsed")
        st.markdown('<div class="scale-label"><span>1 完全不同意</span><span>4 中立</span><span>7 完全同意</span></div>',
                    unsafe_allow_html=True)
        scores.append(v)

    remain = total - idx - 1
    btn = "✅ 完成所有评分，前往下载页" if remain == 0 else f"保存并继续 → （还剩 {remain} 组）"
    if st.button(btn):
        st.session_state.responses.append({
            "stimulus_id":stim["id"],"scene_type":stim["scene_type"],
            "appearance_id":stim["appearance_id"],"voice_id":stim["voice_id"],"scores":scores,
        })
        st.session_state.trial_idx += 1; st.rerun()

# ── 完成页 ────────────────────────────────────────────────────
def page_finish():
    st.markdown("""
    <div style="text-align:center;padding:40px 20px 16px">
      <div style="font-size:56px">🎉</div>
      <h2 style="font-size:22px;font-weight:700;color:#111827;margin:12px 0 8px">
        全部完成，感谢您的参与！
      </h2>
      <p style="color:#6B7280;font-size:14px">
        您已完成全部 18 组评分，您的数据对本研究非常有价值。
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="download-box">
      <h3 style="font-size:18px;color:#065F46;margin:0 0 8px">📥 请下载并发送数据文件</h3>
      <p style="font-size:14px;color:#374151;margin:0 0 4px">
        点击下方按钮 → 文件自动下载到您的手机/电脑<br>
        然后通过 <strong>微信 / 邮件</strong> 发送给研究者
      </p>
      <p style="font-size:12px;color:#9CA3AF">文件仅约 5KB，不含任何隐私信息</p>
    </div>""", unsafe_allow_html=True)

    fname = f"匹配实验_{st.session_state.pid}.csv"
    st.download_button(
        label="⬇️  点击下载数据文件",
        data=to_csv_bytes(),
        file_name=fname,
        mime="text/csv",
    )
    st.info(f"💬 下载后请将文件「{fname}」发给研究者，感谢配合！")

    with st.expander("查看本次评分记录"):
        if st.session_state.responses:
            df = pd.DataFrame([{
                "组号":r["stimulus_id"],"场景":r["scene_type"],
                "匹配度":r["scores"][0],"场景适配":r["scores"][1],
                "温暖感":r["scores"][2],"专业感":r["scores"][3],"采纳意愿":r["scores"][4],
            } for r in st.session_state.responses])
            st.dataframe(df, use_container_width=True, hide_index=True)

# ── 路由 ──────────────────────────────────────────────────────
{
    "consent":     page_consent,
    "info":        page_info,
    "audio_check": page_audio_check,
    "experiment":  page_experiment,
    "finish":      page_finish,
}.get(st.session_state.page, page_consent)()
