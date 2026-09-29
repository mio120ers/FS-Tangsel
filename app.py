import streamlit as st
import pandas as pd
import io, re

st.set_page_config(page_title="Smart Search Homepass & Splitter ID — FS Tangsel", page_icon="🔎", layout="wide")

st.markdown("""
<style>
h1.title{color:#2b6cb0;font-weight:800;margin-bottom:0}
.kpi{background:#f4f6fa;border-radius:12px;padding:18px 22px;box-shadow:0 2px 6px rgba(0,0,0,.08)}
.kpi .l{font-size:.75rem;font-weight:700;letter-spacing:.05em;color:#556}
.kpi .v{font-size:1.9rem;font-weight:800;color:#111}
</style>""", unsafe_allow_html=True)

@st.cache_data
def load():
    d = pd.read_parquet("data.parquet")
    d["_s"] = (d["homepass_id"]+" "+d["splitter_id"]+" "+d["Area Name"]+" "+d["nama_jalan_"]+" "+
               d["no_rumah_gedung"]+" "+d["resident_name"]+" "+d["pop_id"]+" "+d["kelurahan"]+" "+
               d["kecamatan"]+" "+d["project_name"]).str.lower().str.replace(r"[.,\-/]", " ", regex=True)
    return d
df = load()

st.markdown('<h1 class="title">🔎 Smart Search Homepass & Splitter ID — FS Tangerang Selatan</h1>', unsafe_allow_html=True)
st.caption("Ketik pencarian bebas secara lengkap (Contoh: Nama Jalan + Blok + No. Rumah, ID Homepass, ID Splitter, Area Name, dll.)")

if "q" not in st.session_state: st.session_state.q = ""
if "qi" not in st.session_state: st.session_state.qi = ""
def setq(v): st.session_state.q = v; st.session_state.qi = v
def reset():
    st.session_state.q = ""; st.session_state.qi = ""
    st.session_state.jalan = ""; st.session_state.nomor = ""

c1, c2 = st.columns([6,1], vertical_alignment="bottom")
c1.text_input("🔍 Kolom Pencarian Cepat (Smart Search):", key="qi",
    placeholder="Contoh: jl aria putra 8 / Golden Park / 15226H / TNG-05...",
    help="Semua kata harus cocok (urutan bebas), huruf besar/kecil tidak berpengaruh.")
if c2.button("🔍 Cari", type="primary", width="stretch"): st.session_state.q = st.session_state.qi

st.write("**Contoh Pencarian Cepat:**")
ex = st.columns([2,2,2,2,1,2], vertical_alignment="center")
examples = ["Aria Putra 8", "Golden Park", "TNG-05", "15226H"]
for col, e in zip(ex, examples): col.button("💡 "+e, on_click=setq, args=(e,), width="stretch")
ex[5].button("🔄 Reset / Hapus", on_click=reset, width="stretch")
st.divider()

f = df
q = st.session_state.q.strip().lower()
if q:
    for tok in re.sub(r"[.,\-/]", " ", q).split():
        f = f[f["_s"].str.contains(re.escape(tok), na=False)]

with st.expander("📌 Filter Spesifik Nama Jalan/Blok & Nomor Rumah (Opsional)"):
    a, b, c, d_ = st.columns(4)
    jalan = a.text_input("Nama Jalan / Blok", key="jalan")
    nomor = b.text_input("Nomor Rumah / Gedung", key="nomor")
    distrik = c.multiselect("Distrik", sorted(df["Distrik"].unique()))
    hub = d_.multiselect("HUB", sorted(df["HUB"].unique()))
if jalan: f = f[f["nama_jalan_"].str.contains(re.escape(jalan), case=False, na=False)]
if nomor: f = f[f["no_rumah_gedung"].str.fullmatch(re.escape(nomor.strip()), case=False, na=False)]
if distrik: f = f[f["Distrik"].isin(distrik)]
if hub: f = f[f["HUB"].isin(hub)]

def kpi(col, label, val): col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{val:,}</div></div>', unsafe_allow_html=True)
k = st.columns(4)
kpi(k[0], "TOTAL HOMEPASS DITEMUKAN", int(f["Total"].sum()))
kpi(k[1], "JUMLAH SPLITTER ID", f.loc[f["splitter_id"]!="","splitter_id"].nunique())
kpi(k[2], "AREA TERCOVER", f["Area Name"].nunique())
kpi(k[3], "JUMLAH DISTRIK", f["Distrik"].nunique())

st.header("📋 Hasil Pencarian Detail")
full = st.checkbox("Tampilkan seluruh kolom detail Excel")
show = f.drop(columns=["_s"])
if not full:
    show = show[["homepass_id","splitter_id","Area Name","nama_jalan_","no_rumah_gedung","resident_name",
                 "Distrik","HUB","NODE","pop_id","rfs_status","kelurahan","kecamatan","homepassed_koordinat","splitter_koordinat"]]
LIMIT = 100
if len(f) > LIMIT:
    st.info(f"⚠️ Menampilkan {LIMIT} data pertama dari total {len(f):,} data. Ketik pencarian yang lebih spesifik untuk mempersempit hasil.")
st.dataframe(show.head(LIMIT), hide_index=True, width="stretch")

if len(f):
    buf = io.BytesIO(); show.to_excel(buf, index=False)
    st.download_button("⬇️ Unduh hasil (Excel)", buf.getvalue(), "hasil_pencarian.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
