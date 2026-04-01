import streamlit as st
import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === 頁面基礎設定 ===
st.set_page_config(page_title="RF Filter Designer Pro", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# === 🎨 色票定義 (深海霓虹主題 Deep Sea Neon) ===
COLOR_BG_MAIN    = "#0b162d"   # 網頁主背景
COLOR_BG_CARD    = "#152238"   # 面板卡片背景
COLOR_ACCENT     = "#D4AF37"   # 皇家金 (UI 強調色)
COLOR_TEXT_NM    = "#E0E0E0"   # 一般文字

# [NEW] 專業圖表專用色票
COLOR_PLOT_BG    = "#0A122A"   # 圖表極深軍藍背景 (營造暗室效果)
COLOR_GRID       = "#3A4B66"   # 淡淡的網格線
COLOR_S21_NEON   = "#00FFC8"   # S21: 霓虹青 (Vibrant Teal)
COLOR_S11_AMBER  = "#FF9F1C"   # S11: 琥珀金 (Amber)
COLOR_GD_LIME    = "#32CD32"   # Group Delay: 萊姆綠
COLOR_AXIS_LINE  = "#6c7a9c"   # 座標軸線顏色

st.markdown("""
    <style>
    .st-emotion-cache-1y4p8pa { padding-top: 2rem; }
    .srf-text { color: #32CD32; font-family: 'Consolas', monospace; font-weight: bold; }
    .srf-bypass { color: #888888; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

# === CIS Database (庫存模擬) ===
CIS_DB = {
    "CAPS": {
        0.5: {"pn": "101-00050-00", "mfg": "Murata", "desc": "CAP CER 0.5PF 50V C0G 0402"},
        1.0: {"pn": "101-00100-00", "mfg": "Murata", "desc": "CAP CER 1.0PF 50V C0G 0402"},
        1.2: {"pn": "101-00120-00", "mfg": "Samsung", "desc": "CAP CER 1.2PF 50V NP0 0402"},
        1.5: {"pn": "101-00150-00", "mfg": "Murata", "desc": "CAP CER 1.5PF 50V C0G 0402"},
        1.8: {"pn": "101-00180-00", "mfg": "TDK",    "desc": "CAP CER 1.8PF 50V C0G 0402"},
        2.0: {"pn": "101-00200-00", "mfg": "Murata", "desc": "CAP CER 2.0PF 50V C0G 0402"},
        2.2: {"pn": "101-00220-00", "mfg": "Yageo",  "desc": "CAP CER 2.2PF 50V NP0 0402"},
        2.7: {"pn": "101-00270-00", "mfg": "TDK",    "desc": "CAP CER 2.7PF 50V C0G 0402"},
        3.0: {"pn": "101-00300-00", "mfg": "Murata", "desc": "CAP CER 3.0PF 50V C0G 0402"},
        3.3: {"pn": "101-00330-00", "mfg": "Samsung","desc": "CAP CER 3.3PF 50V NP0 0402"},
        3.9: {"pn": "101-00390-00", "mfg": "Murata", "desc": "CAP CER 3.9PF 50V C0G 0402"},
        4.7: {"pn": "101-00470-00", "mfg": "Yageo",  "desc": "CAP CER 4.7PF 50V NP0 0402"},
        5.6: {"pn": "101-00560-00", "mfg": "Murata", "desc": "CAP CER 5.6PF 50V C0G 0402"},
        6.8: {"pn": "101-00680-00", "mfg": "TDK",    "desc": "CAP CER 6.8PF 50V C0G 0402"},
    },
    "INDS": {
        0.5: {"pn": "102-00005-00", "mfg": "Murata", "desc": "IND 0.5NH 300MA 0402 LQP"},
        1.0: {"pn": "102-00010-00", "mfg": "Murata", "desc": "IND 1.0NH 300MA 0402 LQP"},
        1.2: {"pn": "102-00012-00", "mfg": "Coilcraft","desc": "IND 1.2NH 450MA 0402 WireWound"},
        1.5: {"pn": "102-00015-00", "mfg": "Murata", "desc": "IND 1.5NH 300MA 0402 LQP"},
        1.8: {"pn": "102-00018-00", "mfg": "TDK",    "desc": "IND 1.8NH 300MA 0402 MLG"},
        2.0: {"pn": "102-00020-00", "mfg": "Murata", "desc": "IND 2.0NH 300MA 0402 LQP"},
        2.2: {"pn": "102-00022-00", "mfg": "Sunlord","desc": "IND 2.2NH 300MA 0402 HQ"},
        2.7: {"pn": "102-00027-00", "mfg": "Murata", "desc": "IND 2.7NH 300MA 0402 LQP"},
        3.3: {"pn": "102-00033-00", "mfg": "Coilcraft","desc": "IND 3.3NH 400MA 0402 WireWound"},
        3.9: {"pn": "102-00039-00", "mfg": "Murata", "desc": "IND 3.9NH 300MA 0402 LQP"},
        4.7: {"pn": "102-00047-00", "mfg": "TDK",    "desc": "IND 4.7NH 300MA 0402 MLG"},
        5.6: {"pn": "102-00056-00", "mfg": "Murata", "desc": "IND 5.6NH 300MA 0402 LQP"},
        6.8: {"pn": "102-00068-00", "mfg": "Murata", "desc": "IND 6.8NH 300MA 0402 LQP"},
        8.2: {"pn": "102-00082-00", "mfg": "TDK",    "desc": "IND 8.2NH 300MA 0402 MLG"},
    }
}

CAP_VENDORS = ["Any"] + sorted(list(set([v["mfg"] for v in CIS_DB["CAPS"].values()])))
IND_VENDORS = ["Any"] + sorted(list(set([v["mfg"] for v in CIS_DB["INDS"].values()])))

# === 狀態初始化 ===
if 'ladder' not in st.session_state:
    st.session_state.ladder = [
        {"topo": "Shunt (||)", "type": "Capacitor (C)", "val": 1.2},
        {"topo": "Series (—)", "type": "Inductor (L)", "val": 2.2},
        {"topo": "Shunt (||)", "type": "Capacitor (C)", "val": 2.2},
        {"topo": "Shunt (||)", "type": "Inductor (L)", "val": 0.0},
        {"topo": "Series (—)", "type": "Capacitor (C)", "val": 0.0},
        {"topo": "Shunt (||)", "type": "Inductor (L)", "val": 0.0},
    ]

if 'notch' not in st.session_state:
    st.session_state.notch = {
        "in_match": {"type": "Inductor (L)", "val": 0.0},
        "s1": {"type": "Inductor (L)", "val": 0.8},
        "s2": {"type": "Inductor (L)", "val": 0.8},
        "leg_a": {"type": "Inductor (L)", "val": 12.0},
        "leg_b": {"type": "Capacitor (C)", "val": 3.4},
        "out_match": {"type": "Inductor (L)", "val": 0.0}
    }

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = None

# === 數學底層 ===
def get_Z_raw(t, v, fs, use_para, ql, cp_pf, qc, esl_nh):
    v_si = v * (1e-12 if t=="C" else 1e-9)
    w = 2*np.pi*fs
    if not use_para: 
        return (1j*w*v_si if t=="L" else 1/(1j*w*v_si+1e-18)), t
    
    if t=="L": 
        z_ideal = 1j*w*v_si
        rs = (w*v_si)/(ql+1e-9)
        cp_si = cp_pf * 1e-12
        return 1/((1/(z_ideal+rs)) + 1j*w*cp_si + 1e-18), t
    else: 
        z_ideal = 1/(1j*w*v_si+1e-18)
        resr = 1/(w*v_si*qc+1e-9)
        esl_si = esl_nh * 1e-9
        return z_ideal + resr + 1j*w*esl_si, t

def get_mat(z, p):
    n=len(z); m=np.zeros((n,2,2),dtype=complex); m[:,0,0]=1; m[:,1,1]=1
    if p=='series': m[:,0,1]=z
    else: m[:,1,0]=1/(z+1e-18)
    return m

def shunt_mat(y):
    n=len(y); m=np.zeros((n,2,2),dtype=complex); m[:,0,0]=1; m[:,1,1]=1; m[:,1,0]=y
    return m

def calc_srf(val, ctype, L_Cp, C_ESL):
    if val == 0: return "<span class='srf-bypass'>-- Bypass --</span>"
    try:
        if "L" in ctype: srf = 1/(2*np.pi*np.sqrt(val*1e-9*L_Cp*1e-12))
        else: srf = 1/(2*np.pi*np.sqrt(val*1e-12*C_ESL*1e-9))
        txt = f"{srf/1e9:.2f} GHz" if srf>1e9 else f"{srf/1e6:.0f} MHz"
        return f"<span class='srf-text'>{txt}</span>"
    except: return "<span class='srf-bypass'>--</span>"

# === 側邊欄 (Sidebar) ===
with st.sidebar:
    st.title("📡 RF Designer Pro")
    st.markdown("---")
    
    st.subheader("📍 Operating Mode")
    app_mode = st.radio("Select Topology", ["🪜 Custom Ladder", "🎛️ T-Notch Filter", "🤖 AI Auto-Design"], label_visibility="collapsed")
    
    st.markdown("---")
    st.subheader("⚙️ Global Settings")
    col1, col2 = st.columns(2)
    f_start = col1.number_input("Start (MHz)", value=500, step=100)
    f_stop = col2.number_input("Stop (MHz)", value=8000, step=500)
    f_pts = st.number_input("Points", value=2001, step=100)
    
    use_para = st.checkbox("Enable Parasitics Model", value=True)
    show_gd = st.checkbox("Show Group Delay", value=True) 
    
    with st.expander("Parasitic Parameters", expanded=use_para):
        L_Q = st.number_input("Inductor Q", value=80.0)
        L_Cp = st.number_input("Inductor Cp (pF)", value=0.1)
        C_Q = st.number_input("Capacitor Q", value=100.0)
        C_ESL = st.number_input("Capacitor ESL (nH)", value=0.5)

# === 主畫面渲染 ===
m_tot = None 
freqs = np.linspace(f_start*1e6, f_stop*1e6, int(f_pts))

# ---------------------------------------------------------
# Mode 1: Custom Ladder
# ---------------------------------------------------------
if app_mode == "🪜 Custom Ladder":
    st.header("🪜 Custom 6-Stage Ladder Network")
    st.markdown("Configure series/shunt topologies dynamically. Set value to `0` to bypass a stage.")
    
    h_cols = st.columns([1, 2, 2, 2, 2])
    for col, text in zip(h_cols, ["Stage", "Topology", "Component", "Value", "SRF (Resonance)"]):
        col.markdown(f"**{text}**")
        
    for i in range(6):
        c = st.columns([1, 2, 2, 2, 2])
        c[0].markdown(f"**Stage {i+1}**")
        
        topo = c[1].selectbox("Topo", ["Shunt (||)", "Series (—)"], index=0 if st.session_state.ladder[i]["topo"]=="Shunt (||)" else 1, key=f"l_topo_{i}", label_visibility="collapsed")
        ctype = c[2].selectbox("Type", ["Capacitor (C)", "Inductor (L)"], index=0 if st.session_state.ladder[i]["type"]=="Capacitor (C)" else 1, key=f"l_type_{i}", label_visibility="collapsed")
        val = c[3].number_input("Val", value=st.session_state.ladder[i]["val"], step=0.1, min_value=0.0, format="%.2f", key=f"l_val_{i}", label_visibility="collapsed")
        
        st.session_state.ladder[i] = {"topo": topo, "type": ctype, "val": val}
        c[4].markdown(calc_srf(val, ctype, L_Cp, C_ESL), unsafe_allow_html=True)

    m_tot = np.zeros((int(f_pts),2,2),dtype=complex); m_tot[:,0,0]=1; m_tot[:,1,1]=1
    for stg in st.session_state.ladder:
        if stg["val"] > 0:
            t_code = "C" if "Capacitor" in stg["type"] else "L"
            z, _ = get_Z_raw(t_code, stg["val"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL)
            if "Shunt" in stg["topo"]: m_tot = m_tot @ shunt_mat(1/(z+1e-18))
            else: m_tot = m_tot @ get_mat(z, 'series')

# ---------------------------------------------------------
# Mode 2: T-Notch Filter
# ---------------------------------------------------------
elif app_mode == "🎛️ T-Notch Filter":
    st.header("🎛️ T-Notch Filter Configuration")
    
    h_cols = st.columns([2, 2, 2, 2])
    for col, text in zip(h_cols, ["Position", "Component", "Value", "SRF (Resonance)"]):
        col.markdown(f"**{text}**")
        
    def create_notch_row(key_name, label):
        c = st.columns([2, 2, 2, 2])
        c[0].markdown(f"**{label}**")
        state = st.session_state.notch[key_name]
        ctype = c[1].selectbox("Type", ["Capacitor (C)", "Inductor (L)"], index=0 if state["type"]=="Capacitor (C)" else 1, key=f"n_type_{key_name}", label_visibility="collapsed")
        val = c[2].number_input("Val", value=state["val"], step=0.1, min_value=0.0, format="%.2f", key=f"n_val_{key_name}", label_visibility="collapsed")
        st.session_state.notch[key_name] = {"type": ctype, "val": val}
        c[3].markdown(calc_srf(val, ctype, L_Cp, C_ESL), unsafe_allow_html=True)
        return {"type": ctype, "val": val}

    cfg = [("in_match", "1. In Match (Shunt)"), ("s1", "2. Series 1 (Series)"), ("s2", "3. Series 2 (Series)"),
           ("leg_a", "4. Notch Leg A (Shunt)"), ("leg_b", "5. Notch Leg B (Shunt)"), ("out_match", "6. Out Match (Shunt)")]
    
    n_res = {}
    for k, lbl in cfg: n_res[k] = create_notch_row(k, lbl)

    m_tot = np.zeros((int(f_pts),2,2),dtype=complex); m_tot[:,0,0]=1; m_tot[:,1,1]=1
    
    def apply_notch(key, is_shunt):
        global m_tot
        v = n_res[key]["val"]
        if v > 0:
            tc = "C" if "Capacitor" in n_res[key]["type"] else "L"
            z, _ = get_Z_raw(tc, v, freqs, use_para, L_Q, L_Cp, C_Q, C_ESL)
            m_tot = m_tot @ (shunt_mat(1/(z+1e-18)) if is_shunt else get_mat(z, 'series'))
            
    apply_notch("in_match", True)
    apply_notch("s1", False)
    
    va, vb = n_res["leg_a"]["val"], n_res["leg_b"]["val"]
    if va > 0 or vb > 0:
        za, zb = np.zeros_like(freqs, dtype=complex), np.zeros_like(freqs, dtype=complex)
        if va>0: za, _ = get_Z_raw("C" if "Capacitor" in n_res["leg_a"]["type"] else "L", va, freqs, use_para, L_Q, L_Cp, C_Q, C_ESL)
        if vb>0: zb, _ = get_Z_raw("C" if "Capacitor" in n_res["leg_b"]["type"] else "L", vb, freqs, use_para, L_Q, L_Cp, C_Q, C_ESL)
        m_tot = m_tot @ shunt_mat(1/(za+zb+1e-18))
        
    apply_notch("s2", False)
    apply_notch("out_match", True)

# ---------------------------------------------------------
# Mode 3: AI Auto-Design
# ---------------------------------------------------------
elif app_mode == "🤖 AI Auto-Design":
    st.header("🤖 AI Auto-Design & BOM Generation")
    
    col_cfg, col_bom = st.columns([1, 1.2])
    
    with col_cfg:
        with st.container(border=True):
            st.subheader("🎯 Design Specifications")
            
            use_plm = st.checkbox("🔗 Sync with Approved Vendor List (AVL)", value=True)
            if use_plm:
                v_col1, v_col2 = st.columns(2)
                pref_cap = v_col1.selectbox("Preferred Cap Vendor", CAP_VENDORS)
                pref_ind = v_col2.selectbox("Preferred Ind Vendor", IND_VENDORS)
            else:
                pref_cap, pref_ind = "Any", "Any"
            
            st.markdown("---")
            st.markdown("**[ Passband Integrity Protection ]**")
            pb_start, pb_stop = st.slider("Passband Range (MHz)", min_value=100, max_value=8000, value=(1570, 1580), step=10)
            max_loss = st.number_input("Max Insertion Loss (dB)", value=0.8, step=0.1)
            
            st.markdown("---")
            st.markdown("**[ Rejection Targets ]**")
            fc = st.number_input("Cutoff Freq (MHz)", value=2600, step=100)
            r1_f = st.number_input("Rej Target 1 Freq (MHz)", value=4800, step=100)
            r1_a = st.number_input("Rej Target 1 Atten (dB)", value=20, step=5)
            r2_f = st.number_input("Rej Target 2 Freq (MHz)", value=7200, step=100)
            r2_a = st.number_input("Rej Target 2 Atten (dB)", value=25, step=5)

            if st.button("🚀 RUN AI OPTIMIZATION", use_container_width=True, type="primary"):
                with st.spinner('Running Monte Carlo Simulation (5000 Iterations)...'):
                    
                    caps_pool, inds_pool = [], []
                    if use_plm:
                        for v, info in CIS_DB["CAPS"].items():
                            if pref_cap == "Any" or info["mfg"] == pref_cap: caps_pool.append(v)
                        for v, info in CIS_DB["INDS"].items():
                            if pref_ind == "Any" or info["mfg"] == pref_ind: inds_pool.append(v)
                    
                    if use_plm and (not caps_pool or not inds_pool):
                        st.error("❌ Inventory Error: No components found for the selected preferred vendor.")
                    else:
                        best_score = float('inf'); best_vals = (0,0,0)
                        
                        def sim_point(f, c1, l2, c3):
                            fs = np.array([f]); m = np.zeros((1,2,2),dtype=complex); m[:,0,0]=1; m[:,1,1]=1
                            z,_ = get_Z_raw("C",c1,fs,use_para,L_Q,L_Cp,C_Q,C_ESL); m = m @ shunt_mat(1/(z+1e-18))
                            z,_ = get_Z_raw("L",l2,fs,use_para,L_Q,L_Cp,C_Q,C_ESL); m = m @ get_mat(z,'series')
                            z,_ = get_Z_raw("C",c3,fs,use_para,L_Q,L_Cp,C_Q,C_ESL); m = m @ shunt_mat(1/(z+1e-18))
                            return 20*np.log10(np.abs(2.0/(m[:,0,0] + m[:,0,1]/50 + m[:,1,0]*50 + m[:,1,1]))+1e-15)[0]

                        for _ in range(5000):
                            if use_plm: c1, l2, c3 = random.choice(caps_pool), random.choice(inds_pool), random.choice(caps_pool)
                            else: c1, l2, c3 = random.uniform(0.1, 5.0), random.uniform(0.5, 15.0), random.uniform(0.1, 5.0)
                            
                            l_pass = sim_point(pb_stop * 1e6, c1, l2, c3)
                            l_fc = sim_point(fc * 1e6, c1, l2, c3)
                            l_f1 = sim_point(r1_f * 1e6, c1, l2, c3)
                            l_f2 = sim_point(r2_f * 1e6, c1, l2, c3)
                            
                            score = 0
                            if l_pass < -max_loss: score += (abs(l_pass) - max_loss) * 500
                            if l_fc < -4: score += (abs(l_fc) - 3) * 20
                            if l_f1 > -r1_a: score += (l_f1 - (-r1_a)) * 5
                            if l_f2 > -r2_a: score += (l_f2 - (-r2_a)) * 5
                            
                            if score < best_score:
                                best_score = score; best_vals = (c1, l2, c3)
                        
                        c1, l2, c3 = best_vals
                        st.session_state.ai_results = {"c1": c1, "l2": l2, "c3": c3, "score": best_score}
                        
                        st.session_state.ladder[0] = {"topo": "Shunt (||)", "type": "Capacitor (C)", "val": c1}
                        st.session_state.ladder[1] = {"topo": "Series (—)", "type": "Inductor (L)", "val": l2}
                        st.session_state.ladder[2] = {"topo": "Shunt (||)", "type": "Capacitor (C)", "val": c3}
                        for i in range(3,6): st.session_state.ladder[i]["val"] = 0.0

    with col_bom:
        if st.session_state.ai_results is None:
            st.info("👈 Run AI Optimization to generate BOM.")
        else:
            res = st.session_state.ai_results
            st.success(f"✅ Optimization Complete! (Cost Score: {res['score']:.1f})")
            
            bom_data = []
            comps = [("C1 (Shunt)", res["c1"], "CAPS", "pF"), ("L2 (Series)", res["l2"], "INDS", "nH"), ("C3 (Shunt)", res["c3"], "CAPS", "pF")]
            
            for pos, val, db_key, unit in comps:
                val_r = round(val, 2)
                info = CIS_DB[db_key].get(val_r)
                if info: bom_data.append({"Position": pos, "Value": f"{val_r} {unit}", "P/N": info["pn"], "Vendor": info["mfg"], "Description": info["desc"]})
                else: bom_data.append({"Position": pos, "Value": f"{val:.3f} {unit}", "P/N": "---", "Vendor": "---", "Description": "⚠️ NO STOCK - Req. NPI"})
            
            df_bom = pd.DataFrame(bom_data)
            st.dataframe(df_bom, use_container_width=True, hide_index=True)
            
            csv = df_bom.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 Download BOM (.CSV)", data=csv, file_name='filter_bom.csv', mime='text/csv')

    if st.session_state.ai_results is not None:
        res = st.session_state.ai_results
        m_tot = np.zeros((int(f_pts),2,2),dtype=complex); m_tot[:,0,0]=1; m_tot[:,1,1]=1
        z,_ = get_Z_raw("C", res["c1"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_tot = m_tot @ shunt_mat(1/(z+1e-18))
        z,_ = get_Z_raw("L", res["l2"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_tot = m_tot @ get_mat(z, 'series')
        z,_ = get_Z_raw("C", res["c3"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_tot = m_tot @ shunt_mat(1/(z+1e-18))


# === [Plotly] 互動式深海霓虹圖表渲染 ===
if m_tot is not None:
    s21 = 2.0/(m_tot[:,0,0] + m_tot[:,0,1]/50 + m_tot[:,1,0]*50 + m_tot[:,1,1])
    s11 = (m_tot[:,0,0] + m_tot[:,0,1]/50 - m_tot[:,1,0]*50 - m_tot[:,1,1]) / (m_tot[:,0,0] + m_tot[:,0,1]/50 + m_tot[:,1,0]*50 + m_tot[:,1,1])
    s21_db = 20*np.log10(np.abs(s21)+1e-15)
    s11_db = 20*np.log10(np.abs(s11)+1e-15)
    ph = np.unwrap(np.angle(s21)); gd = -1.0/(2*np.pi)*np.gradient(ph, freqs)*1e9

    st.markdown("---")
    st.subheader(f"📈 Simulation Response: {app_mode.split()[1]}")
    
    # 建立雙 Y 軸圖表
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # --- [風格優化] S21: 霓虹青, 加粗實線 ---
    fig.add_trace(
        go.Scatter(x=freqs/1e6, y=s21_db, name="S21 (Trans)",
                   line=dict(color=COLOR_S21_NEON, width=2.5),
                   hovertemplate="%{y:.2f} dB"),
        secondary_y=False,
    )
    
    # --- [風格優化] S11: 琥珀金, 精緻虛線 ---
    fig.add_trace(
        go.Scatter(x=freqs/1e6, y=s11_db, name="S11 (Refl)",
                   line=dict(color=COLOR_S11_AMBER, width=2.0, dash='5px, 3px'), 
                   hovertemplate="%{y:.2f} dB"),
        secondary_y=False,
    )
    
    # Group Delay 繪製
    if show_gd:
        fig.add_trace(
            go.Scatter(x=freqs/1e6, y=gd, name="Group Delay",
                       line=dict(color=COLOR_GD_LIME, width=1.5),
                       hovertemplate="%{y:.3f} ns",
                       opacity=0.7),
            secondary_y=True,
        )

    # --- [背景與排版優化] 深度海洋風格 ---
    fig.update_layout(
        paper_bgcolor=COLOR_PLOT_BG, # 外圍底色
        plot_bgcolor=COLOR_PLOT_BG,  # 繪圖區底色
        font=dict(color=COLOR_TEXT_NM, family="Segoe UI, Arial, sans-serif"),
        hovermode="x unified",       # 十字游標統一顯示
        hoverlabel=dict(
            bgcolor=COLOR_BG_CARD,   # 懸停標籤底色
            font_size=13,
            font_family="Consolas, monospace"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor='rgba(21, 34, 56, 0.8)', # 帶一點透明度的圖例背景
            bordercolor=COLOR_GRID,
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # --- 座標軸網格線與外框樣式 ---
    fig.update_xaxes(title_text="Frequency (MHz)", 
                     showgrid=True, gridcolor=COLOR_GRID, gridwidth=0.5, 
                     zeroline=False, 
                     showline=True, linecolor=COLOR_AXIS_LINE, linewidth=1)
                     
    fig.update_yaxes(title_text="Magnitude (dB)", color=COLOR_S21_NEON, 
                     showgrid=True, gridcolor=COLOR_GRID, gridwidth=0.5, 
                     zeroline=False, 
                     showline=True, linecolor=COLOR_AXIS_LINE, linewidth=1, 
                     secondary_y=False)
    
    if show_gd:
        fig.update_yaxes(title_text="Group Delay (ns)", color=COLOR_GD_LIME, 
                         showgrid=False, zeroline=False, 
                         secondary_y=True)

    # 渲染圖表
    st.plotly_chart(fig, use_container_width=True)

    # 產生 S2P 並提供下載
    s2p_str = "# Hz S RI R 50\n"
    for i in range(len(freqs)):
        s2p_str += f"{freqs[i]:.0f} {s11[i].real:.6f} {s11[i].imag:.6f} {s21[i].real:.6f} {s21[i].imag:.6f} {s21[i].real:.6f} {s21[i].imag:.6f} {s11[i].real:.6f} {s11[i].imag:.6f}\n"

    st.download_button(label="💾 Export S2P File", data=s2p_str, file_name="filter_sim.s2p", mime="text/plain")