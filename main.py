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


class ProcessManager():
    processos = { }

    def carrega_processos(self):
        with open("origem.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            for index, linha in enumerate(linhas):
                # Ignora 5 primeiras linhas que não são instrucoes de processos
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
                elif acao == "A":
                    print("Acesso/leitura")
                elif acao == "M":
                    print("Alocar/aumentar memoria")

