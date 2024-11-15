import random
import math

import numpy
import plotly.graph_objects as go

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import os



def codigo_formiga(dados__: dict):

    #Criação do diretório de saída, caso não exista

    output_dir = './dados/solo_2_camadas/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = os.path.join(output_dir, 'tese_wesley_caso_14_30072024.txt')
    fig_comparativo_filename = os.path.join(output_dir, 'tese_wesley_caso_14_30072024_fig_comparativo.html')
    fig_erro_filename = os.path.join(output_dir, 'tese_wesley_caso_14_30072024_fig_erro.html')



    # ================
    # Funções de Apoio
    # ================


    def converte_bits_em_int(lista):
        ret = 0
        for pot, i in enumerate(lista):
            ret += i * 2**pot
        return ret


    def decodifica_1var(valor, nbits, minimo, maximo):
        '''
        Observe que "maximo" é representado.
        '''
        fator = valor / (2**nbits-1)
        return minimo + fator * (maximo - minimo)


    def decodifica_ind(individual):

        aux = converte_bits_em_int(list(individual[0:nbits_h]))
        h = decodifica_1var(aux, nbits_h, min_h, max_h)

        aux = converte_bits_em_int(list(individual[nbits_h:nbits_h+nbits_k]))
        k = decodifica_1var(aux, nbits_k, min_k, max_k)

        aux = converte_bits_em_int(list(individual[nbits_h+nbits_k:nbits_h+nbits_k+nbits_rho]))
        rho = decodifica_1var(aux, nbits_rho, min_rho, max_rho)

        return h, k, rho


    def calcula_rhos_do_modelo(h, k, rho):

        ret = {}
        for medido_a, _ in dados.items():
            soma = 0
            for n in range(1,11):
                soma += k**n/math.sqrt(1 + (2*n*h/medido_a)**2) - \
                        k**n/math.sqrt(4 + (2*n*h/medido_a)**2)
            ret[medido_a] = rho*(1 + 4*soma)

        return ret


    def eval_fitness(individual):

        h, k, rho = decodifica_ind(individual)
        dados_modelo = calcula_rhos_do_modelo(h, k, rho)

        fit = 0
        for key in dados.keys():
            rho_medido = dados[key]
            rho_modelo = dados_modelo[key]
            fit += (rho_medido - rho_modelo)**2

        return fit,


    def cxTwoPointCopy(ind1, ind2):
        """Execute a two points crossover with copy on the input individuals. The
        copy is required because the slicing in numpy returns a view of the data,
        which leads to a self overwriting in the swap operation. It prevents
        ::

            >>> import numpy
            >>> a = numpy.array((1,2,3,4))
            >>> b = numpy.array((5,6,7,8))
            >>> a[1:3], b[1:3] = b[1:3], a[1:3]
            >>> print(a)
            [1 6 7 4]
            >>> print(b)
            [5 6 7 8]
        """

        size = len(ind1)
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size - 1)
        if cxpoint2 >= cxpoint1:
            cxpoint2 += 1
        else: # Swap the two cx points
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
            = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()

        return ind1, ind2


    def eaSimpleWithElitism(
            population, 
            toolbox, 
            cxpb, 
            mutpb, 
            ngen, 
            stats=None,
            halloffame=None, 
            verbose=__debug__,
    ):
        """This algorithm is similar to DEAP eaSimple() algorithm, with the modification that
        halloffame is used to implement an elitism mechanism. The individuals contained in the
        halloffame are directly injected into the next generation and are not subject to the
        genetic operators of selection, crossover and mutation.
        """
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is None:
            raise ValueError("halloffame parameter must not be empty!")

        halloffame.update(population)
        hof_size = len(halloffame.items) if halloffame.items else 0

        record = stats.compile(population) if stats else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)
        if verbose:
            #print(logbook.stream)
            pass

        # Begin the generational process
        for gen in range(1, ngen + 1):

            # Select the next generation individuals
            offspring = toolbox.select(population, len(population) - hof_size)

            # Vary the pool of individuals
            offspring = algorithms.varAnd(offspring, toolbox, cxpb, mutpb)

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # add the best back to population:
            offspring.extend(halloffame.items)

            # Update the hall of fame with the generated individuals
            halloffame.update(offspring)

            # Replace the current population by the offspring
            population[:] = offspring

            # Append the current generation statistics to the logbook
            record = stats.compile(population) if stats else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:
                #print(logbook.stream)
                pass

        return population, logbook


    def plotar_comparativo_med_mod(dados_med, dados_mod):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=list(dados_med.keys()), 
                y=list(dados_med.values()), 
                mode='lines+markers', 
                name='Medidos',
            )
        )
        fig.add_trace(
            go.Scatter(
                x=list(dados_mod.keys()), 
                y=list(dados_mod.values()), 
                mode='lines+markers', 
                name='Modelo',
            )
        )
        fig.update_layout(
            title='Comparativo: Medidos vs Modelo',
            xaxis_title='Distância "a"',
            yaxis_title='Resistividade (rho)',
        )
        return fig


    def plotar_erros_perc_med_mod(dados_erro):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=list(dados_erro.keys()), 
                y=list(dados_erro.values()), 
                mode='lines+markers', 
                name='Erros: Modelo vs Medidos, em %',
            )
        )
        annotations = []
        for key, value in dados_erro.items():
            annotations.append(
                dict(
                    x=key, 
                    y=value,
                    xanchor='left', 
                    yanchor='top',
                    text=f'{value:.4f}',
                    showarrow=False
                )
            )
        fig.update_layout(
            title='Erro Percentual: Medidos vs Modelo',
            xaxis_title='Distância "a"',
            yaxis_title='Erro (%)',
            showlegend=True, 
            annotations=annotations,
        )
        return fig



    # ================
    # Dados de Entrada
    # ================

    #dados = {1: 4554.967062193557, 2: 4558.75340222863, 4: 2362.6761818859345, 8: 3523.8204593085097, 16: 18537.920811720414}

    ## Caso do Kindermann
    dados = dados__

    ## Caso do trabalho de campo. Insira aqui os dados de entrada par 1, 2, 4, 8 e 16 metros
    #dados = {1: 641.83, 2: 996.62, 4: 1437.62, 8: 1887.08, 16: 2091.32}

    ## Caso da tese Wesley UFU
    #dados = {1: 641.83, 2: 996.62, 4: 1437.62, 8: 1887.08, 16: 2091.32}

    ## Caso da Tese da Univ Fed de Uberlândia
    #dados = {0.5: 2393, 1: 2752, 2: 3418, 4: 4549, 8: 6333, 16: 8444, 32: 10455}

    ## Estudo de caso da tese de José Ricardo (Univ. do Porto)
    #dados = {1: 680, 2: 610, 4: 420, 8: 240, 16: 190, 32: 180}

    ## Caso 24/07/2024
    #dados = {0.5: 3094, 1: 3713, 2: 4360, 4: 5152, 8: 4021, 16: 2211, 32: 944}

    # Caso Tese de Wesley 30/07/2024 - Caso 12
    #dados = {1: 138, 3: 79, 6: 71, 8: 67, 10: 80, 15: 88, 20: 99, 40: 151, 60: 170}

    # Caso Tese de Wesley 30/07/2024 - Caso 14
    # dados = {1: 136, 2: 140, 4: 214, 10: 446, 20: 685, 40: 800}

    nbits_h, min_h, max_h = 12, 0, 16
    nbits_k, min_k, max_k = 12, -1, 1
    nbits_rho, min_rho, max_rho = 20, 0, 10000
    nbits = nbits_h+nbits_k+nbits_rho

    npop = 400
    elitism = True
    nelitism = 3
    cxpb = 0.60
    mutpb = 0.15
    ngen = 1000
    verbose = True

    # output_filename = './dados/solo_2_camadas/tese_wesley_caso_14_30072024.txt'
    # fig_comparativo_filename = './dados/solo_2_camadas/tese_wesley_caso_14_30072024_fig_comparativo.html'
    # fig_erro_filename = './dados/solo_2_camadas/tese_wesley_caso_14_30072024_fig_erro.html'

    output_filename = './dados/solo_2_camadas/resultado_med_campo2024-1.txt'
    fig_comparativo_filename = './dados/solo_2_camadas/resultado_med_campo2024-1_fig_comparativo.html'
    fig_erro_filename = './dados/solo_2_camadas/resultado_med_campo2024-1_fig_erro.html'

    # ================
    # Processamento
    # ================


    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=nbits)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", eval_fitness)
    toolbox.register("mate", cxTwoPointCopy)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    def main():

        random.seed(64)

        pop = toolbox.population(n=npop)
        hof = tools.HallOfFame(nelitism, similar=numpy.array_equal)

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        if elitism:
            pop, logbook = eaSimpleWithElitism(
                pop, 
                toolbox, 
                cxpb=cxpb, 
                mutpb=mutpb, 
                ngen=ngen, 
                stats=stats, 
                halloffame=hof, 
                verbose=verbose,
            )
        else:
            pop, logbook = algorithms.eaSimple(
                pop, 
                toolbox, 
                cxpb=cxpb, 
                mutpb=mutpb, 
                ngen=ngen, 
                stats=stats, 
                halloffame=hof, 
                verbose=verbose,
            )

        return pop, stats, hof, logbook


    if __name__ == "__main__" or __name__  != "__main__":

        # # Teste com todas as variáveis no mínimo
        # ret = eval_fitness([0]*(nbits_h+nbits_k+nbits_rho))
        # print(f'{ret = }')

        # # Teste com todas as variáveis no máximo
        # ret = eval_fitness([1]*(nbits_h+nbits_k+nbits_rho))
        # print(f'{ret = }') 

        pop, stats, hof, logbook = main()

        with open(output_filename, 'w') as file_out:

            # file_out.write(f'pop = \n\n')
            # for item in pop:
            #     file_out.write(f'{item}\n')
            # file_out.write('=====\n\n')

            file_out.write(f'hof = \n\n')
            for item in hof:
                h, k, rho = decodifica_ind(item)
                dados_modelo = calcula_rhos_do_modelo(h, k, rho)
                fit = eval_fitness(item)
                rho2 = rho * (1 + k) / (1 - k)

                file_out.write(f'{item}\n')
                file_out.write(f'h = {h}, k = {k}, rho1 = {rho}, rho2 = {rho2}\n')
                file_out.write(f'fitness = {fit}\n')
                for key in dados.keys():
                    file_out.write(f'a_medido = {key:3.1f}, rho_medido = {dados[key]}, rho_modelo = {dados_modelo[key]}\n')
                file_out.write('---\n')

            file_out.write('=====\n\n')

            file_out.write(f'logbook = \n\n{logbook}\n')

            # Plotar gráficos

            ind = hof[0]
            h, k, rho = decodifica_ind(ind)
            dados_modelo = calcula_rhos_do_modelo(h, k, rho)
            dados_erro = {
                key: 100*(mod-med)/med 
                for key, med, mod in zip(dados.keys(), dados.values(), dados_modelo.values())
            }

            fig1 = plotar_comparativo_med_mod(dados, dados_modelo)
            fig2 = plotar_erros_perc_med_mod(dados_erro)

            fig1.write_html(fig_comparativo_filename)
            fig2.write_html(fig_erro_filename)

            #fig1.show()
            #fig2.show()



    print('FIM')
    return None

