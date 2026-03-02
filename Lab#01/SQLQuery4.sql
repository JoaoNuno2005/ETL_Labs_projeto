USE master;
GO

--Forçar o fecho de todas as conexões e apagar a DB
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'DW_Vendas_Global')
BEGIN
    ALTER DATABASE DW_Vendas_Global SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE DW_Vendas_Global;
END
GO

--Criar a DB novamente
CREATE DATABASE DW_Vendas_Global;
GO

USE DW_Vendas_Global;
GO

-- Criar a estrutura dimensional 
CREATE TABLE DimProduto (
    IDProduto INT PRIMARY KEY,
    NomeProduto VARCHAR(255),
    Categoria VARCHAR(100),
    Preco DECIMAL(10, 2)
); [cite: 33, 38]

CREATE TABLE DimCliente (
    IDCliente INT PRIMARY KEY,
    Nome VARCHAR(255),
    Cidade VARCHAR(100),
    Pais VARCHAR(100),
    DataRegisto DATE
); [cite: 33, 38]

CREATE TABLE DimTempo (
    IDTempo DATE PRIMARY KEY,
    Dia INT,
    Mes INT,
    Ano INT,
    Trimestre INT
); [cite: 33, 95]

CREATE TABLE FactVendas (
    IDVenda INT PRIMARY KEY,
    IDTempo DATE,
    IDCliente INT,
    IDProduto INT,
    Quantidade INT,
    ValorVendido DECIMAL(10, 2),
    CONSTRAINT FK_Tempo FOREIGN KEY (IDTempo) REFERENCES DimTempo(IDTempo),
    CONSTRAINT FK_Cliente FOREIGN KEY (IDCliente) REFERENCES DimCliente(IDCliente),
    CONSTRAINT FK_Produto FOREIGN KEY (IDProduto) REFERENCES DimProduto(IDProduto)
); [cite: 31, 36, 48]
GO