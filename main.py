# -*- coding: utf-8 -*-

TAMANHO_PAGINA = 8
enderecos_fisicos = [0] * 64
enderecos_em_disco = [0] * 16

class Process():
    _id = 0
    quantidade_memoria = 0
    paginas = []

    def __init__(self, _id, quantidade_memoria, paginas):
        self.id = _id
        self.quantidade_memoria = quantidade_memoria


class ProcessManager():
    processos = []

    def carrega_processos():
        with open("origem.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            for linha in linhas:
                instrucoes = linha.split(' ')
                acao = instrucoes[0]
                id_processo = instrucoes[1]
                posicao_relativa_memoria[2]

                if acao == "C":
                    print("Criar processo")
                elif acao == "A":
                    print("Acesso/leitura")
                elif acao == "M":
                    print("Alocar/aumentar memoria")

