
# analista_esportivo_app.py
# Kivy interface wrapper for "Analista Esportivo" — Português (PT-BR)
# Single-file application that uses local football.json-master data and optional online APIs.
# Place this file and the folder "football.json-master" in the same directory on the device.
# Requirements: kivy, requests, pandas

import os, json, threading, logging, math, requests
from datetime import datetime
from functools import partial

# UI imports
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty

# Data libs
try:
    import pandas as pd
except Exception as e:
    pd = None

# -------------------- Config --------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DEFAULT_DATA_BASE_PATH = "football.json-master"  # relative path; place folder next to this file
FOOTBALL_NEWS_API = "https://football-news-api.onrender.com/news"
CRSET_API_BASE = "https://crset.vercel.app/api/standings"
FOOTBALL_API_MATCHES = "https://football-api-production.up.railway.app/api/v1/matches"
N_RECENT_MATCHES = 10

# -------------------- Kivy KV --------------------
KV = '''#:import utils kivy.utils

<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: 12
        spacing: 8

        BoxLayout:
            size_hint_y: None
            height: "64dp"
            spacing: 8

            Label:
                text: "🏟️ ANALISTA ESPORTIVO"
                bold: True
                font_size: "20sp"
                halign: "left"
                valign: "middle"
            Button:
                text: "Sair"
                size_hint_x: None
                width: "80dp"
                on_release: app.stop()

        GridLayout:
            cols: 2
            size_hint_y: None
            height: "160dp"
            spacing: 8

            Button:
                text: "⚽ Analisar Time"
                on_release: root.go_analisar_time()
            Button:
                text: "⚔️ Confronto Direto"
                on_release: root.go_confronto()

            Button:
                text: "📰 Notícias"
                on_release: root.go_noticias()
            Button:
                text: "📊 Classificação"
                on_release: root.go_classificacao()

        BoxLayout:
            size_hint_y: None
            height: "42dp"
            spacing: 8
            TextInput:
                id: path_input
                hint_text: "Caminho para 'football.json-master' (Enter para usar padrão)"
                multiline: False
            Button:
                text: "Salvar caminho"
                size_hint_x: None
                width: "120dp"
                on_release: root.set_data_path(path_input.text)

        BoxLayout:
            size_hint_y: None
            height: "36dp"
            padding: 4
            Label:
                id: status_label
                text: root.status_text
                color: (0,0,0,1)

        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: output_area
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "28dp"
                row_force_default: False
'''

# -------------------- Backend: load and analyze --------------------

