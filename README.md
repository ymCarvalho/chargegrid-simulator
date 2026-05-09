Integrantes: 

João Pedro Santos Ferreira - Rm: 569202; 

Maria Beatriz Braga de Lima - Rm: 570501; 

Ulysses Gomes Soares de Souza – RM: 573826; 

Yasmin Cristina Carvalho Mayer – RM: 573964. 


O projeto possui:
    um algoritmo principal de recarga - algorithm.py
    uma versão com interface gráfica utilizando Tkinter - simulator.py

ChargeGrid - Sistema simples em Python que simula uma estação de recarga para veículos elétricos.

Objetivo - O projeto simula o funcionamento de uma estação de recarga elétrica, permitindo acompanhar:
nível da bateria
energia transferda
tempo de recarga
custo total da sessão

Fluxo do Sistema
O usuário informa:
se possui plano premium
a potência do carregador
a bateria atual
o limite desejado de carga

O sistema:
inicia a simulação
mostra o progresso da recarga
calcula os custos
exibe um recibo final

Tipos de Usuário
Tipo Tarifa Taxa
Comum R$ 1,80/kWh R$ 5,00
Premium R$ 1,20/kWh R$ 2,00

Potências Disponíveis
22 kW
50 kW
150 kW

Eficiência da Recarga
Quando a bateria ultrapassa 80%, a velocidade da recarga diminui pela metade:
eficiencia = 1 if bateria < 80 else 0.5
Isso simula o comportamento real de baterias elétricas.

Estrutura do Código
Funções Principais:
ler_numero() -> Valida entradas numéricas do usuário.
calcular_custo() -> Calcula o custo parcial da recarga.
executar_recarga() -> Executa toda a simulação da recarga minuto a minuto.
mostrar_recibo()-> Exibe o resumo final da sessão.

Projeto desenvolvido para fins acadêmicos e aprendizado em Python.
