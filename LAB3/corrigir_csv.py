import csv
import re


def processar_clientes(nome_input, nome_log):
    colunas_esperadas = 4  # ID, Nome, Idade, Salario

    with open(nome_input, 'r', encoding='utf-8') as f_in, \
         open(nome_log, 'w', encoding='utf-8') as f_log:

        cabecalho = f_in.readline()
        f_log.write(f"LOG DE ERROS - FICHEIRO: {nome_input}\n")
        f_log.write("-" * 50 + "\n")

        # Processar linha a linha
        for i, linha in enumerate(f_in, start=2):
            linha_str = linha.strip()
            if not linha_str:
                continue

            erros_linha = []

            # i) Detetar problemas de formatação

            # 1. Verificar delimitador inconsistente (ponto-e-vírgula)
            if ';' in linha_str and ',' not in linha_str:
                erros_linha.append("Uso de ';' como delimitador em vez de ','")
                campos = linha_str.split(';')
            else:
                # O csv.reader lida corretamente com "Nome, Sobrenome" entre aspas
                leitor = csv.reader([linha_str])
                try:
                    campos = next(leitor)
                except csv.Error:
                    erros_linha.append("Erro crítico na estrutura de aspas/vírgulas")
                    campos = []

            # 2. Verificar número de colunas (a mais ou a menos)
            if len(campos) != colunas_esperadas:
                erros_linha.append(f"Número de colunas inválido: {len(campos)} (esperado {colunas_esperadas})")

            # 3. Detetar campos vazios ou caracteres estranhos
            if len(campos) >= 1:
                # Verificar Idade (deve ser apenas números)
                if len(campos) > 2:
                    idade = campos[2].strip()
                    if not idade:
                        erros_linha.append("Campo 'Idade' vazio")
                    elif not idade.isdigit():
                        erros_linha.append(f"Caracter estranho na Idade: '{idade}'")

                # Verificar Salário (deve ser numérico/decimal)
                if len(campos) > 3:
                    salario = campos[3].strip()
                    if not salario:
                        erros_linha.append("Campo 'Salario' vazio")
                    else:
                        try:
                            float(salario.replace(',', '.'))
                        except ValueError:
                            erros_linha.append(f"Caracter estranho no Salário: '{salario}'")

            # ii) Logar cada linha problemática
            if erros_linha:
                f_log.write(f"LINHA {i}: {linha_str}\n")
                for erro in erros_linha:
                    f_log.write(f"  -> ERRO: {erro}\n")
                f_log.write("\n")

    print(f"Processamento concluído. Verifique o ficheiro '{nome_log}' para detalhes.")


# Execução
# processar_clientes('clientes.csv', 'erros.log')

def processar_e_limpar_clientes(nome_input, nome_limpo, nome_log):
    colunas_esperadas = ["ID", "Nome", "Idade", "Salario"]

    with open(nome_input, 'r', encoding='utf-8') as f_in, \
            open(nome_limpo, 'w', encoding='utf-8', newline='') as f_out, \
            open(nome_log, 'w', encoding='utf-8') as f_log:

        escritor = csv.writer(f_out, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        # Escrever o cabeçalho normalizado
        escritor.writerow(colunas_esperadas)

        # Saltar o cabeçalho original
        f_in.readline()

        for i, linha in enumerate(f_in, start=2):
            linha_raw = linha.strip()
            if not linha_raw: continue

            # Tratamento de delimitador inconsistente para leitura
            if ';' in linha_raw and ',' not in linha_raw:
                campos = [c.strip() for c in linha_raw.split(';')]
            else:
                leitor_temp = csv.reader([linha_raw])
                campos = [c.strip() for c in next(leitor_temp)]

            erros = []

            # iii) Correção e Normalização

            # Validar estrutura básica antes de limpar
            if len(campos) < 4:
                erros.append(f"Linha incompleta (colunas: {len(campos)})")
                # Preencher colunas em falta com strings vazias para evitar erro de índice
                campos.extend([''] * (4 - len(campos)))
            elif len(campos) > 4:
                erros.append(f"Colunas extra removidas (total: {len(campos)})")
                campos = campos[:4]

            # Limpeza específica por campo
            id_limpo = campos[0] if campos[0] else "0"

            # Nome: se vazio -> "N/A"
            nome_limpo_val = campos[1] if campos[1] else "N/A"

            # Idade: se vazio ou inválido -> "0"
            idade_val = campos[2]
            if not idade_val:
                idade_limpo = "0"
            elif not idade_val.isdigit():
                erros.append(f"Idade inválida '{idade_val}' convertida para 0")
                idade_limpo = "0"
            else:
                idade_limpo = idade_val

            # Salário: se vazio ou inválido -> 0
            salario_val = campos[3].replace(',', '.')
            try:
                salario_limpo = float(salario_val) if salario_val else 0.0
            except ValueError:
                erros.append(f"Salário inválido '{salario_val}' convertido para 0.0")
                salario_limpo = 0.0

            # iv) Criar ficheiro CSV limpo

            # Escrevemos a linha processada no ficheiro final
            linha_processada = [id_limpo, nome_limpo_val, idade_limpo, f"{salario_limpo:.2f}"]
            escritor.writerow(linha_processada)

            # Logar se houve algum preenchimento automático ou erro
            if erros:
                f_log.write(f"LINHA {i}: {linha_raw}\n")
                for e in erros:
                    f_log.write(f"  - Corrigido: {e}\n")
                f_log.write(f"  - Resultado: {linha_processada}\n\n")

    print(f"Sucesso! Ficheiro '{nome_limpo}' gerado e erros registados em '{nome_log}'.")


# Executar
processar_e_limpar_clientes('clientes.csv', 'clientes_limpo.csv', 'erros_limpeza.log')