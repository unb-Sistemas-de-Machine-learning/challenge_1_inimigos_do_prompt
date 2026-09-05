import { createRoot } from 'react-dom/client'
import ContentApp from './ContentApp'

function injectApp() {
  // Se o botão já existe, não faz nada
  if (document.getElementById('inimigos-prompt-root')) return

  console.log("Inimigos do Prompt: Injetando script no Gmail...")

  // Cria o container do app
  const container = document.createElement('div')
  container.id = 'inimigos-prompt-root'
  
  // Estilo para forçar o botão a aparecer flutuando no canto inferior direito
  container.style.position = 'fixed'
  container.style.bottom = '30px'
  container.style.right = '30px'
  container.style.zIndex = '99999'

  // Anexa direto no body da página (não tem como falhar)
  document.body.appendChild(container)

  // Renderiza o botão do React
  const root = createRoot(container)
  root.render(<ContentApp />)
}

// Tenta injetar assim que o script carregar
injectApp()

// Observa mudanças na página caso o Gmail limpe o nosso botão
const observer = new MutationObserver(() => {
  injectApp()
})
observer.observe(document.body, { childList: true, subtree: true })