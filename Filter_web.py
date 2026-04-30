import streamlit as st
import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# === 頁面基礎設定 ===
st.set_page_config(page_title="RF Filter Designer Pro", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# === 🎨 色票定義 (深海霓虹主題 Deep Sea Neon) ===
COLOR_BG_MAIN    = "#0b162d"   
COLOR_BG_CARD    = "#152238"   
COLOR_ACCENT     = "#D4AF37"   
COLOR_TEXT_NM    = "#E0E0E0"   
COLOR_PLOT_BG    = "#0A122A"   
COLOR_GRID       = "#3A4B66"   
COLOR_S21_NEON   = "#00FFC8"   
COLOR_S11_AMBER  = "#FF9F1C"   
COLOR_GD_LIME    = "#32CD32"   
COLOR_AXIS_LINE  = "#6c7a9c"   

st.markdown("""
    <style>
    .st-emotion-cache-1y4p8pa { padding-top: 2rem; }
    .srf-text { color: #32CD32; font-family: 'Consolas', monospace; font-weight: bold; }
    .srf-bypass { color: #888888; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

# === CIS Database (庫存模擬 - 完整展開版) ===
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

# === 動態擴充微型元件庫 (0.1 ~ 0.9) ===
def expand_database(db):
    cap_vendors = ["Murata", "TDK", "Samsung", "Yageo"]
    ind_vendors = ["Murata", "TDK", "Coilcraft", "Sunlord"]
    
    vals_to_add = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]
    for v in vals_to_add:
        if v not in db["CAPS"]:
            db["CAPS"][v] = {
                "pn": f"101-{int(v*100):05d}-00", 
                "mfg": random.choice(cap_vendors), 
                "desc": f"CAP CER {v}PF 50V C0G 0402"
            }
        if v not in db["INDS"]:
            db["INDS"][v] = {
                "pn": f"102-{int(v*100):05d}-00", 
                "mfg": random.choice(ind_vendors), 
                "desc": f"IND {v}NH 300MA 0402 LQP"
            }

expand_database(CIS_DB)

CAP_VENDORS = ["Any"] + sorted(list(set([v["mfg"] for v in CIS_DB["CAPS"].values()])))
IND_VENDORS = ["Any"] + sorted(list(set([v["mfg"] for v in CIS_DB["INDS"].values()])))

# === 狀態初始化 (Session State) ===
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
        "in_match": {"type": "Inductor (L)", "val": 0.0}, "s1": {"type": "Inductor (L)", "val": 0.8},
        "s2": {"type": "Inductor (L)", "val": 0.8}, "leg_a": {"type": "Inductor (L)", "val": 12.0},
        "leg_b": {"type": "Capacitor (C)", "val": 3.4}, "out_match": {"type": "Inductor (L)", "val": 0.0}
    }

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = None

# === 數學與拓樸工具 ===
def get_Z_raw(t, v, fs, use_para, ql, cp_pf, qc, esl_nh):
    v_si = v * (1e-12 if t=="C" else 1e-9)
    w = 2*np.pi*fs
    if not use_para: 
        return (1j*w*v_si if t=="L" else 1/(1j*w*v_si+1e-18)), t
    if t=="L": 
        z_ideal, rs, cp_si = 1j*w*v_si, (w*v_si)/(ql+1e-9), cp_pf * 1e-12
        return 1/((1/(z_ideal+rs)) + 1j*w*cp_si + 1e-18), t
    else: 
        z_ideal, resr, esl_si = 1/(1j*w*v_si+1e-18), 1/(w*v_si*qc+1e-9), esl_nh * 1e-9
        return z_ideal + resr + 1j*w*esl_si, t

def get_mat(z, p):
    m = np.zeros((len(z),2,2),dtype=complex); m[:,0,0]=m[:,1,1]=1
    if p=='series': m[:,0,1]=z
    else: m[:,1,0]=1/(z+1e-18)
    return m

def shunt_mat(y):
    m = np.zeros((len(y),2,2),dtype=complex); m[:,0,0]=m[:,1,1]=1; m[:,1,0]=y
    return m

def calc_srf(val, ctype, L_Cp, C_ESL):
    if val == 0: return "<span class='srf-bypass'>-- Bypass --</span>"
    try:
        if "L" in ctype: srf = 1/(2*np.pi*np.sqrt(val*1e-9*L_Cp*1e-12))
        else: srf = 1/(2*np.pi*np.sqrt(val*1e-12*C_ESL*1e-9))
        return f"<span class='srf-text'>{srf/1e9:.2f} GHz" if srf>1e9 else f"{srf/1e6:.0f} MHz</span>"
    except: return "<span class='srf-bypass'>--</span>"

def create_topology_fig(ladder_data, L_Cp_val, C_ESL_val):
    fig_topo = go.Figure()
    x_cursor, nodes_x, nodes_y = 1, [0], [1]
    
    for i, stg in enumerate(ladder_data):
        if stg["val"] == 0: continue 
        is_cap = "Capacitor" in stg["type"]
        unit, comp_label = "pF" if is_cap else "nH", f"{'C' if is_cap else 'L'}{i+1}"
        
        try:
            if not is_cap: srf = 1/(2*np.pi*np.sqrt(stg["val"]*1e-9*L_Cp_val*1e-12))
            else: srf = 1/(2*np.pi*np.sqrt(stg["val"]*1e-12*C_ESL_val*1e-9))
            srf_str = f"{srf/1e9:.2f} GHz" if srf>1e9 else f"{srf/1e6:.0f} MHz"
        except: srf_str = "--"

        hover_html = f"<b>Stage {i+1} ({stg['topo']})</b><br>Component: {stg['type']}<br>Value: {stg['val']} {unit}<br><b>SRF: <span style='color:#32CD32'>{srf_str}</span></b>"

        if "Series" in stg["topo"]:
            fig_topo.add_trace(go.Scatter(x=[x_cursor], y=[1], mode='markers+text', marker=dict(symbol='square', size=35, color=COLOR_BG_CARD, line=dict(color=COLOR_S21_NEON, width=2)), text=f"<b>{comp_label}</b>", textfont=dict(color=COLOR_TEXT_NM, size=12), hovertemplate=hover_html + "<extra></extra>", showlegend=False))
            nodes_x.extend([x_cursor - 0.18, None, x_cursor + 0.18]); nodes_y.extend([1, None, 1]); x_cursor += 1.5
        elif "Shunt" in stg["topo"]:
            fig_topo.add_trace(go.Scatter(x=[x_cursor, x_cursor], y=[1, 0], mode='lines', line=dict(color=COLOR_TEXT_NM, width=2), hoverinfo='skip', showlegend=False))
            fig_topo.add_trace(go.Scatter(x=[x_cursor], y=[0.5], mode='markers+text', marker=dict(symbol='square', size=35, color=COLOR_BG_CARD, line=dict(color=COLOR_S11_AMBER, width=2)), text=f"<b>{comp_label}</b>", textfont=dict(color=COLOR_TEXT_NM, size=12), hovertemplate=hover_html + "<extra></extra>", showlegend=False))
            fig_topo.add_trace(go.Scatter(x=[x_cursor-0.2, x_cursor+0.2, None, x_cursor-0.1, x_cursor+0.1, None, x_cursor-0.05, x_cursor+0.05], y=[0, 0, None, -0.1, -0.1, None, -0.2, -0.2], mode='lines', line=dict(color=COLOR_TEXT_NM, width=2), hoverinfo='skip', showlegend=False))
            nodes_x.append(x_cursor); nodes_y.append(1); x_cursor += 1.5

    nodes_x.append(x_cursor); nodes_y.append(1)
    fig_topo.add_trace(go.Scatter(x=nodes_x, y=nodes_y, mode='lines', line=dict(color=COLOR_TEXT_NM, width=2), hoverinfo='skip', showlegend=False))
    fig_topo.add_annotation(x=0, y=1.2, text="<b>IN</b>", showarrow=False, font=dict(color=COLOR_ACCENT, size=12))
    fig_topo.add_annotation(x=x_cursor, y=1.2, text="<b>OUT</b>", showarrow=False, font=dict(color=COLOR_ACCENT, size=12))

    fig_topo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-0.5, x_cursor + 0.5]), yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[-0.4, 1.5]))
    return fig_topo

# === 側邊欄 ===
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

freqs = np.linspace(f_start*1e6, f_stop*1e6, int(f_pts))
m_tot = None 

# ---------------------------------------------------------
# Mode 1: Custom Ladder
# ---------------------------------------------------------
if app_mode == "🪜 Custom Ladder":
    st.header("🪜 Custom 6-Stage Ladder Network")
    h_cols = st.columns([1, 2, 2, 2, 2])
    for col, text in zip(h_cols, ["Stage", "Topology", "Component", "Value", "SRF (Resonance)"]): col.markdown(f"**{text}**")
        
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
            m_tot = m_tot @ (shunt_mat(1/(z+1e-18)) if "Shunt" in stg["topo"] else get_mat(z, 'series'))

    st.markdown("---")
    st.subheader("🧠 Interactive Topology Architecture")
    fig_topo_main = create_topology_fig(st.session_state.ladder, L_Cp, C_ESL)
    fig_topo_main.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_topo_main, use_container_width=True)

# ---------------------------------------------------------
# Mode 2: T-Notch Filter
# ---------------------------------------------------------
elif app_mode == "🎛️ T-Notch Filter":
    st.header("🎛️ T-Notch Filter Configuration")
    
    # 省略了 T-notch 細節以集中火力在 AI 模式
    st.info("T-Notch filter rendering available in main branch.")

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
                        
                        st.session_state.ai_results = {"c1": best_vals[0], "l2": best_vals[1], "c3": best_vals[2], "score": best_score}
                        st.session_state.ladder[0] = {"topo": "Shunt (||)", "type": "Capacitor (C)", "val": best_vals[0]}
                        st.session_state.ladder[1] = {"topo": "Series (—)", "type": "Inductor (L)", "val": best_vals[1]}
                        st.session_state.ladder[2] = {"topo": "Shunt (||)", "type": "Capacitor (C)", "val": best_vals[2]}
                        for i in range(3,6): st.session_state.ladder[i]["val"] = 0.0

    with col_bom:
        if st.session_state.ai_results is None:
            st.info("👈 Run AI Optimization to generate BOM & Topology.")
        else:
            res = st.session_state.ai_results
            st.success(f"✅ Optimization Complete! (Cost Score: {res['score']:.1f})")
            
            bom_data = []
            comps = [("C1 (Shunt)", res["c1"], "CAPS", "pF"), ("L2 (Series)", res["l2"], "INDS", "nH"), ("C3 (Shunt)", res["c3"], "CAPS", "pF")]
            
            for pos, val, db_key, unit in comps:
                val_r = round(val, 2)
                info = CIS_DB[db_key].get(val_r)
                if info: bom_data.append({"Position": pos, "Value": f"{val_r} {unit}", "P/N": info["pn"], "Vendor": info["mfg"], "Description": info["desc"]})
                else: bom_data.append({"Position": pos, "Value": f"{val:.3f} {unit}", "P/N": "---", "Vendor": "---", "Description": "⚠️ Req. NPI"})
            
            df_bom = pd.DataFrame(bom_data)
            st.dataframe(df_bom, use_container_width=True, hide_index=True)
            csv = df_bom.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 Download BOM (.CSV)", data=csv, file_name='filter_bom.csv', mime='text/csv')

            # --- Topology ---
            st.markdown("---")
            st.markdown("##### 🧠 Active Topology")
            fig_topo_ai = create_topology_fig(st.session_state.ladder[:3], L_Cp, C_ESL)
            fig_topo_ai.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_topo_ai, use_container_width=True)

            # --- Smith Chart (鏡像反轉 C3->L2->C1) ---
            st.markdown("---")
            st.markdown("##### 🎯 Smith Chart (S11 - Standard Aligned)")
            
            m_smith = np.zeros((int(f_pts),2,2),dtype=complex); m_smith[:,0,0]=1; m_smith[:,1,1]=1
            
            # 反轉組件順序以對齊 Load->Source 的工業標準視角
            z3, _ = get_Z_raw("C", res["c3"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_smith = m_smith @ shunt_mat(1/(z3+1e-18))
            zl, _ = get_Z_raw("L", res["l2"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_smith = m_smith @ get_mat(zl, 'series')
            z1, _ = get_Z_raw("C", res["c1"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_smith = m_smith @ shunt_mat(1/(z1+1e-18))
            
            s11_smith = (m_smith[:,0,0] + m_smith[:,0,1]/50 - m_smith[:,1,0]*50 - m_smith[:,1,1]) / (m_smith[:,0,0] + m_smith[:,0,1]/50 + m_smith[:,1,0]*50 + m_smith[:,1,1])
            gamma_mag = np.abs(s11_smith)
            vswr = (1 + gamma_mag) / (1 - gamma_mag + 1e-15)
            z_norm = (1 + s11_smith) / (1 - s11_smith + 1e-15)

            fig_smith = go.Figure(go.Scattersmith(
                real=z_norm.real, imag=z_norm.imag, line=dict(color=COLOR_S11_AMBER, width=2.5), 
                text=[f"Freq: {f/1e6:.1f} MHz<br>VSWR: {v:.2f}<br>|Γ|: {g:.2f}" for f, v, g in zip(freqs, vswr, gamma_mag)],
                hovertemplate="%{text}<extra></extra>"
            ))
            
            fig_smith.update_layout(
                smith=dict(realaxis_gridcolor=COLOR_GRID, imaginaryaxis_gridcolor=COLOR_GRID, bgcolor=COLOR_PLOT_BG),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=60, t=50, b=50), height=380 
            )
            st.plotly_chart(fig_smith, use_container_width=True)

    # 確保主圖表使用正常傳輸方向 (C1->L2->C3)
    if st.session_state.ai_results is not None:
        res = st.session_state.ai_results
        m_tot = np.zeros((int(f_pts),2,2),dtype=complex); m_tot[:,0,0]=1; m_tot[:,1,1]=1
        z1,_ = get_Z_raw("C", res["c1"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_tot = m_tot @ shunt_mat(1/(z1+1e-18))
        zl,_ = get_Z_raw("L", res["l2"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_tot = m_tot @ get_mat(zl, 'series')
        z3,_ = get_Z_raw("C", res["c3"], freqs, use_para, L_Q, L_Cp, C_Q, C_ESL); m_tot = m_tot @ shunt_mat(1/(z3+1e-18))

# === [Plotly] 頻率響應總圖 ===
if m_tot is not None:
    s21 = 2.0/(m_tot[:,0,0] + m_tot[:,0,1]/50 + m_tot[:,1,0]*50 + m_tot[:,1,1])
    s11 = (m_tot[:,0,0] + m_tot[:,0,1]/50 - m_tot[:,1,0]*50 - m_tot[:,1,1]) / (m_tot[:,0,0] + m_tot[:,0,1]/50 + m_tot[:,1,0]*50 + m_tot[:,1,1])
    s21_db = 20*np.log10(np.abs(s21)+1e-15)
    s11_db = 20*np.log10(np.abs(s11)+1e-15)
    ph = np.unwrap(np.angle(s21)); gd = -1.0/(2*np.pi)*np.gradient(ph, freqs)*1e9

    st.markdown("---")
    st.subheader(f"📈 Simulation Response: {app_mode.split()[1]}")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=freqs/1e6, y=s21_db, name="S21 (Trans)", line=dict(color=COLOR_S21_NEON, width=2.5), hovertemplate="%{y:.2f} dB"), secondary_y=False)
    fig.add_trace(go.Scatter(x=freqs/1e6, y=s11_db, name="S11 (Refl)", line=dict(color=COLOR_S11_AMBER, width=2.0, dash='5px, 3px'), hovertemplate="%{y:.2f} dB"), secondary_y=False)
    if show_gd: fig.add_trace(go.Scatter(x=freqs/1e6, y=gd, name="Group Delay", line=dict(color=COLOR_GD_LIME, width=1.5), hovertemplate="%{y:.3f} ns", opacity=0.7), secondary_y=True)

    fig.update_layout(
        paper_bgcolor=COLOR_PLOT_BG, plot_bgcolor=COLOR_PLOT_BG, font=dict(color=COLOR_TEXT_NM, family="Segoe UI, Arial, sans-serif"),
        hovermode="x unified", hoverlabel=dict(bgcolor=COLOR_BG_CARD, font_size=13, font_family="Consolas, monospace"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(21, 34, 56, 0.8)', bordercolor=COLOR_GRID, borderwidth=1, font=dict(size=11)),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    fig.update_xaxes(title_text="Frequency (MHz)", showgrid=True, gridcolor=COLOR_GRID, gridwidth=0.5, zeroline=False, showline=True, linecolor=COLOR_AXIS_LINE, linewidth=1)
    fig.update_yaxes(title_text="Magnitude (dB)", color=COLOR_S21_NEON, showgrid=True, gridcolor=COLOR_GRID, gridwidth=0.5, zeroline=False, showline=True, linecolor=COLOR_AXIS_LINE, linewidth=1, secondary_y=False)
    if show_gd: fig.update_yaxes(title_text="Group Delay (ns)", color=COLOR_GD_LIME, showgrid=False, zeroline=False, secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)