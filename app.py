from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

def limpar(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

def formatar(nome):
    if isinstance(nome, str) and "-" in nome:
        n, uf = nome.split("-")
        return f"{n.title()} ({uf})"
    return nome

def carregar():
    art = limpar(pd.read_excel("br26.xlsx", sheet_name="ART"))
    cla = limpar(pd.read_excel("br26.xlsx", sheet_name="CLA"))
    est = limpar(pd.read_excel("br26.xlsx", sheet_name="EST"))
    cal = limpar(pd.read_excel("br26.xlsx", sheet_name="CAL"))

    cla["TIME"] = cla["TIME"].apply(formatar)
    art["CLUBE"] = art["CLUBE"].apply(formatar)
    cal["MANDANTE"] = cal["MANDANTE"].apply(formatar)
    cal["VISITANTE"] = cal["VISITANTE"].apply(formatar)

    return art, cla, est, cal

@app.route("/")
def home():
    art, cla, est, cal = carregar()

    gols = int((cal["GM"] + cal["GV"]).sum())
    jogos = len(cal)
    artilheiro = art.sort_values("GOLS", ascending=False).iloc[0]

    return render_template("index.html", gols=gols, jogos=jogos, art=artilheiro)

@app.route("/classificacao")
def classificacao():
    _, cla, _, _ = carregar()
    df = cla.sort_values(["PTS","V","SALDO","GOL"], ascending=False)
    return render_template("tabela.html", titulo="Classificação", dados=df.to_dict("records"))

@app.route("/artilheiros")
def artilheiros():
    art, _, _, _ = carregar()
    df = art.sort_values(["GOLS","JOGADOR"], ascending=[False,True])
    return render_template("lista.html", titulo="Artilheiros", dados=df.to_dict("records"))

@app.route("/estrangeiros")
def estrangeiros():
    art, _, est, _ = carregar()

    gringos = art[(art["PAIS"].notna()) & (art["PAIS"] != "") & (art["PAIS"] != "BRA")]
    gringos = gringos.sort_values(["GOLS"], ascending=False)

    est = est[(est["PAIS"].notna()) & (est["PAIS"] != "")]
    est = est.sort_values("GOLS", ascending=False)

    return render_template("estrangeiros.html",
                           gringos=gringos.to_dict("records"),
                           paises=est.to_dict("records"))

@app.route("/resultados")
def resultados():
    _, _, _, cal = carregar()
    cal["PLACAR"] = cal["GM"].astype(int).astype(str) + " x " + cal["GV"].astype(int).astype(str)
    return render_template("resultados.html", dados=cal.to_dict("records"))

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

if __name__ == "__main__":
    app.run()