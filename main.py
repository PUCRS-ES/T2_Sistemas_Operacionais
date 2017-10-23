# -*- coding: utf-8 -*-

TAMANHO_PAGINA = 8
enderecos_fisicos = [0] * 64
enderecos_em_disco = [0] * 16

QUANTIDADE_PAGINAS = int(len(enderecos_fisicos) / TAMANHO_PAGINA)
paginas_ocupadas = [False] * QUANTIDADE_PAGINAS

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

    def calcula_paginas_necessarias(self, quantidade_enderecos):
        paginas = int(quantidade_enderecos / TAMANHO_PAGINA)
        if (quantidade_enderecos % TAMANHO_PAGINA) > 0:
            paginas += 1
        return paginas

    def proxima_pagina_livre(self):
        for index, pagina in enumerate(paginas_ocupadas):
            if pagina is False:
                return index

    def grava_processo_na_pagina(self, pos_inicial, numero_enderecos, index_pagina, id_processo):
        for i in range(pos_inicial, numero_enderecos):
            enderecos_fisicos[(index_pagina * TAMANHO_PAGINA) + i] = id_processo
        self.processos[id_processo].paginas.append(index_pagina)
        paginas_ocupadas[index_pagina] = True

    def quantidade_de_enderecos_livres_na_pagina(self, index_pagina):
        regiao = enderecos_fisicos[index_pagina * TAMANHO_PAGINA:(index_pagina + 1) * TAMANHO_PAGINA]
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
                            pagina_atual = self.proxima_pagina_livre()
                            self.grava_processo_na_pagina(0, memoria, pagina_atual, id_processo)

                        # Concluido com sucesso ate "M p3 5"
                        memoria_antes = self.processos[id_processo].quantidade_memoria
                        self.processos[id_processo].quantidade_memoria = memoria_antes + memoria

manager = ProcessManager()
manager.carrega_processos()
