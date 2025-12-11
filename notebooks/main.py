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
    from pathlib import Path

    import pandas as pd
    import marimo as mo
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go

    DATA_DIR = Path("data/")
    return DATA_DIR, go, mo, np, pd, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Crear y ajustar dataframe
    """)
    return


@app.cell
def _(DATA_DIR, pd):
    #Crear dataframe 
    df = pd.read_excel(DATA_DIR / 'Hf.xlsx').rename(columns = {
        "176Hf/177Hf":"176Hf_177Hf",
        "176Lu/177Hf":"176Lu_177Hf",
        "176Hf/177Hf(t)": "176Hf_177Hf(t)",

    })

    #Ajuste de nombre de columna Sample para cálculos y gráficos
    df[["sampleid", "number"]] = df['Sample'].str.split('_', expand=True, n=1) 

    #Conversión de unidades de Ga a Ma
    df["t(Ma)"] = df["t(Ga)"]*1000

    #Agregar columna de tipo de roca de la muestra

    df
    return (df,)


@app.cell
def _(df):
    df["sampleid"].unique()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Calcular $\epsilon$-Hafnium y propagar errores
    """)
    return


@app.cell
def _():
    # Valores constantes de Hf y Lu en Depleted Mantle y CHUR
    # Vervoort et al. 2018
    Hf_DM = 0.283225
    Lu_DM = 0.0383

    # Vervoort & Blichert-Toft 1999
    Hf_CHUR = 0.282772
    Lu_CHUR = 0.0332

    lam_Lu = 1.867e-5 # My-1

    Lu_crust = 0.015
    return Hf_CHUR, Hf_DM, Lu_CHUR, Lu_DM, Lu_crust, lam_Lu


@app.cell
def _(Hf_CHUR, Lu_CHUR, df, lam_Lu, np):
    # calcular eHfi y propagar errores 

    # Columnas de interés
    t = df["t(Ga)"] 
    Lu176_Hf177 = df["176Lu_177Hf"] 
    Hf176_Hf177 = df["176Hf_177Hf"]

    # Calcular eHf
    decaimiento = np.exp( lam_Lu * t ) - 1
    _numerador = Hf176_Hf177 - Lu176_Hf177*decaimiento
    _denominador = Hf_CHUR - Lu_CHUR*decaimiento
    df["ehf"] = 10_000 * ((_numerador/_denominador)-1)

    #Calcular CHUR_t a determinada edad
    CHUR_t = Hf_CHUR - Lu_CHUR * decaimiento

    #Calcular 2s para los valores de eHf
    two_sigma = 2*(pow(10, 4) * (df["1 s error.1"] / CHUR_t))
    df["2s"] = two_sigma

    df
    return Hf176_Hf177, decaimiento


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Filtrar outliers y datos eHf con errores altos
    """)
    return


@app.cell
def _(df):
    #Calcular cuatiles q1 y q3 de las edades
    q1, q3 = df["t(Ga)"].quantile([.05, .95])
    IRQ = q3 - q1
    print(q1, q3)

    #Separar los datos outliers y errores muy altos
    df_good = df[
        mask := (
            df["t(Ga)"].between(q1 - IRQ, q3 + IRQ)
            & (df["2s"] < 2.5)
        )
    ]
    df_bad = df[-mask] #Lista de outliers

    print(f"Size original: {df.shape}")
    print(f"Size filtered: {df_good.shape}")
    print(f"Ratio: {df_good.shape[0]/df.shape[0]}")

    #Datos filtrados
    df_bad
    return (df_good,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Calcular pendiente de línea DM para el grupo de muestras analizado
    """)
    return


@app.cell
def _(df_good):
    x_min = df_good['t(Ma)'].min()
    x_max = df_good['t(Ma)'].max()


    def chur_y(x):
        return 0

    chur_xs = (x_min, x_max)
    chur_ys = (chur_y(x_min), chur_y(x_max))

    def dm_y(x):
        y = -0.004 * (x) + 18
        return y

    dm_xs = (x_min, x_max)
    dm_ys = (dm_y(x_min), dm_y(x_max))
    
    return chur_xs, chur_ys, dm_xs, dm_ys


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Figura $\epsilon$-Hafnium vs Edad (Ma)
    """)
    return


@app.cell
def _(chur_xs, chur_ys, df_good, dm_xs, dm_ys, go, px):
    #Coordenadas de la línea de DM
    linea_DM_x = (0, 4500)
    linea_DM_y = (18, 0)

    #Coordenadas de la línea de CHUR
    linea_CHUR_x = (0, 4500)
    linea_CHUR_y = (0, 0)

    #Parámetros de la figura
    fig = px.scatter(
        df_good,
        x="t(Ma)",
        y="ehf",
        color ="sampleid",
        error_y="2s",
        marginal_x="rug",
        marginal_y="box",
        title="eHf vs Age (Ma)")

    fig.add_trace(
         go.Scatter(
             x=dm_xs,
             y=dm_ys,
             name="DM",
             line=dict(color="Crimson"))
    )
    fig.add_scatter(name="CHUR", x=chur_xs, y=chur_ys)

    fig.add_annotation(
        text="Depleted Mantle",
        x=dm_xs[0]+3,
        y=dm_ys[0]+1,
        showarrow=False
    )

    fig.add_annotation(
        text="Chondritic uniform reservoir",
        x=chur_xs[0]+5,
        y=chur_ys[0]-1,
        showarrow=False
    )

    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Two‑stage crustal model age (Para circones antiguos)
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
