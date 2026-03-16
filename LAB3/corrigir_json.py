import json


def processar_produtos(caminho_json, caminho_log):
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            produtos = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Erro ao abrir ficheiro: {e}")
        return

    produtos_validados = []
    erros = []

    chaves_essenciais = ['id', 'nome', 'preco']

    for i, prod in enumerate(produtos):
        problemas_no_produto = []

        # i) Verificar Chaves Essenciais
        em_falta = [chave for chave in chaves_essenciais if chave not in prod]
        if em_falta:
            erros.append(f"Produto índice {i}: Faltam chaves essenciais {em_falta}")
            continue  # Se faltam chaves críticas, ignoramos o objeto

        # ii) Validar e Corrigir Tipos

        # 1. Validar Preço (String para Float)
        preco_original = prod['preco']
        try:
            if isinstance(preco_original, str):
                # Remove símbolos de moeda ou espaços se existirem
                preco_limpo = preco_original.replace('€', '').replace('$', '').strip()
                prod['preco'] = float(preco_limpo)
            elif not isinstance(preco_original, (int, float)):
                raise ValueError
        except (ValueError, TypeError):
            problemas_no_produto.append(f"Preço inválido: '{preco_original}' (convertido para 0.0)")
            prod['preco'] = 0.0

        # 2. Validar Variantes (String para Array)
        if 'variantes' in prod:
            variantes = prod['variantes']
            if isinstance(variantes, str):
                # Se for string, transformamos em lista
                prod['variantes'] = [v.strip() for v in variantes.split(',')]
            elif not isinstance(variantes, list):
                problemas_no_produto.append(f"Variantes não é lista nem string. Reset para lista vazia.")
                prod['variantes'] = []
        else:
            # Caso não exista, podemos normalizar criando a chave como lista vazia
            prod['variantes'] = []

        # 3. Tratar Categoria (Se não existir, definir "Geral")
        if 'categoria' not in prod or not prod['categoria']:
            prod['categoria'] = "Geral"

        # Logar problemas encontrados neste objeto específico
        if problemas_no_produto:
            erros.append(f"Produto ID {prod.get('id')}: {'; '.join(problemas_no_produto)}")

        produtos_validados.append(prod)

    # Gravar o Log de Erros/Avisos
    with open(caminho_log, 'w', encoding='utf-8') as f_log:
        f_log.write("\n".join(erros))

    return produtos_validados


# Execução
produtos_limpos = processar_produtos('produtos.json', 'erros_produtos.log')

# Guardar o resultado num novo JSON limpo
if produtos_limpos:
    with open('produtos_limpo.json', 'w', encoding='utf-8') as f_out:
        json.dump(produtos_limpos, f_out, indent=4, ensure_ascii=False)
    print("Processamento JSON concluído!")