def carregar_dados_json_historicos(base_path):
    """Carrega arquivos JSON do formato football.json-master e retorna lista de partidas (dicionários)."""
    all_matches = []
    if not base_path:
        base_path = DEFAULT_DATA_BASE_PATH

    if not os.path.exists(base_path):
        logging.warning(f"Caminho de dados não encontrado: {base_path}")
        return []

    # The expected structure is base_path/<season>/*.json with matches list inside each file
    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if os.path.isdir(year_path):
            for fname in os.listdir(year_path):
                if fname.endswith(".json"):
                    fpath = os.path.join(year_path, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            obj = json.load(f)
                            matches = obj.get("matches") or []
                            league_name = obj.get("name", fname.replace(".json",""))
                            for m in matches:
                                # normalize scores
                                score = m.get("score") or {}
                                ft = score.get("ft") if isinstance(score, dict) else None
                                home_goals = None
                                away_goals = None
                                if ft and isinstance(ft, list) and len(ft) >= 2:
                                    try:
                                        home_goals = int(ft[0])
                                        away_goals = int(ft[1])
                                    except:
                                        home_goals = None
                                all_matches.append({
                                    "Season": year_folder,
                                    "League": league_name,
                                    "Date": m.get("date"),
                                    "Time": m.get("time"),
                                    "HomeTeam": m.get("team1"),
                                    "AwayTeam": m.get("team2"),
                                    "HomeGoals": home_goals,
                                    "AwayGoals": away_goals,
                                    "Raw": m
                                })
                    except Exception as e:
                        logging.error(f"Erro ao ler {fpath}: {e}")
                        continue
    logging.info(f"Carregados {len(all_matches)} jogos (local)." )
    return all_matches

def calcular_estatisticas_por_time(matches, nome_time):
    """Retorna estatísticas básicas (total, vitorias, empates, derrotas, gols marcados/sofridos)"""
    nome_low = nome_time.lower()
    total = v = e = d = gm = gs = 0
    for m in matches:
        ht = (m.get("HomeTeam") or "").lower()
        at = (m.get("AwayTeam") or "").lower()
        hg = m.get("HomeGoals")
        ag = m.get("AwayGoals")
        if nome_low in ht or nome_low in at:
            # considerar somente partidas com placar numérico
            if hg is None or ag is None:
                continue
            total += 1
            if nome_low in ht:
                gm += hg
                gs += ag
                if hg > ag: v += 1
                elif hg == ag: e += 1
                else: d += 1
            else:
                gm += ag
                gs += hg
                if ag > hg: v += 1
                elif ag == hg: e += 1
                else: d += 1
    if total == 0:
        return None
    return {
        "total": total, "vitorias": v, "empates": e, "derrotas": d,
        "gols_marcados": gm, "gols_sofridos": gs,
        "aprox_vitoria": round((v/total)*100,2), "media_gols_marcados": round(gm/total,2)
    }

def analisar_confronto_h2h(matches, time1, time2):
    """Retorna lista de confrontos diretos com placares válidos."""
    time1_low = time1.lower(); time2_low = time2.lower()
    h2h = []
    for m in matches:
        ht = (m.get("HomeTeam") or "").lower()
        at = (m.get("AwayTeam") or "").lower()
        if (time1_low in ht and time2_low in at) or (time1_low in at and time2_low in ht):
            if m.get("HomeGoals") is None or m.get("AwayGoals") is None:
                continue
            h2h.append(m)
    return h2h

def buscar_noticias(query=None, limit=5, timeout=8):
    params = {}
    if query:
        params["q"] = query
    try:
        resp = requests.get(FOOTBALL_NEWS_API, params=params, timeout=timeout)
        resp.raise_for_status()
        j = resp.json()
        return j.get("articles", [])[:limit]
    except Exception as e:
        logging.info(f"News API erro: {e}")
        return []

def buscar_classificacao(league="PL", season="2023", timeout=8):
    url = f"{CRSET_API_BASE}/{league}/{season}"
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        j = resp.json()
        return j.get("standings", [])
    except Exception as e:
        logging.info(f"CRSET API erro: {e}")
        return []

def buscar_partidas(league_id=39, season=2023, limit=10, timeout=8):
    params = {"league": league_id, "season": season, "limit": limit}
    try:
        resp = requests.get(FOOTBALL_API_MATCHES, params=params, timeout=timeout)
        resp.raise_for_status()
        j = resp.json()
        return j.get("matches", [])
    except Exception as e:
        logging.info(f"Football API erro: {e}")
        return []

# -------------------- Kivy Screen --------------------

class MainScreen(Screen):
    status_text = StringProperty("Caminho de dados: (padrão)")
    data_path = StringProperty(DEFAULT_DATA_BASE_PATH)
    loading = BooleanProperty(False)

    def on_pre_enter(self):
        self.ids.status_label.text = f"Caminho de dados: {self.data_path}"

    def set_data_path(self, text):
        text = text.strip()
        if text == "":
            self.data_path = DEFAULT_DATA_BASE_PATH
        else:
            self.data_path = text
        self.ids.status_label.text = f"Caminho de dados: {self.data_path}"
        self.print_to_output(f"✅ Caminho atualizado para: {self.data_path}")

    def clear_output(self):
        container = self.ids.output_area
        container.clear_widgets()

    def print_to_output(self, text):
        from kivy.uix.label import Label
        container = self.ids.output_area
        lbl = Label(text=str(text), size_hint_y=None, height="28dp", halign="left", valign="middle", text_size=(self.width-40, None))
        container.add_widget(lbl)

    # Navegações / ações
    def go_analisar_time(self):
        self.clear_output()
        self.print_to_output("🔎 Digite o nome do time no campo inferior e pressione Enter no teclado.")
        from kivy.uix.textinput import TextInput
        ti = TextInput(size_hint_y=None, height="40dp", multiline=False)
        ti.bind(on_text_validate=lambda inst: self._on_submit_time(inst.text))
        self.ids.output_area.add_widget(ti)
        ti.focus = True

    def _on_submit_time(self, texto):
        nome = texto.strip()
        if not nome:
            self.print_to_output("❗ Nome vazio.")
            return
        self.print_to_output(f"⏳ Analisando {nome} (local + online)...")
        threading.Thread(target=self._task_analisar_time, args=(nome,), daemon=True).start()

    def _task_analisar_time(self, nome_time):
        # Carrega dados locais
        matches = carregar_dados_json_historicos(self.data_path)
        stats = calcular_estatisticas_por_time(matches, nome_time)
        noticias = buscar_noticias(query=nome_time, limit=2)
        Clock.schedule_once(partial(self._show_result_time, nome_time, stats, noticias))

    def _show_result_time(self, nome_time, stats, noticias, dt):
        if not stats:
            self.print_to_output(f"⚠️ Nenhum registro local encontrado para '{nome_time}'. Ainda assim buscarei notícias e partidas recentes.")
        else:
            self.print_to_output(f"📊 Estatísticas locais para {nome_time}:")
            self.print_to_output(f" - Jogos analisados: {stats['total']}")
            self.print_to_output(f" - Vitórias: {stats['vitorias']} | Empates: {stats['empates']} | Derrotas: {stats['derrotas']}")
            self.print_to_output(f" - Gols marcados: {stats['gols_marcados']} | Gols sofridos: {stats['gols_sofridos']}")
            self.print_to_output(f" - Prob. vitória (local): {stats['aprox_vitoria']}%") 
            self.print_to_output(f" - Média gols por jogo (marcados): {stats['media_gols_marcados']}")

        if noticias:
            self.print_to_output("📰 Notícias recentes:")
            for art in noticias:
                title = art.get("title") or art.get("headline") or "—"
                src = art.get("source") or art.get("sourceName") or ""
                published = art.get("publishedAt") or art.get("published")
                url = art.get("url") or ""
                self.print_to_output(f" • {title} [{src}] {published or ''}")
                if url:
                    self.print_to_output(f"   Link: {url}")
        else:
            self.print_to_output("ℹ️ Nenhuma notícia retornada pela API no momento.")

    def go_confronto(self):
        self.clear_output()
        self.print_to_output("🔎 Confronto Direto — digite 'Time1 vs Time2' (ex: Flamengo vs Santos)")
        from kivy.uix.textinput import TextInput
        ti = TextInput(size_hint_y=None, height="40dp", multiline=False)
        ti.bind(on_text_validate=lambda inst: self._on_submit_confronto(inst.text))
        self.ids.output_area.add_widget(ti)
        ti.focus = True

    def _on_submit_confronto(self, texto):
        txt = texto.strip()
        if "vs" not in txt and "x" not in txt:
            self.print_to_output("Formato inválido. Use 'Time1 vs Time2' ou 'Time1 x Time2'.")
            return
        if "vs" in txt:
            parts = txt.split("vs")
        else:
            parts = txt.split("x")
        time1 = parts[0].strip(); time2 = parts[1].strip()
        self.print_to_output(f"⏳ Buscando histórico H2H para {time1} x {time2} ...")
        threading.Thread(target=self._task_confronto, args=(time1, time2), daemon=True).start()

    def _task_confronto(self, t1, t2):
        matches = carregar_dados_json_historicos(self.data_path)
        h2h = analisar_confronto_h2h(matches, t1, t2)
        noticias_t1 = buscar_noticias(query=t1, limit=1)
        noticias_t2 = buscar_noticias(query=t2, limit=1)
        Clock.schedule_once(partial(self._show_result_confronto, t1, t2, h2h, noticias_t1, noticias_t2))

    def _show_result_confronto(self, t1, t2, h2h, n1, n2, dt):
        if not h2h:
            self.print_to_output(f"ℹ️ Não há jogos H2H com placares registrados entre {t1} e {t2} no seu acervo local.")
        else:
            self.print_to_output(f"📚 Histórico Direto ({len(h2h)} jogos):")
            wins_t1 = wins_t2 = draws = 0
            g_t1 = g_t2 = 0
            for m in h2h:
                hg = m.get("HomeGoals"); ag = m.get("AwayGoals")
                ht = m.get("HomeTeam"); at = m.get("AwayTeam")
                if t1.lower() in ht.lower() and t2.lower() in at.lower():
                    g_t1 += hg; g_t2 += ag
                    if hg > ag: wins_t1 += 1
                    elif hg < ag: wins_t2 += 1
                    else: draws += 1
                else:
                    g_t1 += ag; g_t2 += hg
                    if ag > hg: wins_t1 += 1
                    elif ag < hg: wins_t2 += 1
                    else: draws += 1
            self.print_to_output(f" - {t1} vitórias: {wins_t1} | {t2} vitórias: {wins_t2} | Empates: {draws}")
            self.print_to_output(f" - Gols (H2H): {t1} {g_t1} x {g_t2} {t2}")

        if n1:
            self.print_to_output(f"📰 {t1} - {n1[0].get('title','-')}")
        if n2:
            self.print_to_output(f"📰 {t2} - {n2[0].get('title','-')}")

    def go_noticias(self):
        self.clear_output()
        self.print_to_output("📰 Digite termo (ex: Neymar, Flamengo) e pressione Enter.")
        from kivy.uix.textinput import TextInput
        ti = TextInput(size_hint_y=None, height="40dp", multiline=False)
        ti.bind(on_text_validate=lambda inst: self._on_submit_news(inst.text))
        self.ids.output_area.add_widget(ti)
        ti.focus = True

    def _on_submit_news(self, term):
        term = term.strip()
        if not term:
            self.print_to_output("❗ Termo vazio.")
            return
        self.print_to_output(f"⏳ Buscando notícias por '{term}' ...")
        threading.Thread(target=self._task_news, args=(term,), daemon=True).start()

    def _task_news(self, term):
        articles = buscar_noticias(query=term, limit=6)
        Clock.schedule_once(partial(self._show_news, term, articles))

    def _show_news(self, term, articles, dt):
        if not articles:
            self.print_to_output("ℹ️ Nenhuma notícia encontrada no momento.")
            return
        self.print_to_output(f"📰 Notícias sobre {term}:")
        for a in articles:
            t = a.get("title") or "-"
            src = a.get("source") or "-"
            date = a.get("publishedAt") or a.get("published") or ""
            url = a.get("url") or ""
            self.print_to_output(f" • {t} [{src}] {date}")
            if url:
                self.print_to_output(f"   Link: {url}")

    def go_classificacao(self):
        self.clear_output()
        self.print_to_output("📊 Digite liga e temporada no formato 'PL 2023' (ou apenas Enter para PL 2023).")
        from kivy.uix.textinput import TextInput
        ti = TextInput(size_hint_y=None, height="40dp", multiline=False)
        ti.bind(on_text_validate=lambda inst: self._on_submit_table(inst.text))
        self.ids.output_area.add_widget(ti)
        ti.focus = True

    def _on_submit_table(self, txt):
        txt = txt.strip()
        if not txt:
            liga, temporada = "PL", "2023"
        else:
            parts = txt.split()
            liga = parts[0].upper()
            temporada = parts[1] if len(parts) > 1 else "2023"
        self.print_to_output(f"⏳ Buscando classificação {liga} {temporada} ...")
        threading.Thread(target=self._task_classificacao, args=(liga, temporada), daemon=True).start()

    def _task_classificacao(self, liga, temporada):
        standings = buscar_classificacao(league=liga, season=temporada)
        Clock.schedule_once(partial(self._show_classificacao, liga, temporada, standings))

    def _show_classificacao(self, liga, temporada, standings, dt):
        if not standings:
            self.print_to_output("ℹ️ Classificação não disponível para essa liga/temporada.")
            return
        self.print_to_output(f"🏆 Classificação {liga} {temporada}:")
        for t in standings[:20]:
            pos = t.get("position"); team = t.get("team"); pts = t.get("points")
            self.print_to_output(f" {pos}. {team} — {pts} pts")


# Screen manager
sm = ScreenManager(transition=NoTransition())
sm.add_widget(MainScreen(name="main"))

class AnaliseFutebolApp(App):
    def build(self):
        self.title = "Analista Esportivo"
        root = Builder.load_string(KV)
        return sm

if __name__ == "__main__":
    AnaliseFutebolApp().run()
