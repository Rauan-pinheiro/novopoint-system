
import React from 'react';

const formatarDataHora = (dataHoraISO) => {
  if (!dataHoraISO) return '';
  const data = new Date(dataHoraISO);
  return data.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const formatarMoeda = (valor) => {
  return (valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const Dashboard = ({ data, loading, onVoltar, onMarcarPago, onImprimirConta }) => {

  const renderListaPedidos = (titulo, pedidos, showBotoes = false) => (
    <div className="dashboard-section">
      <h3>{titulo} ({(Array.isArray(pedidos) ? pedidos.length : 0)})</h3>
      {!Array.isArray(pedidos) || pedidos.length === 0 ? <p>Nenhum pedido encontrado.</p> : (
        <ul className="dashboard-list">
          {pedidos.map(pedido => (
            <li key={pedido.id} className="dashboard-pedido">
              <div className="pedido-header">
                <strong>{pedido.mesa} {pedido.nome_cliente && `(${pedido.nome_cliente})`}</strong>
                <span>Garçom: {pedido.garcom || 'N/A'}</span>
                <span>{formatarDataHora(pedido.data_hora)}</span>
                {pedido.total_pedido !== null && pedido.total_pedido !== undefined && <span>Total: {formatarMoeda(parseFloat(pedido.total_pedido))}</span>}
              </div>
              
              <ul className="pedido-itens">
                {Array.isArray(pedido.itens) && pedido.itens.map((item, index) => (
                  <li key={index} className="dashboard-item-detalhe">
                    <div className="item-detalhe-info">
                      <span>{item.quantidade}x {item.produto}</span>
                      {item.opcoes_nomes && item.opcoes_nomes.length > 0 && <span className="item-detalhe-opcoes">({item.opcoes_nomes.join(', ')})</span>}
                      {item.adicionais_nomes && item.adicionais_nomes.length > 0 && <span className="item-detalhe-adicionais">+ {item.adicionais_nomes.join(', ')}</span>}
                      {item.observacoes && <span className="item-observacao"> - Obs: {item.observacoes}</span>}
                    </div>
                    <span className="item-detalhe-preco">
                      {formatarMoeda(parseFloat(item.preco_final))}
                    </span>
                  </li>
                ))}
              </ul>

              {showBotoes && (
                <div className="dashboard-pedido-actions">
                  <button
                    onClick={() => onImprimirConta(pedido.id)}
                    className="imprimir-conta-button"
                  >
                    Imprimir Conta
                  </button>
                  <button
                    onClick={() => onMarcarPago(pedido.id)}
                    className="marcar-pago-button"
                  >
                    Confirmar Pagamento
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );

  return (
    <div className="dashboard-container">
      <button onClick={onVoltar} className="back-button">&larr; Voltar para Mesas</button>
      <h2>Dashboard Financeiro</h2>

      {loading || !data ? (
          <p>Carregando dados do dashboard...</p>
      ) : (
          <>

            <div className="dashboard-summary-grid">
              <div className="dashboard-summary vendas-diarias-container">
                <h3>Faturamento Hoje (desde 2h AM)</h3>
                <p>{formatarMoeda(data.total_apurado_hoje)}</p>
              </div>
              <div className="dashboard-summary vendas-mes-container">
                <h3>Faturamento Mês</h3>
                <p>{formatarMoeda(data.total_apurado_mes)}</p>
              </div>
              <div className="dashboard-summary vendas-ano-container">
                <h3>Faturamento Ano</h3>
                <p>{formatarMoeda(data.total_apurado_ano)}</p>
              </div>
            </div>

            <div className="dashboard-lists-grid">
                {renderListaPedidos("Pedidos Em Aberto", data.pedidos_em_aberto, true)}
                
                {renderListaPedidos("Pedidos Pagos", data.pedidos_pagos)}
                
                {renderListaPedidos("Pedidos Cancelados", data.pedidos_cancelados)}
            </div>
          </>
      )}
    </div>
  );
};

export default Dashboard;