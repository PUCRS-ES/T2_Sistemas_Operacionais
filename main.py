# -*- coding: utf-8 -*-
from random import randint
from sys import version

TEXTO = "Pressione ENTER para a proxima instrucao"

# Estas informacoes serao lidas a partir de um arquivo
SEQUENCIAL = True
ALGORITMO_LRU = True
TAMANHO_PAGINA = 8
enderecos_fisicos = [0] * 64
enderecos_em_disco = [0] * 16

# Outras variaveis auxiliares calculadas em funcao do arquivo de origem
QUANTIDADE_PAGINAS = int(len(enderecos_fisicos) / TAMANHO_PAGINA)
paginas_ocupadas = [False] * QUANTIDADE_PAGINAS
pagina_acessada_em = [0] * QUANTIDADE_PAGINAS
paginas_disco_ocupadas = [False] * int(len(enderecos_em_disco) / TAMANHO_PAGINA)

# Depois das definicoes iniciais do arquivo lido, cada linha dele
# representa uma acao sobre um processo
class Process():
    _id = 0
    quantidade_memoria = 0
    paginas = []

    def __init__(self, _id, quantidade_memoria):
        self.id = _id
        self.quantidade_memoria = quantidade_memoria
        self.paginas = []


# Classe principal que gerencia os processos
class ProcessManager():
    # Poderia tambem usar uma lista, mas se tivermos muitos processos
    # um dicionario tem acesso mais rapido
    processos = { }

    # Assumindo que toda vez que lemos uma instrucao/linha gastamos 1 seg
    tempo_geral = 0

    # string opcional para descrever os page faults ("antes" ou "depois" por ex)
    def pretty_print_ram_E_disco(self, estado=""):
        print("Memoria RAM " + estado)
        self.pretty_print_ram()
        print("Disco " + estado)
        self.pretty_print_disco()

    # imprime a memoria de forma legivel (uma pagina por linha)
    def pretty_print_ram(self):
        for pagina_atual in range(0, QUANTIDADE_PAGINAS):
            saida = "Pagina " + str(pagina_atual) + ": "
            for posicao_na_pagina in range(0, TAMANHO_PAGINA):
                saida += str(enderecos_fisicos[(pagina_atual * TAMANHO_PAGINA) + posicao_na_pagina]) + " "
            print(saida)

    # imprime a memoria do disco de forma legivel (uma pagina por linha)
    def pretty_print_disco(self):
        quantidade_paginas_disco = int(len(enderecos_em_disco) / TAMANHO_PAGINA)
        for pagina_atual in range(0, quantidade_paginas_disco):
            saida = "Pagina " + str(pagina_atual) + ": "
            for posicao_na_pagina in range(0, TAMANHO_PAGINA):
                saida += str(enderecos_em_disco[(pagina_atual * TAMANHO_PAGINA) + posicao_na_pagina]) + " "
            print(saida)

    # calcula quantidade de paginas necessarias para criar um processo
    def calcula_paginas_necessarias(self, quantidade_enderecos):
        paginas = int(quantidade_enderecos / TAMANHO_PAGINA)
        if (quantidade_enderecos % TAMANHO_PAGINA) > 0:
            paginas += 1
        return paginas

    # retorna o indice da proxima pagina livre na memoria, ou null se todas estiverem ocupadas
    def proxima_pagina_livre(self):
        for index, pagina in enumerate(paginas_ocupadas):
            if pagina is False:
                return index
        return None

    # retorna o indice da proxima pagina livre do disco, ou null se todas estiverem ocupadas
    def proxima_pagina_disco_livre(self):
        for index, pagina in enumerate(paginas_disco_ocupadas):
            if pagina is False:
                return index
        return None

    # retorna o indice da pagina que sera retirada da memoria quando ocorrer um page fault
    def get_pagina_usando_least_recent_used(self):
        print("Pagina acessada em: ")
        print(pagina_acessada_em)
        tempo_pagina_escolhida = 999999
        index_pagina_escolhida = None
        for index, tempo_atual in enumerate(pagina_acessada_em):
            if tempo_atual < tempo_pagina_escolhida:
                tempo_pagina_escolhida = tempo_atual
                index_pagina_escolhida = index
        return index_pagina_escolhida

    # escolhe uma pagina aleatoria para ser retirada da memoria no caso de um page fault
    def get_pagina_aleatoria(self, max_page_index):
        return randint(0, max_page_index)

    def move_pagina_da_memoria_para_disco(self, index_pagina_memoria, index_pagina_disco):
        for i in range(0, TAMANHO_PAGINA):
            valor_para_copiar = enderecos_fisicos[(index_pagina_memoria * TAMANHO_PAGINA) + i]
            enderecos_em_disco[(index_pagina_disco * TAMANHO_PAGINA) + i] = valor_para_copiar
            enderecos_fisicos[(index_pagina_memoria * TAMANHO_PAGINA) + i] = 0
        # atualiza nas listas de controle que a pagina esta livre na memoria, e ocupada no disco
        paginas_ocupadas[index_pagina_memoria] = False
        paginas_disco_ocupadas[index_pagina_disco] = True
        id_processo_movido = enderecos_em_disco[(index_pagina_disco * TAMANHO_PAGINA)]

        # Atualiza a lista de paginas do processo para indicar que a pagina foi movida para o disco
        # Ao inves de um index que aponta para uma posicao na memoria, teremos um dicionario, que
        # que aponta para uma pagina do disco
        paginas = self.processos[id_processo_movido].paginas
        paginas[paginas.index(index_pagina_memoria)] = {'disco': index_pagina_disco}

    def move_pagina_do_disco_para_memoria(self, index_pagina_disco, index_pagina_memoria):
        for i in range(0, TAMANHO_PAGINA):
            valor_para_copiar = enderecos_em_disco[(index_pagina_disco * TAMANHO_PAGINA) + i]
            enderecos_fisicos[(index_pagina_memoria * TAMANHO_PAGINA) + i] = valor_para_copiar
            enderecos_em_disco[(index_pagina_disco * TAMANHO_PAGINA) + i] = 0
        # atualiza nas listas de controle que a pagina esta livre no disco, e ocupada na memoria
        paginas_disco_ocupadas[index_pagina_disco] = False
        paginas_ocupadas[index_pagina_memoria] = True
        id_processo_movido = enderecos_fisicos[(index_pagina_memoria * TAMANHO_PAGINA)]

        # Atualiza a lista de paginas do processo para indicar que a pagina foi movida para a memoria
        paginas = self.processos[id_processo_movido].paginas
        paginas[paginas.index({'disco': index_pagina_disco})] = index_pagina_memoria

    # Grava efetivamente dados na memoria
    def grava_processo_na_pagina(self, pos_inicial, numero_enderecos, index_pagina, id_processo):
        for i in range(pos_inicial, numero_enderecos):
            enderecos_fisicos[(index_pagina * TAMANHO_PAGINA) + i] = id_processo
        
        # Registra que a pagina pertence ao processo "id_processo" agora, e marca ela como ocupada
        if index_pagina not in self.processos[id_processo].paginas:
            self.processos[id_processo].paginas.append(index_pagina)
        paginas_ocupadas[index_pagina] = True
        pagina_acessada_em[index_pagina] = self.tempo_geral

    def quantidade_de_enderecos_livres_na_pagina(self, index_pagina):
        regiao = enderecos_fisicos[index_pagina * TAMANHO_PAGINA : (index_pagina + 1) * TAMANHO_PAGINA]
        for index, valor in enumerate(regiao):
            if valor == 0:
                return (TAMANHO_PAGINA - index)
        return 0

    def criar_processo(self, id_processo, memoria):
        print("Criar processo: C " + id_processo + " " + str(memoria))
        if id_processo not in self.processos:
            self.processos[id_processo] = Process(id_processo, memoria)
            numero_paginas = self.calcula_paginas_necessarias(memoria)

            pagina_atual = 0
            while numero_paginas > 0:
                pagina_atual = self.proxima_pagina_livre()

                numero_enderecos = TAMANHO_PAGINA if memoria > TAMANHO_PAGINA else memoria
                self.grava_processo_na_pagina(0, numero_enderecos, pagina_atual, id_processo)
                memoria -= numero_enderecos
                numero_paginas -= 1

    def carrega_processos(self):
        with open("origem.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            
            ############### Efetua a leitura das 5 linhas iniciais do arquivo.
            # Essas linhas possuem apenas configuracoes da memoria e disco, mas
            #nao acoes sobre os processos ###############
            for index, linha in enumerate(linhas):
                linhas[index] = linhas[index].strip()
            setup = linhas[:5]

            if setup[0] == "0" or setup[0] == "sequencial" or setup[0] == "s":
                SEQUENCIAL = True
            elif setup[0] == "1" or setup[0] == "aleatorio" or setup[0] == "a":
                SEQUENCIAL = False
            else:
                raise Exception('Entrada invalida para sequencial/aleatorio.')

            if setup[1] == "lru":
                ALGORITMO_LRU = True
            elif setup[1] == "aleatorio":
                ALGORITMO_LRU = False
            else:
                raise Exception('Entrada invalida para algoritmo de troca de paginas.')

            try:
                TAMANHO_PAGINA = int(setup[2])
            except Exception:
                raise Exception('Entrada invalida para tamanho da pagina.')

            try:
                enderecos_fisicos = [0] * int(setup[3])
            except Exception:
                raise Exception('Entrada invalida para quantidade de enderecos fisicos (RAM).')

            try:
                enderecos_em_disco = [0] * int(setup[4])
            except Exception:
                raise Exception('Entrada invalida para quantidade de enderecos em disco.')

            linhas = linhas[5:]
            ############### Fim da leitura das 5 linhas iniciais ###############


            # Se for modo aleatorio, remove a criacao de processos da lista de instrucoes e cria eles
            if SEQUENCIAL is False:
                i = 0
                while i < len(linhas):
                    linha = linhas[i]
                    if linha[0] == "C":
                        linhas.pop(i)
                        instrucoes = linha.split(' ')
                        acao = instrucoes[0]
                        id_processo = instrucoes[1]
                        memoria = int(instrucoes[2])
                        self.tempo_geral += 1
                        self.criar_processo(id_processo, memoria)
                    else:
                        i += 1

            # Executa as acoes sobre os processos (inclusive criar, se sequencial)
            for index, linha in enumerate(linhas):
                instrucoes = linha.split(' ')
                acao = instrucoes[0]
                id_processo = instrucoes[1]
                memoria = int(instrucoes[2])
                self.tempo_geral += 1

                if acao == "C":
                    self.criar_processo(id_processo, memoria)
                
                # Acessa a memoria
                elif acao == "A":
                    print("Acesso/leitura: " + linha)
                    
                    # Se o processo nao existe, ignora
                    if id_processo in self.processos:
                        processo_atual = self.processos[id_processo]
                        pagina_para_acessar = int(memoria / TAMANHO_PAGINA)
                        print("Paginas de " + id_processo + " :")
                        print(processo_atual.paginas)
                        print("Pagina desejada: " + str(pagina_para_acessar) + " (logica)")

                        # A pagina para o processo existe E a memoria esta dentro do limite do processo
                        if pagina_para_acessar < len(processo_atual.paginas) and memoria < processo_atual.quantidade_memoria:
                            print("Pagina desejada: " + str(processo_atual.paginas[pagina_para_acessar]) + " (fisica)")

                            # Apesar da pagina existir, ela esta em disco e nao em memoria.
                            # Precisamos liberar espaco na memoria e traze-la do disco para memoria.
                            if type(processo_atual.paginas[pagina_para_acessar]) is dict:
                                print("---------------------------------")
                                self.pretty_print_ram_E_disco("antes do page fault: ")
                                print("---------------------------------")

                                # Decide como vai liberar uma pagina da memoria
                                if ALGORITMO_LRU:
                                    pagina_origem = self.get_pagina_usando_least_recent_used()
                                else:
                                    pagina_origem = self.get_pagina_aleatoria(QUANTIDADE_PAGINAS)
                                print("Pagina escolhida: " + str(pagina_origem) + " (fisica)")
                                print("---------------------------------")
                                pagina_destino = self.proxima_pagina_disco_livre()
                                self.move_pagina_da_memoria_para_disco(pagina_origem, pagina_destino)
                                
                                pagina_destino = pagina_origem
                                pagina_origem = processo_atual.paginas[pagina_para_acessar]['disco']
                                self.move_pagina_do_disco_para_memoria(pagina_origem, pagina_destino)

                                self.pretty_print_ram_E_disco("depois do page fault: ")
                                print("---------------------------------")
                            #else:
                            #    # Como a pagina foi acessada, devemos atualizar o instante de tempo
                            #    # do ultimo acesso. Importante para o calculo do LRU.
                            #    pagina_acessada_em[pagina_para_acessar] = self.tempo_geral
                        # A pagina nao existe. Informa o usuario
                        else:
                            print("Erro de acesso - " + id_processo + ":" + str(processo_atual.quantidade_memoria) + ":" + str(memoria))
                
                # Aloca mais memoria para o processo
                elif acao == "M":
                    print("Alocar/aumentar memoria: " + linha)
                    
                    # Se o processo nao existe, ignora
                    if id_processo in self.processos:
                        
                        # Obtem a ultima pagina do processo, e quanto de memoria (bytes) ainda tem disponivel nela
                        ultima_pagina = self.processos[id_processo].paginas[-1:][0]
                        memoria_disponivel = self.quantidade_de_enderecos_livres_na_pagina(ultima_pagina)
                        
                        # Se a quantidade de memoria solicitada for menor que a quantidade disponível, só escreve na mesma pagina
                        if memoria < memoria_disponivel:
                            pos_inicial = TAMANHO_PAGINA - memoria_disponivel
                            self.grava_processo_na_pagina(pos_inicial, memoria + pos_inicial, ultima_pagina, id_processo)
                        else:
                            
                            # Se ainda tivermos algum espaco disponivel na ultima_pagina, devemos PRIMEIRO
                            # preencher todo esse espaço, e DEPOIS escrever na nova pagina
                            if memoria_disponivel > 0:
                                pos_inicial = TAMANHO_PAGINA - memoria_disponivel
                                self.grava_processo_na_pagina(pos_inicial, TAMANHO_PAGINA, ultima_pagina, id_processo)
                                
                                memoria_antes = self.processos[id_processo].quantidade_memoria
                                self.processos[id_processo].quantidade_memoria = memoria_antes + memoria_disponivel
                                
                                memoria = memoria - memoria_disponivel
                            
                            # Agora devemos buscar a proxima pagina livre, e gravar os dados restantes nela
                            pagina_atual = self.proxima_pagina_livre()
                            
                            # Se nao houver mais paginas livres na memoria, remove uma movendo-a para o disco
                            if pagina_atual is None:
                                
                                pagina_disco_livre = self.proxima_pagina_disco_livre()
                                if pagina_disco_livre is None:
                                    print("Não tem mais memória")
                                    continue
                                else:
                                    # Decide como vai liberar uma pagina da memoria
                                    if ALGORITMO_LRU:
                                        pagina_atual = self.get_pagina_usando_least_recent_used()
                                    else:
                                        pagina_atual = self.get_pagina_aleatoria(QUANTIDADE_PAGINAS)
                                    print("---------------------------------")
                                    print("Pagina escolhida: " + str(pagina_atual) + " (fisica)")
                                    print("---------------------------------")
                                    self.pretty_print_ram_E_disco("antes do page fault: ")
                                    print("---------------------------------")

                                    self.move_pagina_da_memoria_para_disco(pagina_atual, pagina_disco_livre)
                                    self.pretty_print_ram_E_disco("depois do page fault: ")
                                    print("---------------------------------")

                            self.grava_processo_na_pagina(0, memoria, pagina_atual, id_processo)

                        memoria_antes = self.processos[id_processo].quantidade_memoria
                        self.processos[id_processo].quantidade_memoria = memoria_antes + memoria

                # Permite acompanhar passo-a-passo cada acao com os processos
                self.pretty_print_ram_E_disco()
                if version[0] == "2":
                    raw_input(TEXTO)
                elif version[0] == "3":
                    input(TEXTO)
                print("\n\n\n")

manager = ProcessManager()
manager.carrega_processos()
