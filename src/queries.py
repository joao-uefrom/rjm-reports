from datetime import datetime
from typing import List

from fdb import Cursor

from src.helpers import safe_strip
from src.models import Item, Pedido


def get_pedidos(cur: Cursor, de: datetime, ate: datetime = None) -> List[Pedido]:
    query = """
    SELECT pedido.CODIGO                                                AS codigo,
           cliente.NOME                                                 AS cliente,
           atendente_contato.nome                                       AS atendente,
           entregador.NOME                                              AS entregador,
           CASE
               WHEN pedido.NUMERO = -2 THEN 'Caixa'
               WHEN pedido.NUMERO = -1 THEN 'Balcão'
               WHEN pedido.NUMERO = 0 AND pedido.CODIGOPEDIDOORIGEM = 1 THEN 'Delivery'
               WHEN pedido.NUMERO = 0 AND pedido.CODIGOPEDIDOORIGEM = 6 THEN 'Bot'
               WHEN pedido.NUMERO = 0 AND pedido.CODIGOPEDIDOORIGEM = 7 THEN 'iFood'
               ELSE 'Mesa'
               END                                                      AS tipo_atendimento,
           pedido.DATAABERTURA                                          AS data_abertura,
           pedido.DATAFECHAMENTO                                        AS data_fechamento,
           pedido.VALORENTREGA                                          AS valor_entrega,
           pedido.VALORTOTAL                                            AS valor_total,
           DATEDIFF(SECOND, pedido.DATAABERTURA, pedido.DATAFECHAMENTO) AS tempo_atendimento,
           CASE
               WHEN pedido.CODIGOCONTATOFIADO IS NOT NULL THEN TRUE
               ELSE FALSE
               END                                                      AS eh_fiado
    FROM PEDIDOS pedido
             LEFT JOIN USUARIOS atendente ON pedido.CODIGOUSUARIOCRIADOR = atendente.CODIGO
             LEFT JOIN CONTATOS atendente_contato ON atendente.CODIGOCONTATO = atendente_contato.CODIGO
             LEFT JOIN CONTATOS entregador ON pedido.CODIGOCOLABORADOR = entregador.CODIGO
             LEFT JOIN CONTATOS cliente ON COALESCE(pedido.CODIGOCONTATOFIADO, pedido.CODIGOCONTATOCLIENTE) = cliente.CODIGO
    """

    query_end = "pedido.DATADELETE IS NULL AND pedido.DATAFECHAMENTO IS NOT NULL"

    if ate is not None:
        query += " WHERE CAST(pedido.DATAABERTURA AS DATE) BETWEEN ? AND ? AND " + query_end
        cur.execute(query, (de, ate))
    else:
        query += " WHERE CAST(pedido.DATAABERTURA AS DATE) = ? AND " + query_end
        cur.execute(query, (de,))

    pedidos = []

    for row in cur.fetchall():
        pedidos.append(
            Pedido(
                codigo=row[0],
                cliente=safe_strip(row[1]),
                atendente=safe_strip(row[2]),
                entregador=safe_strip(row[3]),
                tipo_atendimento=safe_strip(row[4]),
                data_abertura=row[5],
                data_fechamento=row[6],
                valor_entrega=row[7],
                valor_total=row[8],
                itens=[],
                tempo_atendimento=row[9],
                eh_fiado=row[10]
            )
        )

    for i in range(len(pedidos)):
        pedidos[i].itens = get_itens(cur, pedidos[i].codigo)

    return pedidos


def get_itens(
        cur: Cursor,
        pedido: int = None,
        de: datetime = None, ate: datetime = None
) -> List[Item]:
    query = """
    SELECT produto_detalhe.CODIGO AS codigo,
       CASE
           WHEN produto_detalhe.CODIGOPRODUTOTAMANHO IS NULL THEN produto.NOME
           ELSE produto_personalizado.DESCRICAO || ' ' || produto.NOME || ' ' || produto_tamanho.DESCRICAO
           END                    AS produto,
       item.QUANTIDADE            AS quantidade,
       produto_detalhe.PRECOVENDA AS valor_unitario,
       item.VALORITEM             AS valor_cobrado,
       item.VALORTOTAL            AS valor_total
    FROM ITENSPEDIDO item
             LEFT JOIN PEDIDOS pedido ON item.CODIGOPEDIDO = pedido.CODIGO
             LEFT JOIN PRODUTODETALHE produto_detalhe ON item.CODIGOPRODUTODETALHE = produto_detalhe.CODIGO
             LEFT JOIN PRODUTOS produto ON produto_detalhe.CODIGOPRODUTO = produto.CODIGO
             LEFT JOIN PRODUTOTAMANHO produto_tamanho ON produto_detalhe.CODIGOPRODUTOTAMANHO = produto_tamanho.CODIGO
             LEFT JOIN PRODUTOPERSONALIZADO produto_personalizado ON produto_tamanho.CODIGOPRODUTOPERSONALIZADO = produto_personalizado.CODIGO 
    """

    query_end = "pedido.DATADELETE IS NULL AND pedido.DATAFECHAMENTO IS NOT NULL AND item.DATADELETE IS NULL AND item.CODIGOPAI IS NULL"

    if pedido is not None:
        query += " WHERE item.CODIGOPEDIDO = ? AND " + query_end
        cur.execute(query, (pedido,))
    elif ate is not None:
        query += " WHERE CAST(pedido.DATAABERTURA AS DATE) BETWEEN ? AND ? AND " + query_end
        cur.execute(query, (de, ate))
    else:
        query += " WHERE CAST(pedido.DATAABERTURA AS DATE) = ? AND " + query_end
        cur.execute(query, (de,))

    itens = []

    for row in cur.fetchall():
        itens.append(
            Item(
                codigo=row[0],
                nome=row[1].strip(),
                quantidade=row[2],
                valor_unitario=row[3],
                valor_cobrado=row[4],
                valor_total=row[5]
            )
        )

    return itens
