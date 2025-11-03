from kivy.app import App
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.utils import get_color_from_hex
import json
import os
import sys

# *******************************************************************
# URL PÚBLICA DE DADOS ESTÁTICOS: Mude o final para a liga/ano desejado (ex: /2024/br.1.json).
API_DADOS_URL = 'https://cdn.jsdelivr.net/gh/openfootball/football.json@master/2024-25/nl.1.json' 
# *******************************************************************

# Código KV do layout (Dark Mode)
kv_code = """
BoxLayout:
    orientation: 'vertical'
    padding: '10dp'
    spacing: '10dp'
    
    # Título
    Label:
        text: 'Analista Esportivo Pro'
        size_hint_y: 0.1
        font_size: '24sp'
        color: get_color_from_hex('#1E90FF')

    # Container de Status/Botão
    BoxLayout:
        size_hint_y: 0.1
        spacing: '10dp'
        
        Label:
            id: status_label
            text: 'Aguardando dados...'
            size_hint_x: 0.6
            color: get_color_from_hex('#FFFFFF')
        
        Button:
            text: 'Atualizar'
            size_hint_x: 0.4
            background_normal: ''
            background_color: get_color_from_hex('#00FF7F')
            color: 0, 0, 0, 1
            on_release: app.buscar_dados()

    # Lista de Jogos (RecycleView)
    RecycleView:
        id: lista_jogos
        viewclass: 'JogoItem'
        data: []
        scroll_type: ['bars', 'content']
        scroll_wheel_distance: 20
        bar_width: 10
        
        RecycleBoxLayout:
            default_size: None, dp(60)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(5)

<JogoItem@BoxLayout>:
    # Item da lista
    horario: ''
    times: ''
    canal: '' # Este dado não está no JSON, será um placeholder
    campeonato: ''
    
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(60)
    padding: dp(10)
    canvas.before:
        Color:
            rgba: get_color_from_hex('#363636')
        Rectangle:
            size: self.size
            pos: self.pos
    
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.6
        
        Label:
            text: root.times
            font_size: '16sp'
            halign: 'left'
            valign: 'top'
            text_size: self.size
            color: get_color_from_hex('#FFFFFF')
        
        Label:
            text: root.campeonato
            font_size: '12sp'
            halign: 'left'
            valign: 'bottom'
            text_size: self.size
            color: get_color_from_hex('#AAAAAA')
            
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.4
        
        Label:
            text: root.horario
            font_size: '14sp'
            color: get_color_from_hex('#00FF7F')
        
        Label:
            text: root.canal
            font_size: '12sp'
            color: get_color_from_hex('#1E90FF')
"""


class MainApp(App):
    def build(self):
        # Carrega o layout e configura o fundo escuro global
        self.root = Builder.load_string(kv_code)
        self.root.canvas.before.add(
            self.root.canvas.before.get_context().get('Color', get_color_from_hex('#121212'))
        )
        self.root.canvas.before.add(
            self.root.canvas.before.get_context().get('Rectangle', (self.root.pos, self.root.size))
        )
        return self.root

    def on_start(self):
        # Inicia a busca de dados assim que o app começa
        self.buscar_dados()

    def buscar_dados(self, *args):
        """Função para buscar dados assincronamente do arquivo JSON estático."""
        self.root.ids.status_label.text = 'Buscando dados...'
        
        # Faz a requisição HTTP para o arquivo JSON público.
        UrlRequest(
            API_DADOS_URL,
            on_success=self.parse_api_response,
            on_failure=self.on_error,
            on_error=self.on_error,
            on_progress=lambda req, cur, total: self.root.ids.status_label.text == f'Baixando: {cur}/{total} bytes'
        )

    def on_error(self, req, error):
        """Lida com falhas de rede ou HTTP."""
        error_msg = f'Erro de conexão ao buscar dados.'
        print(f"Erro ao buscar dados: {error}")
        self.root.ids.status_label.text = error_msg

    def parse_api_response(self, req, result):
        """
        Lida com a resposta JSON, que é um dicionário com uma chave 'matches'.
        """
        try:
            dados = result 
            
            # O arquivo JSON tem a estrutura {'name': '...', 'matches': [...] }
            jogos = dados.get('matches', [])

            dados_limpos = []
            campeonato_nome = dados.get('name', 'Dados da Liga')

            for item in jogos:
                # Combina os nomes dos times
                times_str = f"{item.get('team1', {}).get('name', 'N/A')} x {item.get('team2', {}).get('name', 'N/A')}"
                
                # Combina data e hora
                horario_str = f"{item.get('date', '')} {item.get('time', 'N/A')}"
                
                # O JSON não tem a coluna 'canal', então colocamos um placeholder informativo.
                canal_str = "Sem Info de TV" 
                
                dados_limpos.append({
                    'horario': horario_str,
                    'times': times_str,
                    'canal': canal_str,
                    'campeonato': campeonato_nome,
                })
            
            self.root.ids.lista_jogos.data = dados_limpos
            self.root.ids.status_label.text = f'{len(dados_limpos)} jogos carregados ({campeonato_nome}).'

        except Exception as e:
            error_msg = f"Erro ao processar dados JSON: {e}"
            print(error_msg)
            self.root.ids.status_label.text = error_msg


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    MainApp().run()
