import sys
import math
import random
import time

# Funções para políticas de substituição
def substituir_random(cache, indice, tag, assoc):
    """Substitui uma linha aleatória no conjunto."""
    random_num = random.randint(0, assoc - 1)
    cache[indice][random_num].tag = tag
    cache[indice][random_num].validade = 1

def substituir_fifo(cache, indice, tag, fifo, assoc):
    """Substitui a linha mais antiga no conjunto (FIFO)."""
    cache[indice][fifo[indice]].tag = tag
    cache[indice][fifo[indice]].validade = 1
    fifo[indice] = (fifo[indice] + 1) % assoc

def substituir_lru(cache, indice, tag, tempoatual, assoc):
    """Substitui a linha menos recentemente usada no conjunto (LRU)."""
    tempoantigo = tempoatual
    indiceantigo = -1
    for j in range(assoc):
        if cache[indice][j].time <= tempoantigo:
            tempoantigo = cache[indice][j].time
            indiceantigo = j
            tempoatual += 1
    if indiceantigo != -1:
        cache[indice][indiceantigo].tag = tag
        cache[indice][indiceantigo].time = tempoatual
    return tempoatual

def main(argv):
    if len(argv) != 7:
        print("Número de argumentos incorreto. Utilize:")
        print("./cache_simulator <nsets> <bsize> <assoc> <substituição> <flag_saida> arquivo_de_entrada")
        sys.exit(1)

    nsets = int(argv[1])
    bsize = int(argv[2])
    assoc = int(argv[3])
    subst = argv[4]
    flagOut = int(argv[5])
    Enderecos = argv[6]

    print(f"nsets = {nsets}")
    print(f"bsize = {bsize}")
    print(f"assoc = {assoc}")
    print(f"subst = {subst}")
    print(f"flagOut = {flagOut}")
    print(f"arquivo = {Enderecos}")

    # Struct que define cada bloco.
    class CacheLine:
        def __init__(self):
            self.tag = -1
            self.validade = 0
            self.time = 0

    # Inicialização dos valores.
    total_acessos = 0
    acertos = 0  # Renomeado de "hit" para "acertos"
    miss_compulsorio = 0
    miss_capacidade = 0
    miss_conflito = 0

    n_bits_offset = int(math.log2(bsize))  # Calcula os bits para o offset.
    n_bits_indice = int(math.log2(nsets))  # Calcula os bits para o índice.
    blocos_vazios = nsets * assoc  # Contador para o miss de capacidade.

    cache = [[CacheLine() for _ in range(assoc)] for _ in range(nsets)]  # Define o tamanho da matriz que representa a cache.

    # Inicia a leitura do arquivo binário.
    with open(Enderecos, "rb") as fp:
        # Move a posição atual para o final do arquivo e obtém o tamanho.
        fp.seek(0, 2)  # 2 indica o final do arquivo.
        file_size = fp.tell()  # Obtém o tamanho do arquivo.

        # Move a posição atual de volta para o início do arquivo.
        fp.seek(0)

        # Lê o conteúdo do arquivo.
        buffer = fp.read(file_size)

    # Converte e armazena no array "dec_values" os valores inteiros.
    num_values = file_size // 4  # Calcula o número de valores inteiros no arquivo.
    dec_values = [int.from_bytes(buffer[i:i+4], byteorder='big') for i in range(0, file_size, 4)]

    # Dicionário de funções para políticas de substituição
    politicas_substituicao = {
        "R": substituir_random,
        "F": substituir_fifo,
        "L": substituir_lru
    }

    # Verifica se a política de substituição é válida
    if subst not in politicas_substituicao:
        print(f"Política de substituição inválida: {subst}")
        sys.exit(1)

    # Obtém a função correspondente à política de substituição
    substituir = politicas_substituicao[subst]

    # Mapeamento Direto
    if assoc == 1:
        for i in range(num_values):
            total_acessos += 1
            endereco = dec_values[i]
            tag = endereco >> (n_bits_offset + n_bits_indice)
            indice = (endereco >> n_bits_offset) & ((1 << n_bits_indice) - 1)

            # Verifica se o bloco está na cache.
            if cache[indice][0].validade == 1:  # Linha válida.
                if cache[indice][0].tag == tag:  # Hit.
                    acertos += 1
                else:  # Miss de conflito.
                    miss_conflito += 1
                    cache[indice][0].tag = tag
            else:  # Linha inválida.
                if blocos_vazios == 0:  # Miss de capacidade.
                    miss_capacidade += 1
                else:  # Miss compulsório.
                    miss_compulsorio += 1
                    blocos_vazios -= 1

                # Atualiza a linha da cache.
                cache[indice][0].validade = 1
                cache[indice][0].tag = tag

    # Mapeamento Associativo
    if assoc > 1:
        random.seed(time.time())
        fifo = [0] * nsets  # Cria uma lista para rastrear a próxima linha a ser substituída em cada conjunto (FIFO).
        tempoatual = 0  # Inicializa um contador de tempo para o algoritmo LRU.

        for i in range(num_values):
            total_acessos += 1
            hita = 0
            endereco = dec_values[i]
            tag = endereco >> (n_bits_offset + n_bits_indice)
            indice = (endereco >> n_bits_offset) & ((1 << n_bits_indice) - 1)

            # Verifica se o endereço está na cache (hit).
            for j in range(assoc):
                if cache[indice][j].validade and cache[indice][j].tag == tag:
                    hita = 1
                    acertos += 1
                    cache[indice][j].time = tempoatual
                    tempoatual += 1
                    break

            if not hita:
                empty_line = -1
                for j in range(assoc):
                    if not cache[indice][j].validade:
                        empty_line = j
                        break

                if empty_line != -1:  # Se houver uma linha inválida, coloca a nova linha lá.
                    miss_compulsorio += 1
                    cache[indice][empty_line].tag = tag
                    cache[indice][empty_line].validade = 1
                    cache[indice][empty_line].time = tempoatual
                    tempoatual += 1
                    blocos_vazios -= 1
                elif blocos_vazios == 0:  # Miss de capacidade.
                    miss_capacidade += 1
                    if subst == "L":  # LRU precisa retornar o tempoatual atualizado
                        tempoatual = substituir(cache, indice, tag, tempoatual, assoc)
                    else:
                        substituir(cache, indice, tag, fifo, assoc)
                else:  # Miss de conflito.
                    miss_conflito += 1
                    if subst == "L":  # LRU precisa retornar o tempoatual atualizado
                        tempoatual = substituir(cache, indice, tag, tempoatual, assoc)
                    else:
                        substituir(cache, indice, tag, fifo, assoc)

    # Calcula as taxas de Hit e Miss
    taxa_hit = acertos / total_acessos
    miss = miss_capacidade + miss_compulsorio + miss_conflito
    taxa_miss = miss / total_acessos
    taxa_miss_compulsorio = miss_compulsorio / miss if miss != 0 else 0
    taxa_miss_capacidade = miss_capacidade / miss if miss != 0 else 0
    taxa_miss_conflito = miss_conflito / miss if miss != 0 else 0

    # Seleciona o método de impressão dos valores de acordo com a flag.
    if flagOut == 0:
        print(f"\nTotal valores: {total_acessos:.0f}")
        print(f"Taxa de Hit: {taxa_hit:.2f}")
        print(f"Taxa de Miss: {taxa_miss:.2f}")
        print(f"Taxa de Miss Compulsório: {taxa_miss_compulsorio:.2f}")
        print(f"Taxa de Miss de Capacidade: {taxa_miss_capacidade:.2f}")
        print(f"Taxa de Miss de Conflito: {taxa_miss_conflito:.2f}")
    elif flagOut == 1:
        print(f"\n {total_acessos:.0f} {taxa_hit:.2f} {taxa_miss:.2f} {taxa_miss_compulsorio:.2f} {taxa_miss_capacidade:.2f} {taxa_miss_conflito:.2f}")

if __name__ == "__main__":
    main(sys.argv)