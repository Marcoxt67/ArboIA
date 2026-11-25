/* ARborIA — comportamentos compartilhados da interface */

/* Preferências ficam só neste navegador; se o armazenamento estiver
   bloqueado (aba privada, por exemplo) o app continua funcionando. */
const prefs = {
  ler(chave, padrao) {
    try { const v = window.localStorage.getItem(chave); return v === null ? padrao : v; }
    catch (e) { return padrao; }
  },
  gravar(chave, valor) {
    try { window.localStorage.setItem(chave, valor); } catch (e) { /* ignora */ }
  },
};

document.addEventListener('DOMContentLoaded', () => {
  const caminho = window.location.pathname;

  /* 1. Destaca o link atual no menu lateral. */
  document.querySelectorAll('.menu-links [data-nav]').forEach((link) => {
    const alvo = link.getAttribute('data-nav');
    const ativo = alvo === '/' ? caminho === '/' : caminho.startsWith(alvo);
    if (ativo) link.classList.add('ativo');
  });

  /* 2. Entrada suave dos cartões. */
  if ('IntersectionObserver' in window) {
    const observador = new IntersectionObserver((entradas) => {
      entradas.forEach((entrada) => {
        if (entrada.isIntersecting) {
          entrada.target.classList.add('visivel');
          observador.unobserve(entrada.target);
        }
      });
    }, { threshold: 0.05 });
    document.querySelectorAll('.fade-up').forEach((el) => observador.observe(el));
  } else {
    document.querySelectorAll('.fade-up').forEach((el) => el.classList.add('visivel'));
  }

  /* 3. Abas de fichas (Limites / Problemáticas / Soluções). */
  const abas = Array.from(document.querySelectorAll('.aba-ficha'));
  const tiles = Array.from(document.querySelectorAll('.tile[data-categoria]'));
  const mostrarAba = (nome) => {
    abas.forEach((a) => {
      const ativa = a.dataset.aba === nome;
      a.classList.toggle('ativa', ativa);
      a.setAttribute('aria-pressed', ativa ? 'true' : 'false');
    });
    tiles.forEach((t) => t.classList.toggle('oculto', t.dataset.categoria !== nome));
  };
  abas.forEach((a) => a.addEventListener('click', () => mostrarAba(a.dataset.aba)));
  if (abas.length) mostrarAba(abas[0].dataset.aba);

  /* 4. Seleção de fichas e bandeja "Sua Combinação". */
  const contador = document.getElementById('selecao-contador');
  const campo = document.getElementById('fichas-selecionadas');
  const lista = document.getElementById('combo-lista');
  const botaoAnalisar = document.getElementById('botao-analisar');
  const selecionadas = []; // preserva a ordem em que foram escolhidas

  const desenharBandeja = () => {
    if (contador) contador.textContent = selecionadas.length;
    if (campo) campo.value = selecionadas.map((t) => t.dataset.ficha).join('|');
    if (botaoAnalisar) {
      botaoAnalisar.disabled = selecionadas.length === 0;
      botaoAnalisar.classList.toggle('desativado', selecionadas.length === 0);
    }
    if (!lista) return;
    lista.innerHTML = '';
    if (!selecionadas.length) {
      const vazio = document.createElement('span');
      vazio.className = 'combo-vazio';
      vazio.textContent = 'Toque nas fichas para montar sua combinação';
      lista.appendChild(vazio);
      return;
    }
    selecionadas.forEach((tile) => {
      const mini = document.createElement('span');
      mini.className = 'mini tile-' + tile.dataset.categoria;
      mini.title = tile.dataset.curto || tile.dataset.ficha;
      mini.textContent = tile.dataset.icone || '';
      const tirar = document.createElement('button');
      tirar.type = 'button';
      tirar.className = 'tirar';
      tirar.setAttribute('aria-label', 'Remover ' + (tile.dataset.curto || tile.dataset.ficha));
      tirar.innerHTML = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
      tirar.addEventListener('click', () => alternarFicha(tile));
      mini.appendChild(tirar);
      lista.appendChild(mini);
    });
    lista.scrollLeft = lista.scrollWidth;
  };

  function alternarFicha(tile) {
    const posicao = selecionadas.indexOf(tile);
    if (posicao >= 0) {
      selecionadas.splice(posicao, 1);
      tile.classList.remove('selecionada');
      tile.setAttribute('aria-pressed', 'false');
    } else {
      selecionadas.push(tile);
      tile.classList.add('selecionada');
      tile.setAttribute('aria-pressed', 'true');
    }
    desenharBandeja();
  }

  tiles.filter((t) => t.dataset.ficha).forEach((tile) => {
    tile.setAttribute('role', 'button');
    tile.setAttribute('tabindex', '0');
    tile.setAttribute('aria-pressed', 'false');
    tile.addEventListener('click', () => alternarFicha(tile));
    tile.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); alternarFicha(tile); }
    });
  });
  desenharBandeja();

  /* 5. Os 9 Limites: cartões e seletor controlam o mesmo painel. */
  const seletor = document.getElementById('seletor-limite');
  const paineis = Array.from(document.querySelectorAll('.painel-limite'));
  const cartoesLimite = Array.from(document.querySelectorAll('.tile[data-limite]'));
  const bolinha = document.getElementById('seletor-bolinha');
  const mostrarLimite = (id, rolar) => {
    paineis.forEach((p) => p.classList.toggle('ativo', p.dataset.limite === id));
    cartoesLimite.forEach((c) => c.classList.toggle('ativo-limite', c.dataset.limite === id));
    if (seletor && seletor.value !== id) seletor.value = id;
    const cartao = cartoesLimite.find((c) => c.dataset.limite === id);
    if (bolinha && cartao) bolinha.textContent = cartao.dataset.icone || '';
    if (rolar && seletor) seletor.closest('.seletor-limite').scrollIntoView({ behavior: 'smooth', block: 'center' });
  };
  if (seletor) {
    seletor.addEventListener('change', () => mostrarLimite(seletor.value, false));
    cartoesLimite.forEach((c) => {
      c.setAttribute('role', 'button');
      c.setAttribute('tabindex', '0');
      c.addEventListener('click', () => mostrarLimite(c.dataset.limite, true));
      c.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); mostrarLimite(c.dataset.limite, true); }
      });
    });
    mostrarLimite(seletor.value, false);
  }

  /* 6. Câmera e galeria (foto das fichas). */
  const entradaCamera = document.getElementById('foto-camera');
  const entradaFoto = document.getElementById('imagem');
  const previa = document.getElementById('preview-imagem');
  const visor = document.getElementById('visor');
  const botaoEnviar = document.getElementById('botao-enviar-foto');

  const mostrarPrevia = (arquivo) => {
    if (!arquivo) return;
    if (previa) {
      previa.src = URL.createObjectURL(arquivo);
      previa.classList.remove('d-none');
    }
    const wrapper = document.getElementById('preview-wrapper');
    if (wrapper) wrapper.classList.remove('d-none');
    if (visor) visor.classList.remove('vazio');
    const dica = document.getElementById('visor-dica');
    if (dica) dica.classList.add('d-none');
    if (botaoEnviar) { botaoEnviar.disabled = false; botaoEnviar.classList.remove('desativado'); }
  };

  document.querySelectorAll('.abrir-camera').forEach((botao) => {
    botao.addEventListener('click', () => { if (entradaCamera) entradaCamera.click(); });
  });
  document.querySelectorAll('.abrir-galeria').forEach((botao) => {
    botao.addEventListener('click', () => { if (entradaFoto) entradaFoto.click(); });
  });
  if (entradaFoto) {
    entradaFoto.addEventListener('change', () => mostrarPrevia(entradaFoto.files && entradaFoto.files[0]));
  }
  if (entradaCamera) {
    entradaCamera.addEventListener('change', () => {
      const arquivo = entradaCamera.files && entradaCamera.files[0];
      if (!arquivo) return;
      // A câmera usa um campo separado; copiamos o arquivo para o campo enviado ao servidor.
      if (entradaFoto && typeof DataTransfer !== 'undefined') {
        const dados = new DataTransfer();
        dados.items.add(arquivo);
        entradaFoto.files = dados.files;
      }
      mostrarPrevia(arquivo);
    });
  }

  /* 7. Configurações: tema e avisos. */
  const chaveTema = document.getElementById('alternar-tema');
  if (chaveTema) {
    chaveTema.checked = document.documentElement.dataset.tema !== 'claro';
    chaveTema.addEventListener('change', () => {
      const escuro = chaveTema.checked;
      document.documentElement.dataset.tema = escuro ? 'escuro' : 'claro';
      document.documentElement.dataset.bsTheme = escuro ? 'dark' : 'light';
      prefs.gravar('arboia-tema', escuro ? 'escuro' : 'claro');
    });
  }
  const chaveAvisos = document.getElementById('alternar-avisos');
  if (chaveAvisos) {
    chaveAvisos.checked = prefs.ler('arboia-avisos', 'on') !== 'off';
    chaveAvisos.addEventListener('change', () => prefs.gravar('arboia-avisos', chaveAvisos.checked ? 'on' : 'off'));
  }

  /* 8. Tela "Parabéns! Você subiu de nível". */
  const overlay = document.getElementById('nivel-overlay');
  if (overlay) {
    if (prefs.ler('arboia-avisos', 'on') === 'off') {
      overlay.remove();
    } else {
      overlay.classList.add('aberto');
      const reduzir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (!reduzir) {
        const cores = ['#ffcf3f', '#3be85f', '#22d3ee', '#ef4444', '#8b5cf6', '#ffffff'];
        for (let i = 0; i < 46; i++) {
          const p = document.createElement('span');
          p.className = 'confete';
          p.style.left = Math.random() * 100 + '%';
          p.style.background = cores[i % cores.length];
          p.style.animationDuration = 3 + Math.random() * 3.5 + 's';
          p.style.animationDelay = Math.random() * 3 + 's';
          overlay.appendChild(p);
        }
      }
      const fechar = (e) => {
        overlay.classList.remove('aberto');
        if (e && e.currentTarget && e.currentTarget.tagName === 'A' && caminho !== '/') return; // segue o link
        if (e) e.preventDefault();
      };
      const botaoFechar = document.getElementById('nivel-fechar');
      if (botaoFechar) botaoFechar.addEventListener('click', fechar);
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') overlay.classList.remove('aberto'); });
      if (botaoFechar) botaoFechar.focus();
    }
  }
});
