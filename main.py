# -*- coding: utf-8 -*-

TAMANHO_PAGINA = 8
enderecos_fisicos = [0] * 64
enderecos_em_disco = [0] * 16

QUANTIDADE_PAGINAS = int(len(enderecos_fisicos) / TAMANHO_PAGINA)
paginas_ocupadas = [False] * QUANTIDADE_PAGINAS
pagina_acessada_em = [0] * QUANTIDADE_PAGINAS
paginas_disco_ocupadas = [False] * int(len(enderecos_em_disco) / TAMANHO_PAGINA)

class Process():
    _id = 0
    quantidade_memoria = 0
    paginas = []

    def __init__(self, _id, quantidade_memoria):
        self.id = _id
        self.quantidade_memoria = quantidade_memoria
        self.paginas = []


class ProcessManager():
    processos = { }
    # Assumindo que toda vez que lemos uma instrucao/linha gastamos 1 seg
    tempo_geral = 0

    def calcula_paginas_necessarias(self, quantidade_enderecos):
        paginas = int(quantidade_enderecos / TAMANHO_PAGINA)
        if (quantidade_enderecos % TAMANHO_PAGINA) > 0:
            paginas += 1
        return paginas

    def proxima_pagina_livre(self):
        for index, pagina in enumerate(paginas_ocupadas):
            if pagina is False:
                return index
        return None

    def proxima_pagina_disco_livre(self):
        for index, pagina in enumerate(paginas_disco_ocupadas):
            if pagina is False:
                return index
        return None

    def get_pagina_usando_least_recent_used(self):
        tempo_pagina_escolhida = 999999
        index_pagina_escolhida = None
        for index, tempo_atual in enumerate(pagina_acessada_em):
            if tempo_atual < tempo_pagina_escolhida:
                tempo_pagina_escolhida = tempo_atual
                index_pagina_escolhida = index
        return index_pagina_escolhida

    def move_pagina_da_memoria_para_disco(self, index_pagina_memoria, index_pagina_disco):
        for i in range(0, TAMANHO_PAGINA):
            valor_para_copiar = enderecos_fisicos[(index_pagina_memoria * TAMANHO_PAGINA) + i]
            enderecos_em_disco[(index_pagina_disco * TAMANHO_PAGINA) + i] = valor_para_copiar
            enderecos_fisicos[(index_pagina_memoria * TAMANHO_PAGINA) + i] = 0
        paginas_ocupadas[index_pagina_memoria] = False
        paginas_disco_ocupadas[index_pagina_disco] = True
        id_processo_movido = enderecos_em_disco[(index_pagina_disco * TAMANHO_PAGINA)]

        # Atualiza a lista de paginas do processo para indicar que a pagina foi movida para o disco
        paginas = self.processos[id_processo_movido].paginas
        paginas[paginas.index(index_pagina_memoria)] = {'disco': index_pagina_disco}

    def move_pagina_do_disco_para_memoria(self, index_pagina_disco, index_pagina_memoria):
        pass

    def grava_processo_na_pagina(self, pos_inicial, numero_enderecos, index_pagina, id_processo):
        for i in range(pos_inicial, numero_enderecos):
            enderecos_fisicos[(index_pagina * TAMANHO_PAGINA) + i] = id_processo
        
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

    def carrega_processos(self):
        with open("origem.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            for index, linha in enumerate(linhas):
                # Ignora 5 primeiras linhas que nao sao instrucoes de processos
                if index < 5:
                    continue
                
                instrucoes = linha.split(' ')
                acao = instrucoes[0]
                id_processo = instrucoes[1]
                memoria = int(instrucoes[2])
                self.tempo_geral += 1

                if acao == "C":
                    print("Criar processo")
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
                elif acao == "A":
                    print("Acesso/leitura")
                    if id_processo in self.processos:
                        if memoria < self.processos[id_processo].quantidade_memoria:
                            print("Existe um valor para posicao " + str(memoria) + " de " + id_processo)
                        else:
                            print("Erro de acesso - " + id_processo + ":" + str(self.processos[id_processo].quantidade_memoria) + ":" + str(memoria))
                elif acao == "M":
                    print("Alocar/aumentar memoria")
                    if id_processo in self.processos:
                        ultima_pagina = self.processos[id_processo].paginas[-1:][0]
                        memoria_disponivel = self.quantidade_de_enderecos_livres_na_pagina(ultima_pagina)
                        if memoria < memoria_disponivel:
                            pos_inicial = TAMANHO_PAGINA - memoria_disponivel
                            self.grava_processo_na_pagina(pos_inicial, memoria + pos_inicial, ultima_pagina, id_processo)
                        else:
                            
                            # Se ainda tivermos algum espaco disponivel na ultima_pagina, devemos primeiro
                            # preencher todo esse espaço, e DEPOIS escrever na nova pagina
                            if memoria_disponivel > 0:
                                pos_inicial = TAMANHO_PAGINA - memoria_disponivel
                                self.grava_processo_na_pagina(pos_inicial, TAMANHO_PAGINA, ultima_pagina, id_processo)
                                
                                memoria_antes = self.processos[id_processo].quantidade_memoria
                                self.processos[id_processo].quantidade_memoria = memoria_antes + memoria_disponivel
                                
                                memoria = memoria - memoria_disponivel
                            
                            # Agora devemos buscar a proxima pagina livre, e gravar os dados restantes nela
                            pagina_atual = self.proxima_pagina_livre()
                            
                            # Tira uma pagina da memoria, movendo-a para o disco (se houver espaco)
                            if pagina_atual is None:
                                pagina_atual = self.get_pagina_usando_least_recent_used()
                                print("Memoria RAM antes do page fault: ", enderecos_fisicos)
                                print("Disco antes do page fault: ", enderecos_em_disco)
                                self.move_pagina_da_memoria_para_disco(pagina_atual, self.proxima_pagina_disco_livre())

                                print("Memoria RAM depois do page fault: ", enderecos_fisicos)
                                print("Disco depois do page fault: ", enderecos_em_disco)

                            self.grava_processo_na_pagina(0, memoria, pagina_atual, id_processo)
                            
                            # Continuar em "A p1 1"

                        memoria_antes = self.processos[id_processo].quantidade_memoria
                        self.processos[id_processo].quantidade_memoria = memoria_antes + memoria

manager = ProcessManager()
manager.carrega_processos()
