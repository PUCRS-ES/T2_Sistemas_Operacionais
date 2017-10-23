# -*- coding: utf-8 -*-

TAMANHO_PAGINA = 8
enderecos_fisicos = [0] * 64
enderecos_em_disco = [0] * 16

class Process():
    _id = 0
    quantidade_memoria = 0
    paginas = []

    def __init__(self, _id, quantidade_memoria):
        self.id = _id
        self.quantidade_memoria = quantidade_memoria

    def set_paginas(self, lista_de_paginas):
        self.paginas = lista_de_paginas


class ProcessManager():
    processos = { }

    def calcula_paginas_necessarias(self, quantidade_enderecos):
        paginas = quantidade_enderecos / TAMANHO_PAGINA
        if (quantidade_enderecos % TAMANHO_PAGINA) > 0:
            paginas += 1
        return paginas

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
                        paginas = []
                        endereco_atual = 0
                        while numero_paginas > 0:
                            if enderecos_fisicos[endereco_atual] == 0:
                                enderecos_escrever = TAMANHO_PAGINA if memoria > TAMANHO_PAGINA else memoria
                                for i in range(0, enderecos_escrever):
                                    enderecos_fisicos[endereco_atual + i] = id_processo
                                    memoria -= 1
                                paginas.append(endereco_atual / TAMANHO_PAGINA)
                                numero_paginas -= 1
                            endereco_atual += TAMANHO_PAGINA
                        self.processos[id_processo].set_paginas(paginas)
                elif acao == "A":
                    print("Acesso/leitura")
                    if id_processo in self.processos:
                        if memoria < self.processos[id_processo].quantidade_memoria:
                            print("Existe um valor para posicao " + str(memoria) + " de " + id_processo)
                        else:
                            print("Erro de acesso - " + id_processo + ":" + str(self.processos[id_processo].quantidade_memoria) + ":" + str(memoria))
                elif acao == "M":
                    print("Alocar/aumentar memoria")


manager = ProcessManager()
manager.carrega_processos()
