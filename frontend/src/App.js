
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';
import Dashboard from './Dashboard';

// URL DA NUVEM
axios.defaults.baseURL = process.env.REACT_APP_API_URL;

const setupAxiosToken = (token) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

const initialToken = localStorage.getItem('accessToken');
if (initialToken) { setupAxiosToken(initialToken); }

axios.interceptors.response.use((response) => response, async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && originalRequest.url !== '/token/refresh/' && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
         localStorage.removeItem('accessToken'); localStorage.removeItem('refreshToken'); localStorage.removeItem('garcomNome');
         window.location.href = '/';
         return Promise.reject(error);
      }
      try {
        const refreshResponse = await axios.post('/token/refresh/', { refresh: refreshToken });
        const newAccessToken = refreshResponse.data.access;
        localStorage.setItem('accessToken', newAccessToken);
        setupAxiosToken(newAccessToken);
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('accessToken'); localStorage.removeItem('refreshToken'); localStorage.removeItem('garcomNome');
        setupAxiosToken(null);
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

const Carrinho = ({ itens, pedido, garcom, nomeCliente, onNomeClienteChange, finalizarPedido, cancelarPedido, aumentarQtd, diminuirQtd, removerItem }) => {
  if (!pedido) return null;
  const totalPedido = itens.reduce((total, item) => total + (parseFloat(item.preco_total) || 0), 0);

  return (
    <div className="carrinho">
      <div className="carrinho-header">
        <h3>Pedido Atual (Mesa {pedido?.mesa})</h3>
        {garcom && <span className="garcom-nome">Garçom: {garcom}</span>}
      </div>
      <div className="carrinho-identificador-grupo">
        <label htmlFor="nome-cliente-input">Cliente:</label>
        <input id="nome-cliente-input" type="text" value={nomeCliente} onChange={onNomeClienteChange} placeholder="Nome (opcional)" className="carrinho-nome-input" />
      </div>
      {itens.length > 0 ? (
        <>
          <ul>
            {itens.map((item, index) => {
                const precoExibicao = (parseFloat(item.preco_total) || 0).toFixed(2);
                return (
                  <li key={index} className="carrinho-item">
                    <div className="item-info">
                        <span className="item-nome">{item.produto_nome}</span>
                        <span className="item-opcoes">
                            {item.opcoes_nomes?.length > 0 && `(${item.opcoes_nomes.join(', ')})`}
                        </span>
                        {item.adicionais_nomes?.length > 0 && (
                            <span className="item-adicionais">+ {item.adicionais_nomes.join(', ')}</span>
                        )}
                    </div>
                    <div className="item-controles">
                      <button onClick={() => diminuirQtd(index)} className="qtd-button">-</button>
                      <span className="item-quantidade">{item.quantidade}</span>
                      <button onClick={() => aumentarQtd(index)} className="qtd-button">+</button>
                      <span className="item-preco-total">R$ {precoExibicao}</span>
                      <button onClick={() => removerItem(index)} className="remove-item-button">×</button>
                    </div>
                  </li>
                );
            })}
          </ul>
          <div className="carrinho-total"><strong>Total: R$ {totalPedido.toFixed(2)}</strong></div>
          <div className="carrinho-actions">
            <button onClick={finalizarPedido} className="submit-button">Enviar para Cozinha</button>
            <button onClick={cancelarPedido} className="cancel-button">Cancelar</button>
          </div>
        </>
      ) : (<p style={{textAlign: 'center', color: '#888'}}>O carrinho está vazio.</p>)}
    </div>
  );
};

const Login = ({ onLogin }) => { const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const handleSubmit = (event) => { event.preventDefault(); setError(''); onLogin(username, password).catch(() => { setError('Usuário ou senha inválidos.'); }); }; return (<div className="login-container"><form onSubmit={handleSubmit} className="login-form"><h2>Login Garçom</h2>{error && <p className="login-error">{error}</p>}<div className="form-group"><label htmlFor="username">Usuário</label><input type="text" id="username" value={username} onChange={(e) => setUsername(e.target.value)} required /></div><div className="form-group"><label htmlFor="password">Senha</label><input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></div><button type="submit" className="submit-button">Entrar</button></form></div>);};

function App() {
  const [token, setToken] = useState(localStorage.getItem('accessToken'));
  const [garcomNome, setGarcomNome] = useState(localStorage.getItem('garcomNome'));
  const [view, setView] = useState('mesas');
  const [mesas, setMesas] = useState([]);
  const [adicionaisDisponiveis, setAdicionaisDisponiveis] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [nomeClienteInput, setNomeClienteInput] = useState('');
  const [categorias, setCategorias] = useState([]);
  const [produtos, setProdutos] = useState([]);
  const [categoriaSelecionada, setCategoriaSelecionada] = useState(null);
  const [produtoSelecionado, setProdutoSelecionado] = useState(null);
  const [pedidoAtual, setPedidoAtual] = useState(null);
  const [carrinho, setCarrinho] = useState([]);
  const [quantidade, setQuantidade] = useState('1');
  const [observacoes, setObservacoes] = useState('');
  const [opcaoSelecionada, setOpcaoSelecionada] = useState(null);
  const [adicionaisSelecionados, setAdicionaisSelecionados] = useState([]);
  const [opcoesExtrasSelecionadas, setOpcoesExtrasSelecionadas] = useState({});

  const fetchDashboardData = () => { if (token && garcomNome === 'pedro') { setLoadingDashboard(true); setDashboardData(null); axios.get('/dashboard/hoje/').then(response => { setDashboardData(response.data); }).catch(error => { console.error('Erro dashboard', error); setDashboardData(null); }).finally(() => { setLoadingDashboard(false); }); }};
  useEffect(() => { const storedToken = localStorage.getItem('accessToken'); const storedGarcom = localStorage.getItem('garcomNome'); if (storedToken && storedGarcom) { setupAxiosToken(storedToken); setToken(storedToken); setGarcomNome(storedGarcom); } else { setupAxiosToken(null); } }, []);
  useEffect(() => { if (token) { axios.get('/adicionais/').then(response => { setAdicionaisDisponiveis(response.data || []); }).catch(console.error); } }, [token]);
  
  useEffect(() => {
    if (token) {
      if (view === 'mesas') {
        axios.get('/mesas/').then(res => setMesas(res.data || [])).catch(console.error);
        if (garcomNome === 'pedro') {
           axios.get('/relatorios/vendas-diarias/').then(res => setDashboardData({ total_apurado_hoje: res.data.total_apurado_hoje })).catch(console.error);
        } else { setDashboardData(null); }
      } else if (view === 'dashboard' && garcomNome === 'pedro') {
        fetchDashboardData();
      } else if (view === 'cardapio' && pedidoAtual && categorias.length === 0) {
         axios.get('/categorias/').then(res => setCategorias(res.data || [])).catch(console.error);
      }
    }
  }, [token, view, garcomNome, pedidoAtual, categorias.length, refreshTrigger]);

  const handleLogin = async (username, password) => { try { const response = await axios.post('/token/', { username, password }); const { access, refresh, username: nomeDoUsuario } = response.data; localStorage.setItem('accessToken', access); localStorage.setItem('refreshToken', refresh); localStorage.setItem('garcomNome', nomeDoUsuario); setupAxiosToken(access); setGarcomNome(nomeDoUsuario); setToken(access); setView('mesas'); toast.success(`Bem-vindo, ${nomeDoUsuario}!`); } catch (error) { toast.error('Usuário ou senha inválidos.'); throw error; }};
  const handleLogout = () => { localStorage.clear(); setupAxiosToken(null); setToken(null); setGarcomNome(null); setView('mesas'); setPedidoAtual(null); setCarrinho([]); };
  const handleMesaSelect = (mesaId) => { axios.post('/pedidos/', { mesa: mesaId }).then(res => { setPedidoAtual(res.data); setNomeClienteInput(''); axios.get('/categorias/').then(r => setCategorias(r.data || [])); setView('cardapio'); }).catch(() => toast.error('Erro ao iniciar pedido.')); };
  const handleVoltarParaMesas = (cancelar = true) => { if (cancelar && pedidoAtual) { axios.patch(`/pedidos/${pedidoAtual.id}/`, { status: 'cancelado' }).then(() => toast.info("Cancelado")).catch(() => toast.error("Erro cancelar")); } setView('mesas'); setPedidoAtual(null); setCarrinho([]); };

  const atualizarItemNoBackend = async (item, novaQtd) => {
      try {
          await axios.delete(`/itens-pedido/${item.db_id}/`);
          const dadosNovo = { pedido: pedidoAtual.id, produto: item.produto_id, quantidade: novaQtd, observacoes: item.observacoes, opcoes_selecionadas: item.opcoes_ids_lista };
          const res = await axios.post('/itens-pedido/', dadosNovo);
          return { ...item, quantidade: novaQtd, db_id: res.data.id, preco_total: parseFloat(res.data.preco_final) };
      } catch (error) { console.error(error); toast.error("Erro ao atualizar item."); return item; }
  };

  const handleAumentarQtd = async (i) => { const item = carrinho[i]; const novoItem = await atualizarItemNoBackend(item, item.quantidade + 1); const novoCarrinho = [...carrinho]; novoCarrinho[i] = novoItem; setCarrinho(novoCarrinho); };
  const handleDiminuirQtd = async (i) => { const item = carrinho[i]; if (item.quantidade > 1) { const novoItem = await atualizarItemNoBackend(item, item.quantidade - 1); const novoCarrinho = [...carrinho]; novoCarrinho[i] = novoItem; setCarrinho(novoCarrinho); } else { handleRemoverItem(i); } };
  const handleRemoverItem = (i) => { const item = carrinho[i]; if (item.db_id) { axios.delete(`/itens-pedido/${item.db_id}/`).then(() => { const nc = carrinho.filter((_, idx) => idx !== i); setCarrinho(nc); toast.info("Removido."); }).catch(() => toast.error("Erro ao remover.")); } };

  const handleFinalizarPedido = async () => { if (carrinho.length === 0) { toast.warn("Carrinho vazio."); return; } try { await axios.patch(`/pedidos/${pedidoAtual.id}/`, { nome_cliente: nomeClienteInput || '', status: 'em_preparo' }); toast.success(`Pedido #${pedidoAtual.id} enviado!`); handleVoltarParaMesas(false); } catch (error) { console.error(error); toast.error('Erro ao finalizar. Tente novamente.'); } };
  const handleCancelarPedido = () => { if (window.confirm("Tem certeza?")) { handleVoltarParaMesas(); }};
  const handleProdutoClick = (id) => { axios.get(`/produtos/${id}/`).then(res => { setProdutoSelecionado(res.data); setQuantidade('1'); setObservacoes(''); setOpcaoSelecionada(null); setAdicionaisSelecionados([]); setOpcoesExtrasSelecionadas({}); }).catch(() => toast.error("Erro ao carregar produto.")); };
  const handleCategoriaClick = (cat) => { axios.get(`/produtos/?categoria=${cat.id}`).then(res => { setProdutos(res.data || []); setCategoriaSelecionada(cat); setProdutoSelecionado(null); }).catch(() => toast.error("Erro ao carregar produtos.")); };
  const handleVoltarParaCategorias = () => { setCategoriaSelecionada(null); setProdutos([]); setProdutoSelecionado(null); };
  const handleVoltarParaProdutos = () => { setProdutoSelecionado(null); };
  const handleAdicionalChange = (id) => { setAdicionaisSelecionados(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]); };
  const handleOpcaoExtraChange = (gid, vid) => { setOpcoesExtrasSelecionadas(prev => ({ ...prev, [gid]: vid })); };

  const handleAddItemSubmit = (e) => {
    e.preventDefault();
    try {
      const qtdNum = parseInt(quantidade);
      if (isNaN(qtdNum) || qtdNum < 1) { toast.warn("Qtd inválida."); return; }
      
      let precoBase = 0;
      if (produtoSelecionado.preco_fixo) precoBase = parseFloat(produtoSelecionado.preco_fixo);
      else if (opcaoSelecionada) precoBase = parseFloat(opcaoSelecionada.preco);
      else if (produtoSelecionado.precos_opcoes?.length > 0) { toast.warn("Selecione uma opção de preço."); return; }

      const grupos = produtoSelecionado.opcoes_obrigatorias || [];
      for (const g of grupos) { if (!opcoesExtrasSelecionadas[g.id]) { toast.warn(`Selecione: ${g.nome}`); return; } }

      const precoAdd = adicionaisSelecionados.reduce((acc, id) => { const add = adicionaisDisponiveis.find(a => a.id === id); return acc + (add ? parseFloat(add.preco_adicional || 0) : 0); }, 0);
      const unitario = precoBase + precoAdd;
      const totalLocal = qtdNum * unitario;

      const idsExtras = Object.values(opcoesExtrasSelecionadas);
      const nomesExtras = grupos.flatMap(g => (g.valores || [])).filter(v => idsExtras.includes(v.id)).map(v => v.valor);
      const addsInfo = adicionaisSelecionados.map(id => adicionaisDisponiveis.find(a => a.id === id)).filter(Boolean);
      
      const itemData = { pedido: pedidoAtual.id, produto: produtoSelecionado.id, quantidade: qtdNum, observacoes: observacoes, opcoes_selecionadas: [ ...(opcaoSelecionada ? [opcaoSelecionada.valor_opcao.id] : []), ...idsExtras, ...adicionaisSelecionados ] };
      
      axios.post('/itens-pedido/', itemData).then(res => {
            const itemVisual = { db_id: res.data.id, produto_id: produtoSelecionado.id, produto_nome: produtoSelecionado.nome, quantidade: qtdNum, observacoes: observacoes, opcoes_nomes: (opcaoSelecionada ? [opcaoSelecionada.valor_opcao.valor] : []).concat(nomesExtras), adicionais_nomes: addsInfo.map(a => a.valor), adicionais_ids: adicionaisSelecionados, opcoes_ids_lista: itemData.opcoes_selecionadas, preco_unitario: unitario, preco_total: parseFloat(res.data.preco_final || totalLocal) };
            setCarrinho(curr => [...curr, itemVisual]); toast.success("Adicionado!"); handleVoltarParaProdutos();
      }).catch(err => { console.error(err); toast.error("Erro ao salvar item."); });
    } catch (error) { console.error(error); toast.error("Erro no app."); }
  };

  const handleMarcarComoPago = (pid) => { axios.patch(`/pedidos/${pid}/`, { status: 'pago' }).then(() => { toast.success("Pago!"); setRefreshTrigger(p => p + 1); }); };
  const handleImprimirConta = (pid) => { toast.info("Imprimindo..."); axios.patch(`/pedidos/${pid}/`, { status: 'solicitado_conta' }).then(() => { toast.success("Enviado!"); setTimeout(() => setRefreshTrigger(p => p + 1), 2000); }); };



const renderContent = () => {
    if (view === 'mesas') { 
        return (
            <div>
                {garcomNome === 'pedro' && (
                    <>
                        {dashboardData && (
                            <div className="vendas-diarias-container">
                                <h3>Hoje: {(dashboardData.total_apurado_hoje || 0).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</h3>
                            </div>
                        )}
                        <button onClick={() => setView('dashboard')} className="dashboard-button">Financeiro</button>
                    </>
                )}
                <h2>Mesas</h2>
                <div className="mesa-grid">
                    {mesas.map(m => (<div key={m.id} className="mesa-card clickable" onClick={() => handleMesaSelect(m.id)}>Mesa {m.numero}</div>))}
                </div>
            </div>
        ); 
    }
    
    if (view === 'dashboard') return <Dashboard data={dashboardData} loading={loadingDashboard} onVoltar={() => setView('mesas')} onMarcarPago={handleMarcarComoPago} onImprimirConta={handleImprimirConta} />;
    
    if (view === 'cardapio') {
        if (produtoSelecionado) {
            return (
                <div className="produto-detalhe-container">
                    <button onClick={handleVoltarParaProdutos} className="back-button">&larr; Voltar</button>
                    <div className="produto-header">
                        <h2>{produtoSelecionado.nome}</h2>
                        <p>{produtoSelecionado.descricao}</p>
                    </div>

                    <form onSubmit={handleAddItemSubmit} className="item-form">
                        
                        {produtoSelecionado.precos_opcoes?.length > 0 && (
                            <div className="form-section">
                                <label className="section-label">Escolha a Opção:</label>
                                <div className="tamanhos-grid">
                                    {produtoSelecionado.precos_opcoes.map(op => (
                                        <label key={op.valor_opcao.id} className="tamanho-label-wrapper">
                                            <input type="radio" name="preco" value={op.valor_opcao.id} onChange={() => setOpcaoSelecionada(op)} required />
                                            <div className="tamanho-card">
                                                <span className="tamanho-nome">{op.valor_opcao.valor}</span>
                                                <span className="tamanho-preco">R$ {op.preco}</span>
                                            </div>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        {produtoSelecionado.preco_fixo && (!produtoSelecionado.precos_opcoes?.length) && 
                            <div className="preco-fixo-display"><h3>R$ {produtoSelecionado.preco_fixo}</h3></div>
                        }

                        {produtoSelecionado.opcoes_obrigatorias?.map(g => (
                            <div key={g.id} className="form-section">
                                <label className="section-label">{g.nome}:</label>
                                <div className="opcoes-grid">
                                    {g.valores.map(v => {
                                        
                                        let valorBruto = v.preco_adicional || "0";
                                        
                                        let valorFormatado = String(valorBruto).replace(',', '.');

                                        let precoExtra = parseFloat(valorFormatado);

                                        if (isNaN(precoExtra)) precoExtra = 0;
                                        
                                        return (
                                            <label key={v.id} className="opcao-label-wrapper">
                                                <input type="radio" name={`grp-${g.id}`} value={v.id} checked={opcoesExtrasSelecionadas[g.id] === v.id} onChange={() => handleOpcaoExtraChange(g.id, v.id)} />
                                                <div className="opcao-card">
                                                    <strong>{v.valor}</strong>

                                                    {precoExtra > 0.01 && 
                                                        <span style={{
                                                            color: 'var(--brand-green)', 
                                                            fontWeight: 'bold', 
                                                            display:'block', 
                                                            marginTop:'4px',
                                                            fontSize: '0.85rem'
                                                        }}>
                                                            + R$ {precoExtra.toFixed(2).replace('.', ',')}
                                                        </span>
                                                    }
                                                </div>
                                            </label>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}

                        {produtoSelecionado.categoria.permite_adicionais && adicionaisDisponiveis.length > 0 && (
                            <div className="form-section">
                                <label className="section-label">Adicionais:</label>
                                <div className="opcoes-grid">
                                    {adicionaisDisponiveis
                                        .filter(add => {
                                            
                                            const rawName = add.valor || add.nome || '';
                                            const catNome = produtoSelecionado.categoria.nome.trim().toLowerCase();
                                            const addNome = rawName.trim().toUpperCase();

                                            if (catNome.includes('pizza') || catNome.includes('beirute')) {
                                                if (catNome.includes('beirute') && (addNome.includes('CARNE MOÍDA') || addNome.includes('CARNE MOIDA'))) return false;
                                                
                                                return addNome.startsWith('PZ');
                                            }

                                            if (catNome.includes('lanche') || catNome.includes('sandu') || catNome.includes('burguer')) {
                                                return addNome.startsWith('SN');
                                            }

                                            return !addNome.startsWith('PZ') && !addNome.startsWith('SN');
                                        })
                                        .map(add => (
                                        <label key={add.id} className="opcao-label-wrapper">
                                            <input type="checkbox" checked={adicionaisSelecionados.includes(add.id)} onChange={() => handleAdicionalChange(add.id)} />
                                            <div className="opcao-card">
                                                <strong>{add.valor.replace(/^(PZ|SN)\s*-\s*/i, '')}</strong>
                                                <span>+ R$ {add.preco_adicional}</span>
                                            </div>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="form-footer">
                            <div className="form-group qtd-group">
                                <label>Quantidade:</label>
                                <input type="number" value={quantidade} onChange={e => setQuantidade(e.target.value)} className="quantity-input" />
                            </div>
                            <div className="form-group obs-group">
                                <label>Observações:</label>
                                <textarea value={observacoes} onChange={e => setObservacoes(e.target.value)} rows="2" placeholder="Ex: Sem cebola..." />
                            </div>
                            <button type="submit" className="submit-button">Adicionar ao Pedido</button>
                        </div>
                    </form>
                </div>
            );
        }
        if (categoriaSelecionada) return (<div><button onClick={handleVoltarParaCategorias} className="back-button">&larr; Categorias</button><h2>{categoriaSelecionada.nome}</h2><ul>{produtos.map(p => <li key={p.id} onClick={() => handleProdutoClick(p.id)} className="clickable">{p.nome}</li>)}</ul></div>);
        return (<div><button onClick={() => handleVoltarParaMesas()} className="back-button">&larr; Mesas</button><h2>Cardápio</h2><ul>{categorias.map(c => <li key={c.id} onClick={() => handleCategoriaClick(c)} className="clickable">{c.nome}</li>)}</ul></div>);
    }
  };


  if (!token) return (<><ToastContainer theme="dark"/><Login onLogin={handleLogin}/></>);
  return (<div className="App"><ToastContainer theme="dark" position="top-center" /><header className="App-header"><div className="header-top"><h1>DevFlow</h1><button onClick={handleLogout} className="logout-button">Sair</button></div><div className="main-content">{pedidoAtual && view === 'cardapio' && <Carrinho itens={carrinho} pedido={pedidoAtual} garcom={garcomNome} nomeCliente={nomeClienteInput} onNomeClienteChange={e => setNomeClienteInput(e.target.value)} finalizarPedido={handleFinalizarPedido} cancelarPedido={handleCancelarPedido} aumentarQtd={handleAumentarQtd} diminuirQtd={handleDiminuirQtd} removerItem={handleRemoverItem} />}{renderContent()}</div></header></div>);
}

export default App;