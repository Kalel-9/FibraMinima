"""Estilo de apresentação, separado dos algoritmos de grafos."""

import streamlit as st


def apply_style() -> None:
    st.markdown("""
    <style>
    .block-container {max-width: 1560px; padding-top: 1.5rem; padding-bottom: 2rem;}
    [data-testid="stAppViewContainer"] {background: #f5f7fa;}
    [data-testid="stSidebar"] {background: #edf2f6; border-right: 1px solid #dce4eb;}
    h1,h2,h3 {color: #102b3f; letter-spacing: -.035em;}
    h3 {font-size: 1.25rem !important;}
    .stButton>button, .stFormSubmitButton>button {min-height: 2.8rem; border-radius: 10px;
        font-weight: 600; font-size: 1rem;}
    .stButton>button:focus {outline: 2px solid #0d9488; outline-offset: 2px;}
    [data-testid="stMetric"] {background: white; border: 1px solid #dce4eb;
        border-radius: 12px; padding: .85rem 1rem;}
    [data-testid="stMetricValue"] {font-size: 1.9rem; color: #102b3f;}
    [data-testid="stMetricLabel"] {color: #526777;}
    [data-testid="stVerticalBlockBorderWrapper"] {border-radius: 14px;}
    .hero {background: #102b3f; color: white; border-radius: 18px; padding: 1.7rem 2rem;
        border-left: 6px solid #2dd4bf; margin-bottom: .8rem;}
    .eyebrow {color: #8de4d7; font-size: .78rem; letter-spacing: .15em; font-weight: 700;}
    .hero h1 {color: white; font-size: 2rem; margin: .35rem 0; padding: 0;}
    .hero p {color: #d1dfe9; margin: .4rem 0 0; font-size: 1.03rem;}
    .step {font-size: .78rem; color: #526777; text-transform: uppercase;
        letter-spacing: .08em; font-weight: 700; margin-bottom: .3rem;}
    .preset-title {font-size: 1.1rem; color: #102b3f; font-weight: 700;}
    .preset-price {font-size: 1.65rem; color: #102b3f; font-weight: 700; margin: .15rem 0;}
    .preset-detail {font-size: .9rem; color: #526777; min-height: 2.6rem;}
    .pill {display: inline-block; background: #e0f5ef; color: #086859; padding: .2rem .6rem;
        border-radius: 20px; font-size: .78rem; font-weight: 600; margin-bottom: .5rem;}
    .network-status {border-radius: 10px; padding: .85rem 1rem; margin: .2rem 0 .5rem;
        font-size: 1rem; background: #e3f5ed; color: #16634e; border: 1px solid #abd8c5;}
    .network-status.down {background: #fff2e3; color: #8b430b; border-color: #edc897;}
    .route {border-left: 3px solid #2563eb; background: #edf4ff; color: #193e75;
        border-radius: 0 8px 8px 0; padding: .7rem .9rem; line-height: 1.7;}
    .route.off {border-color: #b45309; background: #fff4e7; color: #8b430b;}
    .legend {display: flex; flex-wrap: wrap; gap: .6rem 1.2rem; color: #425d70;
        font-size: .83rem; padding: .35rem 0 .6rem;}
    .legend span {display: inline-flex; align-items: center; gap: .45rem;}
    .legend i {width: 24px; height: 4px; display: inline-block; border-radius: 4px;}
    .legend .broken {height: 0; border-top: 3px dashed #dc2626;}
    .legend .dot {height: 10px; width: 10px; background: #b45309; border-radius: 50%;}
    @media (max-width: 800px) {
        .block-container {padding: 1rem;}
        .hero {padding: 1.1rem;}
        .hero h1 {font-size: 1.6rem;}
    }
    </style>
    """, unsafe_allow_html=True)


def apply_building_style() -> None:
    """Mantém os ajustes compactos da tela principal junto dos demais estilos."""
    apply_style()
    st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1600px;}
h2 {font-size: 1.6rem !important; padding-top: 0 !important;}
[data-testid="stMetric"] {padding: .5rem .85rem;}
[data-testid="stMetricValue"] {font-size: 1.65rem;}
.st-key-building_controls [data-testid="stVerticalBlock"],
.st-key-custom_building_controls [data-testid="stVerticalBlock"] {gap: .6rem;}
</style>
""", unsafe_allow_html=True)


def hero() -> None:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">ALGORITMOS EM GRAFOS · PLANEJAMENTO DE REDES</div>
      <h1>FibraMínima</h1>
      <p>Quanto custa uma rede que continua conectada quando um cabo rompe?</p>
    </div>
    """, unsafe_allow_html=True)


def legend() -> None:
    st.markdown("""
    <div class="legend">
      <span><i style="background:#0d9488"></i>Cabo instalado</span>
      <span><i style="background:#2563eb"></i>Caminho em uso</span>
      <span><i class="broken"></i>Cabo rompido</span>
      <span><i class="dot"></i>Ponto sem acesso</span>
      <span><i style="background:#cbd5e1"></i>Não instalado</span>
    </div>
    """, unsafe_allow_html=True)