def ler_linha_25():
    with open("dados/solo_2_camadas/resultado_med_campo2024-1.txt", "r") as file:
        linhas = file.readlines()  # Lê todas as linhas do arquivo como uma lista
        linha_25 = linhas[24]  # Índice 24 para a linha 25, já que a contagem começa do 0
        
        
    # Remove espaços e divide a string em partes
    partes = linha_25.replace(" ", "").split(",")

    # Extraímos os valores e atribuímos às variáveis
    h = float(partes[0].split("=")[1])
    k = float(partes[1].split("=")[1])
    rho1 = float(partes[2].split("=")[1])
    rho2 = float(partes[3].split("=")[1])

    resultado = [round(h, 2), round(rho1, 2), round(rho2, 2)]

    return resultado    

def ler_linhas_27_a_31():
    a_medido = []
    rho_medido = []
    rho_modelo = []

    with open("dados/solo_2_camadas/resultado_med_campo2024-1.txt", "r") as file:
        linhas = file.readlines()[26:31]  # Lê apenas as linhas 27 a 31 (índices 26 a 30)
        
        for linha in linhas:
            # Verifica se a linha contém "a_medido" e extrai os valores
            if "a_medido" in linha:
                partes = linha.split(", ")
                
                # Extrai e armazena valores de a_medido, rho_medido e rho_modelo
                a_val = float(partes[0].split(" = ")[1])
                rho_medido_val = float(partes[1].split(" = ")[1])
                rho_modelo_val = float(partes[2].split(" = ")[1])
                
                a_medido.append(a_val)
                rho_medido.append(rho_medido_val)
                rho_modelo.append(rho_modelo_val)

    return a_medido, rho_medido, rho_modelo

#x = {1: 641.83, 2: 996.62, 4: 1437.62, 8: 1887.08, 16: 2091.32}
#x = {1: 8739.547537642615, 2: 7645.742511273771, 4: 3095.7305886123195, 8: 3858.258925489078, 16: 18950.120802924477}

#codigo_formiga(x)
#parametros = ler_linha_25()
#print(parametros)

#a, b, c = ler_linhas_27_a_31()
#print(a)
#print(b)
#print(c)