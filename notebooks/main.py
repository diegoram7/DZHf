import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _():
    #Valores constantes de Hf y Lu en Depleted Mantle y CHUR
    # Vervoort et al. 2018 values
    Hf_DM = 0.283225
    Lu_DM = 0.0383

    # Vervoort & Blichert-Toft 1999
    Hf_CHUR = 0.282772
    Lu_CHUR = 0.0332

    lam_Lu = 1.867e-5 # My-1
    return


@app.cell
def _(pd):
    df=pd.read_excel(r'data\Hf.xlsx') 
    df
    return (df,)


@app.cell
def _(df):
    #Filtrar outliers
    q1edad, q3edad = df["t(Ga)"].quantile([.05, .95])
    IRQedad = q3edad - q1edad
    print(q1edad, q3edad)

    q1eps, q3eps = df["e(t)"].quantile([.05, .95])
    print(q1eps, q3eps)
    IRQeps = q3eps - q1eps

    df_filtrado = df[
        df["t(Ga)"].between(q1edad-IRQedad, q3edad+IRQedad) & df["e(t)"].between(q1eps-IRQeps, q3eps+IRQeps)
    ]
    print(df.shape)
    print(df_filtrado.shape)
    print(df_filtrado.shape[0]/df.shape[0])
    df_filtrado
    return


@app.cell
def _(pd):
    df2=pd.read_excel(r'data\eHf_by_sample.xlsx')
    return (df2,)


@app.cell
def _(df2):
    df2
    return


if __name__ == "__main__":
    app.run()
