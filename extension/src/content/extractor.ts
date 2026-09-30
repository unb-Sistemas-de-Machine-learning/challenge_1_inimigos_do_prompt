export function extractEmailContent(): { subject: string; bodyText: string } | null {
  // Captura o corpo da mensagem no Gmail ou Outlook
  const gmailBody = document.querySelector('.a3s.aiL');
  const outlookBody = document.querySelector('.x_WordSection1') || document.querySelector('[aria-label="Corpo da mensagem"]');
  const bodyElement = gmailBody || outlookBody;
  
  // Captura o assunto
  const gmailSubject = document.querySelector('h2[data-thread-perm-id]') || document.querySelector('.hP');
  const outlookSubject = document.querySelector('.ms-font-weight-semibold.ms-font-color-neutralPrimary');
  const subjectHeader = gmailSubject || outlookSubject;

  if (!bodyElement) return null;

  // Cria um clone em memória para isolar a manipulação e não quebrar a tela do usuário
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = bodyElement.innerHTML;

  // 1. LIMPEZA BÁSICA: Remove lixo estrutural
  tempDiv.querySelectorAll('script, style, iframe, footer, .unsubscribe, .footer').forEach(el => el.remove());

  // 2. REQ-01: ESTRUTURAÇÃO DE BLOCOS E TABELAS
  // Injeta um espaço em branco no final de células e blocos.
  // Garante que "<td>Texto</td><td>Outro</td>" vire "Texto Outro" em vez de "TextoOutro".
  tempDiv.querySelectorAll('td, th, p, div, br, li, h1, h2, h3').forEach(el => {
    el.insertAdjacentText('beforeend', ' ');
  });

  // 3. REQ-01: TRATAMENTO DE IMAGENS E TRACKING PIXELS
  tempDiv.querySelectorAll('img').forEach(img => {
    // Pega a largura para identificar se é um pixel de rastreamento invisível
    const width = img.getAttribute('width') ? parseInt(img.getAttribute('width')!, 10) : img.clientWidth;
    
    // Se for uma imagem real (maior que 10px) e tiver texto alternativo, extraímos o contexto.
    if (width > 10 && img.alt) {
      img.replaceWith(` [Imagem: ${img.alt}] `);
    } else {
      // Caso contrário (é ícone de layout ou rastreador), destruímos.
      img.remove();
    }
  });

  // Extrai o texto final e remove múltiplos espaços seguidos
  let cleanText = tempDiv.innerText.replace(/\s+/g, ' ').trim();

  // 4. REQ-02: TRUNCAMENTO SEGURO
  // O modelo BERT suporta ~512 tokens. 5000 caracteres no frontend é uma margem conservadora
  // para evitar payloads excessivos na API FastAPI.
  const MAX_CHARS = 5000;
  if (cleanText.length > MAX_CHARS) {
    cleanText = cleanText.substring(0, MAX_CHARS) + '... [TRUNCADO]';
  }

  return {
    subject: subjectHeader ? subjectHeader.textContent || '' : '',
    bodyText: cleanText
  };
}