import streamlit as st
from graphviz import Digraph


def matrix_chain_order_with_steps(p):
    n = len(p) - 1
    m = [[0] * n for _ in range(n)]
    s = [["-"] * n for _ in range(n)]
    steps = []

    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            m[i][j] = float('inf')
            step_explanation = f"Memproses subrantai A{i+1} sampai A{j+1} (panjang {l})\n"
            for k in range(i, j):
                q = m[i][k] + m[k+1][j] + p[i] * p[k+1] * p[j+1]
                step_explanation += (
                    f"  ➤ Coba split di A{k+1}: "
                    f"m[{i+1},{k+1}] + m[{k+2},{j+1}] + {p[i]}×{p[k+1]}×{p[j+1]} = "
                    f"{m[i][k]} + {m[k+1][j]} + {p[i]*p[k+1]*p[j+1]} = {q}\n"
                )
                if q < m[i][j]:
                    m[i][j] = q
                    s[i][j] = k + 1
                    step_explanation += f"    ✅ Minimum baru ditemukan: {q} dengan split di A{k+1}\n"

            steps.append({
                'm': [row[:] for row in m],
                's': [row[:] for row in s],
                'description': step_explanation
            })

    return m, s, steps


def get_optimal_parenthesization(s, i, j):
    if i == j:
        return f"A{i+1}"
    else:
        k = s[i][j] - 1
        left = get_optimal_parenthesization(s, i, k)
        right = get_optimal_parenthesization(s, k+1, j)
        return f"({left} × {right})"

def print_tree(s, i, j, indent=""):
    if i == j:
        return indent + f"A{i+1}\n"
    k = s[i][j] - 1
    tree = indent + f"Split A{i+1}..A{j+1} at A{k+1}\n"
    tree += print_tree(s, i, k, indent + "  ")
    tree += print_tree(s, k + 1, j, indent + "  ")
    return tree
    
def draw_tree(s, i, j, dot, parent=None):
    if i == j:
        label = f"A{i+1}"
    else:
        k = s[i][j] - 1
        label = f"({i+1}..{j+1})\\nSplit at A{k+1}"

    node_id = f"{i}_{j}"
    dot.node(node_id, label)

    if parent:
        dot.edge(parent, node_id)

    if i != j:
        k = s[i][j] - 1
        draw_tree(s, i, k, dot, node_id)
        draw_tree(s, k+1, j, dot, node_id)

def show_tree(s, n):
    dot = Digraph()
    dot.attr(rankdir='TB')  # Top to Bottom
    draw_tree(s, 0, n - 1, dot)
    st.graphviz_chart(dot.source)


st.set_page_config(page_title="Matrix Chain Multiplication", layout="centered")

st.title("📐 Matrix Chain Multiplication Visualizer")

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Visualisasi Langkah", "✅ Hasil Akhir"])

with tab1:
    st.header("🔰 Deskripsi")
    st.markdown("""
    Algoritma Matrix Chain Multiplication digunakan untuk menentukan **urutan perkalian matriks** yang **paling efisien** agar biaya total minimum.  
    Menggunakan pendekatan **Dynamic Programming**, algoritma ini mengisi dua matriks:
    - `m[i][j]`: minimum cost untuk mengalikan dari matriks Ai hingga Aj
    - `s[i][j]`: indeks pemisah optimal

    ---
    """)

    st.header("🧮 Input Dimensi Matriks")

    n_matrix = st.number_input("Jumlah Matriks", min_value=2, max_value=10, value=4, step=1)

    p = []
    for i in range(n_matrix):
        row = st.number_input(f"Baris Matriks A{i+1}", min_value=1, key=f"row_{i}")
        if i == 0:
            p.append(row)
        col = st.number_input(f"Kolom Matriks A{i+1}", min_value=1, key=f"col_{i}")
        p.append(col)

    if st.button("🔍 Hitung"):
        m, s, steps = matrix_chain_order_with_steps(p)
        st.session_state.p = p
        st.session_state.m = m
        st.session_state.s = s
        st.session_state.steps = steps
        st.session_state.step_idx = 0

with tab2:
    if 'steps' in st.session_state and st.session_state.steps:
        st.header("📊 Visualisasi Langkah per Langkah")

        step = st.session_state.steps[st.session_state.step_idx]
        st.write(f"### Langkah {st.session_state.step_idx + 1} dari {len(st.session_state.steps)}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📘 Matriks M")
            st.table(step["m"])
        with col2:
            st.subheader("📗 Matriks S")
            st.table(step["s"])

        st.text_area("📝 Penjelasan Langkah", value=step["description"], height=250)

        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("⬅️ Sebelumnya") and st.session_state.step_idx > 0:
                st.session_state.step_idx -= 1
        with col_next:
            if st.button("➡️ Selanjutnya") and st.session_state.step_idx < len(st.session_state.steps) - 1:
                st.session_state.step_idx += 1
    else:
        st.info("Masukkan input terlebih dahulu di tab 'Home' dan klik 'Hitung'.")

with tab3:
    if 'm' in st.session_state and 's' in st.session_state:
        st.header("✅ Kesimpulan")

        n = len(st.session_state.p) - 1
        st.subheader("🔢 Matriks Akhir M dan S")
        col1, col2 = st.columns(2)
        with col1:
            st.write("📘 Matriks M")
            st.table(st.session_state.m)
        with col2:
            st.write("📗 Matriks S")
            st.table(st.session_state.s)

        st.subheader("🧠 Optimal Parenthesization")
        optimal = get_optimal_parenthesization(st.session_state.s, 0, n - 1)
        st.success(f"Hasil Urutan Optimal: {optimal}")

        st.subheader("🌳 Visualisasi Parenthesization Tree")
        show_tree(st.session_state.s, n)
    else:
        st.info("Silakan isi input dan jalankan perhitungan terlebih dahulu.")

# Tambahkan ini setelah st.set_page_config
st.markdown("""
    <style>
    /* Pastel gradient background */
    .stApp {
        background: linear-gradient(to right top, #fceaff, #e0f7fa, #ffe5ec);
        background-attachment: fixed;
    }
            
    /* Tambahkan dark overlay semi-transparent */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(0, 0, 0, 0.10);  /* transparansi gelap */
        z-index: 0;
    }
            
    /* Semua konten di atas overlay */
    .block-container {
        position: relative;
        z-index: 1;
    }

    /* Optional: rounder cards and softer box shadows */
    .stMarkdown, .stTable, .stTextArea, .stNumberInput, .stButton {
        border-radius: 12px !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
        background-color: rgba(255, 255, 255, 0.25) !important;
        padding: 8px;
    }

    /* Customize header and subheader */
    h1, h2, h3 {
        color: #5c5470;
    }

    /* Button style */
    button[kind="primary"] {
        background-color: #ffd1dc !important;
        color: black !important;
    }

    button[kind="secondary"] {
        background-color: #d5f4e6 !important;
        color: black !important;
    }

    .stTabs [role="tablist"] > div {
        background-color: #fbeaff;
        border-radius: 10px;
        padding: 4px 8px;
        margin-right: 4px;
        color: #5c5470;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffecf0 !important;
        font-weight: bold;
        color: #5c5470 !important;
    }
    </style>
""", unsafe_allow_html=True)