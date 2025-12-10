import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Importar librerias
    """)
    return


@app.cell
def _():
    import quak
    import pandas as pd
    import marimo as mo
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    return mo, np, pd, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Crear y ajustar dataframe
    """)
    return


@app.cell
def _(pd):
    df = pd.read_excel(r'data\Hf.xlsx').rename(columns = {
        "176Hf/177Hf":"176Hf_177Hf",
        "176Lu/177Hf":"176Lu_177Hf",
        "176Hf/177Hf(t)": "176Hf_177Hf(t)",

    })

    df[["sampleid", "number"]] = df['Sample'].str.split('_', expand=True, n=1)

    return (df,)


@app.cell
def _(df):
    #Filtrar outliers
    q1, q3 = df["t(Ga)"].quantile([.05, .95])
    IRQ = q3 - q1
    print(q1, q3)

    df_good = df[
        mask := df["t(Ga)"].between(q1-IRQ, q3+IRQ)
    ]
    df_bad = df[-mask]

    print(f"Size original: {df.shape}")
    print(f"Size filtered: {df_good.shape}")
    print(f"Ratio: {df_good.shape[0]/df.shape[0]}")
    df_bad
    return (df_good,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Calcular $\epsilon$-Hafnium y propagar errores
    """)
    return


@app.cell
def _():
    # Valores constantes de Hf y Lu en Depleted Mantle y CHUR
    # Vervoort et al. 2018 values
    Hf_DM = 0.283225
    Lu_DM = 0.0383

    # Vervoort & Blichert-Toft 1999
    Hf_CHUR = 0.282772
    Lu_CHUR = 0.0332

    lam_Lu = 1.867e-5 # My-1

    Lu_crust = 0.015
    return Hf_CHUR, Hf_DM, Lu_CHUR, Lu_DM, Lu_crust, lam_Lu


@app.cell
def _(Hf_CHUR, Lu_CHUR, df, df_good, lam_Lu, np):
    # calcular eHfi 

    # Columns of interest
    t = df_good["t(Ga)"] 
    Lu176_Hf177 = df_good["176Lu_177Hf"] 
    Hf176_Hf177 = df_good["176Hf_177Hf"]

    # Calculation of eHf
    decaimiento = np.exp( lam_Lu * t ) - 1
    _numerador = Hf176_Hf177 - Lu176_Hf177*decaimiento
    _denominador = Hf_CHUR - Lu_CHUR*decaimiento
    _ehf = 10_000 * ((_numerador/_denominador)-1)
@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Filtrar outliers y datos eHf con errores altos
    """)
    return


    df_with_ehf=df.assign(ehf=_ehf)

    df_with_ehf

    return Hf176_Hf177, decaimiento, df_with_ehf

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Figura $\epsilon$-Hafnium vs Edad (Ma)
    """)
    return


@app.cell
def _(df_with_ehf, px):
    colores = { # Color scheme for different samples
      "060065":"red",
      "060067":"green",
      "060072":"blue",
      "070242":"black",
      "300351":"yellow",
      "300339":"purple",
      "300334":"pink",
    }
    linea_recta_x = (0.03, .08)
    linea_recta_y = (-10, 10)

    fig = px.scatter(
        df_with_ehf,
        x="t(Ga)",
        y="ehf",
        color ="sampleid",
        color_discrete_map=colores)

    fig.add_scatter(name="referencia", x=linea_recta_x, y=linea_recta_y)
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Other Thing
    """)
    return


@app.cell
def _(Hf176_Hf177, Hf_DM, Lu_DM, Lu_crust, decaimiento, lam_Lu, np):
    _numerador = Hf176_Hf177 + Lu_crust * decaimiento - Hf_DM
    _denominador = Lu_crust - Lu_DM

    #print(_numerador/_denominador)

    tdm2 = (1 / lam_Lu) * np.log(_numerador/_denominador + 1)
    tdm2

    return


if __name__ == "__main__":
    app.run()
