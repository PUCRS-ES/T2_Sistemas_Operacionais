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
                posicao_relativa_memoria = int(instrucoes[2])

                if acao == "C":
                    print("Criar processo")
                    if id_processo not in self.processos:
                        self.processos[id_processo] = Process(id_processo, posicao_relativa_memoria)
                        numero_paginas = self.calcula_paginas_necessarias(posicao_relativa_memoria)
                        paginas = []
                        endereco_atual = 0
                        while numero_paginas > 0:
                            if enderecos_fisicos[endereco_atual] == 0:
                                for i in range(0, TAMANHO_PAGINA):
                                    enderecos_fisicos[endereco_atual + i] = id_processo
                                paginas.append(endereco_atual / TAMANHO_PAGINA)
                                numero_paginas -= 1
                            endereco_atual += TAMANHO_PAGINA
                        self.processos[id_processo].set_paginas(paginas)
                elif acao == "A":
                    print("Acesso/leitura")
                elif acao == "M":
                    print("Alocar/aumentar memoria")


manager = ProcessManager()
manager.carrega_processos()
