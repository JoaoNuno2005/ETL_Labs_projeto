import pandas as pd
from sqlalchemy import create_engine
import urllib

params = urllib.parse.quote_plus(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=localhost;'
    r'DATABASE=DW_Vendas_Global;'
    r'Trusted_Connection=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

def realizar_etl():
    print("A iniciar o processo ETL...")

    df_produtos = pd.read_csv('produtos.csv')
    df_vendas = pd.read_csv('vendas.csv')
    df_clientes = pd.read_csv('clientes.csv')

    # --- TRANSFORMAÇÃO ---
    # Converter colunas para datetime
    df_vendas['Data'] = pd.to_datetime(df_vendas['Data'])
    df_clientes['DataRegisto'] = pd.to_datetime(df_clientes['DataRegisto'])

    # Criar DimTempo conforme os requisitos de negócio (mês, ano, trimestre)
    datas_unicas = df_vendas['Data'].unique()
    dim_tempo = pd.DataFrame({'IDTempo': datas_unicas})
    dim_tempo['Dia'] = dim_tempo['IDTempo'].dt.day
    dim_tempo['Mes'] = dim_tempo['IDTempo'].dt.month
    dim_tempo['Ano'] = dim_tempo['IDTempo'].dt.year
    dim_tempo['Trimestre'] = dim_tempo['IDTempo'].dt.quarter

    # --- CARGA ---
    print("A carregar dados no SQL Server...")

    # Inserir Dimensões
    df_produtos.to_sql('DimProduto', con=engine, if_exists='append', index=False)

    df_clientes_dw = df_clientes[['IDCliente', 'Nome', 'Cidade', 'Pais', 'DataRegisto']]
    df_clientes_dw.to_sql('DimCliente', con=engine, if_exists='append', index=False)

    dim_tempo.to_sql('DimTempo', con=engine, if_exists='append', index=False)

    # Inserir Fact Table
    fact_vendas = df_vendas[['IDVenda', 'Data', 'IDCliente', 'IDProduto', 'Quantidade', 'Valor']]
    fact_vendas.columns = ['IDVenda', 'IDTempo', 'IDCliente', 'IDProduto', 'Quantidade', 'ValorVendido']
    fact_vendas.to_sql('FactVendas', con=engine, if_exists='append', index=False)

    print("ETL concluído com sucesso!")


if __name__ == "__main__":
    realizar_etl()