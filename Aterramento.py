#################################################################################################################
######################################  UNIVERSIDADE FEDERAL DE SERGIPE  ########################################
##########################   CLEITON SOUZA CUNHA E MATHEUS HENRIQUE VIEIRA DE ARAUJO   ##########################
import PySimpleGUI as sg
import math
import teste__
import matplotlib.pyplot as plt

valores_iniciais = {
    'd1_m1': 721, 'd1_m2': 720, 'd1_m3': 723, 'd1_m4': 722, 'd1_m5': 723,
    'd2_m1': 365, 'd2_m2': 361, 'd2_m3': 360, 'd2_m4': 360, 'd2_m5': 360,
    'd4_m1': 94, 'd4_m2': 93, 'd4_m3': 93, 'd4_m4': 94, 'd4_m5': 94,
    'd8_m1': 68, 'd8_m2': 69, 'd8_m3': 70, 'd8_m4': 71, 'd8_m5': 71,
    'd16_m1': 184, 'd16_m2': 186, 'd16_m3': 184, 'd16_m4': 182, 'd16_m5': 182
}

resistividades_geral = {}

########################################################################################################################################################################
def tela_inicial():
    global resistividades_geral

    sg.theme('DarkBlue')
    layout = [
        [sg.Image(filename='cabecalho.png')],
        [sg.Text('Preencha conforme sua base de dados', justification='center', font=('rubik', 15, 'bold'),expand_x=True, expand_y=True)],
        [sg.Text('', expand_x=True), sg.Button('Resistência', font=('rubik', 10,'bold')), sg.Button('Resistividade', font=('rubik', 10,'bold')), sg.Text('', expand_x=True)]
    ]


    window = sg.Window('WennerCalc', layout, finalize=True)

    while True:

        event, values = window.read()
        print(event, values)

        if event in (sg.WIN_CLOSED, None):
            break

        elif event == 'Resistência':
            resistividades_geral = tabela_resistencias()


        elif event == 'Resistividade':
            tabela_resistividade()   

    
    window.close()

