export function extractEmailContent(): { subject: string; bodyText: string } | null {
  // Seletor típico de corpo de mensagem no Gmail e Outlook
  const gmailBody = document.querySelector('.a3s.aiL');
  const outlookBody = document.querySelector('.x_WordSection1') || document.querySelector('[aria-label="Corpo da mensagem"]');
  
  const bodyElement = gmailBody || outlookBody;
  
  const gmailSubject = document.querySelector('h2[data-thread-perm-id]') || document.querySelector('.hP');
  const outlookSubject = document.querySelector('.ms-font-weight-semibold.ms-font-color-neutralPrimary');
  
  const subjectHeader = gmailSubject || outlookSubject;

  if (!bodyElement) return null;

  const rawHtml = bodyElement.innerHTML;
  
  // Cria elemento temporário para isolar apenas o texto sem tags de estilo e scripts
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = rawHtml;

  // Remove propagandas conhecidas e elementos de rodapé irrelevantes
  tempDiv.querySelectorAll('script, style, iframe, footer, .unsubscribe, .footer').forEach(el => el.remove());

  const cleanText = tempDiv.innerText.replace(/\s+/g, ' ').trim();

  return {
    subject: subjectHeader ? subjectHeader.textContent || '' : '',
    bodyText: cleanText
  };
}
