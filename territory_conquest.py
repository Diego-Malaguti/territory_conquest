import random

class Territorio:
    def __init__(self, nome):
        self.nome = nome
        self.tropas = 1
        self.controlador = None

    def __str__(self):
        return f"{self.nome} (Tropas: {self.tropas}, Controlador: {self.controlador if self.controlador else 'Ninguém'})"

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.territorios = set()

    def __str__(self):
        return self.nome

class Jogo:
    def __init__(self, nomes_jogadores, mapa):
        self.jogadores = [Jogador(nome) for nome in nomes_jogadores]
        self.mapa = mapa
        self.turno_atual = 0

    def distribuir_territorios(self):
        territorios = list(self.mapa.values())
        random.shuffle(territorios)
        num_jogadores = len(self.jogadores)
        for i, territorio in enumerate(territorios):
            jogador_index = i % num_jogadores
            territorio.controlador = self.jogadores[jogador_index]
            self.jogadores[jogador_index].territorios.add(territorio)

    def calcular_reforcos(self, jogador):
        num_territorios = len(jogador.territorios)
        reforcos = max(3, num_territorios // 3)
        return reforcos

    def fase_reforco(self, jogador):
        reforcos = self.calcular_reforcos(jogador)
        print(f"\n{jogador}, você tem {reforcos} tropas para reforçar seus territórios.")
        while reforcos > 0 and jogador.territorios:
            territorio_nome = input(f"Escolha um território para reforçar ({', '.join(t.nome for t in jogador.territorios)}): ")
            territorio = self.mapa.get(territorio_nome)
            if territorio and territorio in jogador.territorios:
                try:
                    num_tropas = int(input(f"Quantas tropas deseja adicionar a {territorio_nome} ({reforcos} restantes)? "))
                    if 1 <= num_tropas <= reforcos:
                        territorio.tropas += num_tropas
                        reforcos -= num_tropas
                        print(f"{num_tropas} tropas adicionadas a {territorio_nome}.")
                    else:
                        print("Número de tropas inválido.")
                except ValueError:
                    print("Por favor, digite um número inteiro.")
            else:
                print("Território inválido ou não pertence a você.")

    def fase_ataque(self, jogador):
        print(f"\n{jogador}, é a sua fase de ataque.")
        while True:
            territorio_atacante_nome = input(f"Escolha um território seu para atacar ({', '.join(t.nome for t in jogador.territorios)} ou 'fim' para encerrar ataques): ")
            if territorio_atacante_nome.lower() == 'fim':
                break
            territorio_atacante = self.mapa.get(territorio_atacante_nome)
            if not territorio_atacante or territorio_atacante not in jogador.territorios or territorio_atacante.tropas <= 1:
                print("Território inválido para ataque (deve pertencer a você e ter mais de uma tropa).")
                continue

            territorios_adjacentes_inimigos = [
                t for t in self.mapa.values()
                if t.controlador != jogador and t.nome in self.get_fronteiras(territorio_atacante_nome)
            ]

            if not territorios_adjacentes_inimigos:
                print(f"{territorio_atacante_nome} não faz fronteira com nenhum território inimigo.")
                continue

            territorio_defensor_nome = input(f"Escolha um território inimigo adjacente para atacar ({', '.join(t.nome for t in territorios_adjacentes_inimigos)}): ")
            territorio_defensor = self.mapa.get(territorio_defensor_nome)
            if not territorio_defensor or territorio_defensor.controlador == jogador or territorio_defensor.nome not in self.get_fronteiras(territorio_atacante_nome):
                print("Território inválido para atacar.")
                continue

            self.batalha(territorio_atacante, territorio_defensor)
            if territorio_defensor.controlador == jogador:
                print(f"Você conquistou {territorio_defensor.nome}!")
                jogador.territorios.add(territorio_defensor)
                territorio_atacante.tropas -= 1  # Mover pelo menos uma tropa
                num_tropas_mover = 0
                if territorio_atacante.tropas > 0:
                    while True:
                        try:
                            num_tropas_mover = int(input(f"Quantas tropas deseja mover de {territorio_atacante.nome} para {territorio_defensor.nome} (máximo {territorio_atacante.tropas - 1})? "))
                            if 1 <= num_tropas_mover < territorio_atacante.tropas:
                                territorio_atacante.tropas -= num_tropas_mover
                                territorio_defensor.tropas += num_tropas_mover
                                break
                            else:
                                print("Número de tropas inválido.")
                        except ValueError:
                            print("Por favor, digite um número inteiro.")
                self.remover_territorio_jogador(territorio_defensor, self.get_outro_jogador(jogador))


    def batalha(self, atacante, defensor):
        print(f"\nBatalha entre {atacante.nome} (atacante, {atacante.tropas} tropas) e {defensor.nome} (defensor, {defensor.tropas} tropas).")
        dados_atacante = sorted([random.randint(1, 6) for _ in range(min(3, atacante.tropas - 1))], reverse=True)
        dados_defensor = sorted([random.randint(1, 6) for _ in range(min(2, defensor.tropas))], reverse=True)

        print(f"Dados do atacante: {dados_atacante}")
        print(f"Dados do defensor: {dados_defensor}")

        perdas_atacante = 0
        perdas_defensor = 0

        for i in range(min(len(dados_atacante), len(dados_defensor))):
            if dados_atacante[i] > dados_defensor[i]:
                perdas_defensor += 1
            else:
                perdas_atacante += 1

        atacante.tropas -= perdas_atacante
        defensor.tropas -= perdas_defensor

        print(f"Perdas do atacante: {perdas_atacante}, Perdas do defensor: {perdas_defensor}")
        print(f"Tropas restantes - {atacante.nome}: {atacante.tropas}, {defensor.nome}: {defensor.tropas}")

        if defensor.tropas <= 0:
            print(f"{atacante.controlador} conquistou {defensor.nome}!")
            defensor.controlador.territorios.remove(defensor)
            defensor.controlador = atacante.controlador
            atacante.controlador.territorios.add(defensor)

    def fase_movimento(self, jogador):
        print(f"\n{jogador}, é a sua fase de movimento (opcional).")
        while True:
            origem_nome = input(f"Escolha um território seu para mover tropas ({', '.join(t.nome for t in jogador.territorios)} ou 'fim' para pular): ")
            if origem_nome.lower() == 'fim':
                break
            origem = self.mapa.get(origem_nome)
            if not origem or origem not in jogador.territorios or origem.tropas <= 1:
                print("Território de origem inválido (deve pertencer a você e ter mais de uma tropa).")
                continue

            destino_nome = input(f"Escolha um território adjacente seu para mover tropas ({', '.join(t.nome for t in jogador.territorios if t.nome in self.get_fronteiras(origem_nome) and t != origem)}): ")
            destino = self.mapa.get(destino_nome)
            if not destino or destino not in jogador.territorios or destino.nome not in self.get_fronteiras(origem_nome):
                print("Território de destino inválido (deve ser adjacente e pertencer a você).")
                continue

            while True:
                try:
                    num_tropas = int(input(f"Quantas tropas deseja mover de {origem_nome} para {destino_nome} (máximo {origem.tropas - 1})? "))
                    if 1 <= num_tropas < origem.tropas:
                        origem.tropas -= num_tropas
                        destino.tropas += num_tropas
                        print(f"{num_tropas} tropas movidas de {origem_nome} para {destino_nome}.")
                        break
                    else:
                        print("Número de tropas inválido.")
                except ValueError:
                    print("Por favor, digite um número inteiro.")

    def get_fronteiras(self, territorio_nome):
        # Defina as fronteiras entre os territórios aqui
        fronteiras = {
            "Brasil": ["Argentina", "Peru"],
            "Argentina": ["Brasil", "Chile"],
            "Chile": ["Argentina", "Peru"],
            "Peru": ["Brasil", "Chile"],
            "Canada": ["Estados Unidos"],
            "Estados Unidos": ["Canada", "Mexico"],
            "Mexico": ["Estados Unidos"]
        }
        return fronteiras.get(territorio_nome, [])

    def verificar_vencedor(self):
        if not self.jogadores:
            return None
        primeiro_jogador = self.jogadores[0]
        if all(territorio.controlador == primeiro_jogador for territorio in self.mapa.values()):
            return primeiro_jogador
        return None

    def get_outro_jogador(self, jogador_atual):
        for jogador in self.jogadores:
            if jogador != jogador_atual:
                return jogador
        return None

    def remover_territorio_jogador(self, territorio, jogador_perdedor):
        if jogador_perdedor and territorio in jogador_perdedor.territorios:
            jogador_perdedor.territorios.remove(territorio)
            if not jogador_perdedor.territorios:
                print(f"\n{jogador_perdedor} foi eliminado!")
                self.jogadores.remove(jogador_perdedor)

    def jogar_turno(self):
        jogador_atual = self.jogadores[self.turno_atual % len(self.jogadores)]
        print(f"\n----- Turno de {jogador_atual} -----")

        # Fase de Reforço
        self.fase_reforco(jogador_atual)

        # Fase de Ataque
        self.fase_ataque(jogador_atual)

        # Fase de Movimento
        self.fase_movimento(jogador_atual)

        vencedor = self.verificar_vencedor()
        if vencedor:
            print(f"\nParabéns, {vencedor}! Você conquistou todos os territórios e venceu o jogo!")
            return True

        self.turno_atual += 1
        return False

def main():
    nomes_jogadores = ["Jogador 1", "Jogador 2"]
    mapa_jogo = {
        "Brasil": Territorio("Brasil"),
        "Argentina": Territorio("Argentina"),
        "Chile": Territorio("Chile"),
        "Peru": Territorio("Peru"),
        "Canada": Territorio("Canada"),
        "Estados Unidos": Territorio("Estados Unidos"),
        "Mexico": Territorio("Mexico")
    }
    jogo = Jogo(nomes_jogadores, mapa_jogo)
    jogo.distribuir_territorios()

    jogo_terminou = False
    while not jogo_terminou and len(jogo.jogadores) > 1:
        jogo_terminou = jogo.jogar_turno()

    if len(jogo.jogadores) == 1 and not jogo_terminou:
        print(f"\nParabéns, {jogo.jogadores[0]}! Você é o último jogador sobrevivente e venceu!")
    elif len(jogo.jogadores) <= 1 and not jogo_terminou:
        print("\nO jogo terminou sem um vencedor claro.")

if __name__ == "__main__":
    main()