def tabela_resistencias():
    
    #global resistividades_geral
    tip  = 'Obtenha os parâmetros do solo antes de Plotar Gráficos.'
    tip2 = 'Plotar Gráficos Liberado!'
    tip3 = 'Plotar Gráfico da resistividade do solo previamente.'

    def calcular_resistividade(distancia, valor_medio_resistencia):

        profundidade = 2#0.05*distancia
        resistividade = (4 * math.pi * distancia * valor_medio_resistencia) / \
                        (1 + (2 * distancia / math.sqrt(distancia ** 2 + 4 * profundidade ** 2) -
                            distancia / math.sqrt(distancia ** 2 + profundidade ** 2)))
        return resistividade
    
    def calcular_media_filtrada(valores):

        media_inicial = sum(valores) / len(valores)
        valores_filtrados = [v for v in valores if abs(v - media_inicial) / media_inicial <= 0.5]
        media_final = sum(valores_filtrados) / len(valores_filtrados) if valores_filtrados else media_inicial
        return media_final

    # Layout da janela com tabela editável
    header = ['Distância (m)', 'Medição 1', 'Medição 2', 'Medição 3', 'Medição 4', 'Medição 5']
    distancias = [1, 2, 4, 8, 16]

    layout = [
        [sg.Text('INSIRA OS VALORES DE RESISTÊNCIA PARA CADA DISTÂNCIA (Ω):', justification='center', font=('Helvetica', 14), expand_x=True)],
        [sg.Text(h, size=(10, 1), justification='center', expand_x=True) for h in header]
    ]
    
    for d in distancias:
        row = [sg.Text(f'{d}m', size=(8, 1), justification='center', expand_x=True)] + \
              [sg.Input(size=(10, 1), key=f'd{d}_m{i}', expand_x=True) for i in range(1, 6)]
        layout.append(row)

    layout.append([sg.Button('Calcular Resistividade', expand_x=True), sg.Button('Obter Parâmetros', expand_x=True), sg.Button('Plotar Gráficos', expand_x=True, disabled=True, button_color=("#FFCCCC"), tooltip=tip), sg.Button("Visualizar Curva de Resistividade", tooltip=tip3), sg.Button('Voltar', expand_x=True)])

    # Criar a janela
    window = sg.Window('Cálculo de Resistividade', layout, resizable=True, finalize=True)

    for row in layout:
        for element in row:
            element.expand(expand_x=True)

    ""
    # Preencher a tabela com os valores iniciais
    for key, value in valores_iniciais.items():
        window[key].update(value)
    ""

    resistividades_dict = {}

    while True:
        event, values = window.read()
        print(event)

        if event in (sg.WINDOW_CLOSED, 'Voltar'):
            break
        
        elif event == 'Calcular Resistividade':
            try:
                resistividades = []

                for distancia in distancias:
                    resistencias = [float(values[f'd{distancia}_m{i}']) for i in range(1, 6)]
                    if any(r <= 0 for r in resistencias):
                        sg.popup_error(f'Todas as resistências para a distância {distancia}m devem ser valores positivos.')
                        break

                    media_resistencia = calcular_media_filtrada(resistencias)
                    resistividade = calcular_resistividade(distancia, media_resistencia)
                    resistividades.append((distancia, resistividade))
                    resistividades_dict[distancia] = resistividade

                resultados = "\n".join([f"Distância {d}m: Resistividade = {r:.2f} Ω.m" for d, r in resistividades])
                sg.popup(f'Resistividade específica do terreno:\n\n{resultados}')

            except ValueError:
                sg.popup_error('Por favor, insira valores numéricos válidos.')

        elif event == 'Obter Parâmetros':
            
            window["Plotar Gráficos"].update(disabled=False, button_color=("black", "#CCFFCC")) # ativar botao
            window["Plotar Gráficos"].set_tooltip(tip2)

            resistividades = []
            try:
                resistividades = []

                for distancia in distancias:
                    resistencias = [float(values[f'd{distancia}_m{i}']) for i in range(1, 6)]
                    if any(r <= 0 for r in resistencias):
                        sg.popup_error(f'Todas as resistências para a distância {distancia}m devem ser valores positivos.')
                        break

                    media_resistencia = calcular_media_filtrada(resistencias)
                    resistividade = calcular_resistividade(distancia, media_resistencia)
                    resistividades.append((distancia, resistividade))
                    resistividades_dict[distancia] = resistividade

                resultados = "\n".join([f"Distância {d}m: Resistividade = {r:.2f} Ω.m" for d, r in resistividades])
                #sg.popup(f'Resistividade específica do terreno:\n\n{resultados}')

            except ValueError:
                sg.popup_error('Por favor, insira valores numéricos válidos.')

            teste__.codigo_formiga(resistividades_dict)
            parametros = teste__.ler_linha_25()
            print(parametros)

            linha = '-'
            texto = f'{50*linha}\nh = {parametros[0]} m\np1 = {parametros[1]} Ω.m\np2 = {parametros[2]} Ω.m\n{50*linha}'

            sg.popup(texto, title='Parâmetros', button_justification='center', font=('', 15, 'bold')) 
           
        elif event == 'Plotar Gráficos':

            window["Plotar Gráficos"].update(button_color=("#FFCCCC"), disabled=True) # desativar botao
            window["Plotar Gráficos"].set_tooltip(tip)

            a_medido, rho_medido, rho_modelo = teste__.ler_linhas_27_a_31()
            plotar_grafico(a_medido, rho_medido, rho_modelo)

        elif event == 'Visualizar Curva de Resistividade':
            try:
                resistividades = []

                for distancia in distancias:
                    resistencias = [float(values[f'd{distancia}_m{i}']) for i in range(1, 6)]
                    if any(r <= 0 for r in resistencias):
                        sg.popup_error(f'Todas as resistências para a distância {distancia}m devem ser valores positivos.')
                        break

                    media_resistencia = calcular_media_filtrada(resistencias)
                    resistividade = calcular_resistividade(distancia, media_resistencia)
                    resistividades.append((distancia, resistividade))
                    resistividades_dict[distancia] = resistividade

                resultados = "\n".join([f"Distância {d}m: Resistividade = {r:.2f} Ω.m" for d, r in resistividades])

            except ValueError:
                sg.popup_error('Por favor, insira valores numéricos válidos.')

                          
            
            resistividades__ = [float(value) for value in resistividades_dict.values()]

            a_medido, rho_medido, rho_modelo = teste__.ler_linhas_27_a_31()
            plotar_grafico2(a_medido, resistividades__)

            pass




    window.close()
    #print("Resistividades calculadas:", resistividades_dict)


    return resistividades_dict

