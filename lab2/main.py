import yfinance as yf
import pandas as pd
import logging
from datetime import datetime
import os
import time

# PLANEAMENTO E CONFIGURAÇÃO

TICKERS = ['AAPL', 'MSFT', 'TSLA', 'BTC-USD', 'NVDA', 'AMZN']
FILE_NAME = 'monitor_financeiro_v3.csv'
LOG_FILE = 'logs_projeto.log'

# Configuração de Logs
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def formatar_valor_grande(valor):
    """Auxiliar para transformar números gigantes em formatos legíveis (Tarefa 4.3.2)"""
    if valor is None: return "N/A"
    if valor >= 1_000_000_000_000:
        return f"{valor / 1_000_000_000_000:.2f}T"
    elif valor >= 1_000_000_000:
        return f"{valor / 1_000_000_000:.2f}B"
    return str(valor)


def executar_scraping():
    resultados = []

    print(f"--- Iniciando Captura de Dados: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ---")


    # DESENVOLVIMENTO (Navegação e Extração)

    for ticker_symbol in TICKERS:
        try:
            ticker_obj = yf.Ticker(ticker_symbol)

            # Obtendo dados rápidos (Preço, Volume, Máximos/Mínimos)
            f_info = ticker_obj.fast_info
            # Obtendo dados fundamentais (Nome, Market Cap, PE Ratio)
            full_info = ticker_obj.info

            # Validação e Tratamento de Dados
            preco = f_info['last_price']
            if preco is None or preco <= 0:
                raise ValueError("Preço não disponível ou inválido.")

            # Estrutura de Dados Enriquecida
            dados = {
                'ticker': ticker_symbol,
                'nome': full_info.get('longName', 'N/A'),
                'preco_atual': round(preco, 2),
                'moeda': f_info['currency'],
                'variacao_dia_%': round(((preco / f_info['previous_close']) - 1) * 100, 2),
                'max_24h': round(f_info['day_high'], 2),
                'min_24h': round(f_info['day_low'], 2),
                'volume_diario': f_info['last_volume'],
                'market_cap_formatado': formatar_valor_grande(full_info.get('marketCap')),
                'pe_ratio': full_info.get('trailingPE', 'N/A'),
                'data_extracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            resultados.append(dados)
            logging.info(f"Sucesso ao extrair: {ticker_symbol}")
            print(
                f"✅ {ticker_symbol.ljust(8)} | Preço: {str(dados['preco_atual']).ljust(8)} | Var: {dados['variacao_dia_%']}%")

        except Exception as e:
            # Registo de erros em logs
            erro_msg = f"Erro no ticker {ticker_symbol}: {str(e)}"
            logging.error(erro_msg)
            print(f"❌ {erro_msg}")

        time.sleep(1)  # Pequena pausa

    # ARMAZENAMENTO E APRESENTAÇÃO

    if resultados:
        df = pd.DataFrame(resultados)

        # Guardar em CSV
        file_exists = os.path.isfile(FILE_NAME)
        df.to_csv(FILE_NAME, mode='a', index=False, header=not file_exists)

        # Relatório de Estatísticas
        print("\n" + "=" * 40)
        print("       RELATÓRIO DE ESTATÍSTICAS")
        print("=" * 40)
        print(f"Total de ativos analisados: {len(resultados)}")

        # Exemplo de transformação para o Top 3
        top_precos = df.sort_values(by='preco_atual', ascending=False).head(3)
        print("\nTop 3 ativos mais caros nesta extração:")
        for idx, row in top_precos.iterrows():
            print(f"- {row['nome']} ({row['ticker']}): {row['preco_atual']} {row['moeda']}")

        print(f"\nOs dados foram consolidados em: {FILE_NAME}")
        print("=" * 40)
    else:
        print("\nNenhum dado extraído nesta sessão.")


if __name__ == "__main__":
    executar_scraping()