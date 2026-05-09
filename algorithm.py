import time

CAPACIDADE_BATERIA = 75


def ler_numero(texto, minimo, maximo):

    while True:

        try:
            valor = int(input(texto))

            if minimo <= valor <= maximo:
                return valor

            print(f"Digite entre {minimo} e {maximo}")

        except:
            print("Valor inválido")


def calcular_custo(energia, tarifa, taxa):

    return (energia * tarifa) + taxa


def executar_recarga(bateria, limite, potencia, tarifa, taxa):

    energia_total = 0
    tempo = 0

    print("\n⚡ Iniciando recarga...\n")

    while bateria < limite:

        # eficiência reduz após 80%
        if bateria < 80:
            eficiencia = 1
        else:
            eficiencia = 0.5

        # energia por minuto
        energia_min = (potencia * eficiencia) / 60

        #conversão para %
        ganho = (energia_min / CAPACIDADE_BATERIA) * 100

        energia_total += energia_min

        bateria += ganho

        if bateria > limite:
            bateria = limite

        tempo += 1

        custo = calcular_custo(
            energia_total,
            tarifa,
            taxa
        )

        print("-" * 40)
        print(f"Bateria: {bateria:.1f}%")
        print(f"Energia: {energia_total:.2f} kWh")
        print(f"Tempo: {tempo} min")
        print(f"Custo: R$ {custo:.2f}")

        time.sleep(0.2)

    return bateria, energia_total, tempo


def mostrar_recibo(
    bateria,
    energia,
    tempo,
    tarifa,
    taxa
):

    subtotal = energia * tarifa
    total = subtotal + taxa

    print("\n" + "=" * 40)
    print("🧾 RECIBO FINAL")
    print("=" * 40)

    print(f"Tempo: {tempo} min")
    print(f"Energia: {energia:.2f} kWh")
    print(f"Bateria final: {bateria:.1f}%")
    print(f"Tarifa: R$ {tarifa:.2f}/kWh")
    print(f"Taxa: R$ {taxa:.2f}")
    print(f"Subtotal: R$ {subtotal:.2f}")

    print("-" * 40)

    print(f"TOTAL: R$ {total:.2f}")

    print("=" * 40)




print("=" * 50)
print("CHARGEGRID")
print("=" * 50)

premium = input("Usuário premium? (s/n): ").lower()

if premium == "s":
    tarifa = 1.2
    taxa = 2
else:
    tarifa = 1.8
    taxa = 5

print("\nPotências disponíveis:")
print("1 - 22 kW")
print("2 - 50 kW")
print("3 - 150 kW")

opcao = ler_numero("Escolha: ", 1, 3)

if opcao == 1:
    potencia = 22

elif opcao == 2:
    potencia = 50

else:
    potencia = 150

bateria = ler_numero(
    "\nBateria atual (%): ",
    5,
    70
)

limite = ler_numero(
    "Limite desejado (%): ",
    bateria + 1,
    100
)

bateria, energia, tempo = executar_recarga(
    bateria,
    limite,
    potencia,
    tarifa,
    taxa
)

mostrar_recibo(
    bateria,
    energia,
    tempo,
    tarifa,
    taxa
)