def tabela_resistividade():

    tip  = 'Obtenha os parâmetros do solo antes de Plotar Gráficos.' 
    tip2 = 'Plotar Gráficos Liberado!'
    tip3 = 'Plotar Gráfico da resistividade do solo previamente.'

    layout = [
        [sg.Text('', expand_x=True), sg.Text("RESISTIVIDADE MÉDIA FINAL (Ω.m)", font=("Helvetica", 12, "bold"), justification="center"), sg.Text('', expand_x=True)],
        [sg.Text("ρ(1m):", size=(8, 1)), sg.Input(8739.55, key=1)],
        [sg.Text("ρ(2m):", size=(8, 1)), sg.Input(7645.74,key=2)],
        [sg.Text("ρ(4m):", size=(8, 1)), sg.Input(3095.73,key=4)],
        [sg.Text("ρ(8m):", size=(8, 1)), sg.Input(3858.26,key=8)],
        [sg.Text("ρ(16m):", size=(8, 1)), sg.Input(18950.12,key=16)],
        [sg.Push(), sg.Button("Obter Parâmetros"), sg.Button("Plotar Gráficos", disabled=True, button_color=("#FFCCCC"), tooltip=tip), sg.Button("Visualizar Curva de Resistividade", tooltip=tip3),sg.Button("Voltar"), sg.Push()]
    ]


    window  = sg.Window('Tabela de Resistividade', layout, resizable=False)

    while True:

        event, values = window.read()
        print(values)
        if event in (sg.WIN_CLOSED, None, 'Voltar'):
            break

        elif event =='Obter Parâmetros':

            window["Plotar Gráficos"].update(disabled=False, button_color=("black", "#CCFFCC")) # ativar botao
            window["Plotar Gráficos"].set_tooltip(tip2)

            #x = {1: 641.83, 2: 996.62, 4: 1437.62, 8: 1887.08, 16: 2091.32}
            #x = {1: 2393, 2: 2752, 4: 3418, 8: 4549, 16: 6333}
            #x = {1: 8739.547537642615, 2: 7645.742511273771, 4: 3095.7305886123195, 8: 3858.258925489078, 16: 18950.120802924477}
            #x = values # values é um dicionario que recebe dados de sg.input()
            #values = x

            for chave, valor in values.items():
                values[chave] = float(valor)

            teste__.codigo_formiga(values)
            parametros = teste__.ler_linha_25()
            print(parametros)

            linha = '-'
            texto = f'{50*linha}\nh = {parametros[0]} m\np1 = {parametros[1]} Ω.m\np2 = {parametros[2]} Ω.m\n{50*linha}'

            sg.popup(texto, title='Parâmetros', button_justification='center', font=('', 15, 'bold'))   

        elif event == 'Plotar Gráficos':
            
            window["Plotar Gráficos"].update(button_color=("#FFCCCC"), disabled=True) # desativar botao
            window["Plotar Gráficos"].set_tooltip(tip)

            a_medido, rho_medido, rho_modelo = teste__.ler_linhas_27_a_31()
            plotar_grafico(a_medido, rho_medido, rho_modelo)

        elif event == 'Visualizar Curva de Resistividade':

            resistividades__ = [float(value) for value in values.values()]
            a_medido, rho_medido, rho_modelo = teste__.ler_linhas_27_a_31()
            plotar_grafico2(a_medido, resistividades__)
            


    window.close()

    return None

def plotar_grafico(x, y_1, y_2):

    plt.title("Comparativo Medido VS. Modelo")
    plt.xlabel("Distancia 'a' ")
    plt.ylabel("Resistividade (rho)")
    plt.plot(x, y_1, label='Medido', color='blue', linewidth=1, marker='o')
    plt.plot(x, y_2, label='Modelo', color='red', linewidth=1, marker='o')
    #plt.plot(x, y_2)
    plt.grid(True, which='both', linestyle='--', color='gray', alpha=0.7, linewidth=0.8) 
    plt.legend()  
    plt.show()


    return None

def plotar_grafico2(x, y_1):

    plt.title("Resistividade Medida")
    plt.xlabel("Distancia 'a' ")
    plt.ylabel("Resistividade (rho)")
    plt.plot(x, y_1, label='Medido', color='blue', linewidth=1, marker='o')
    #plt.plot(x, y_2)
    plt.grid(True, which='both', linestyle='--', color='gray', alpha=0.7, linewidth=0.8) 
    plt.legend()  
    plt.show()


    return None
########################################################################################################################################################################
tela_inicial()

#print(resistividades_geral)
