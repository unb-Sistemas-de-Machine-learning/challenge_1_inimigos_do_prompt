import { useState } from 'react'

function App() {
  const [resultado, setResultado] = useState<any>(null)

  const testarAPI = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: "URGENTE! Uma notícia bombástica que vai destruir o mundo tech!"
        })
      })
      const data = await res.json()
      setResultado(data)
    } catch (erro) {
      console.error("Erro ao conectar com a API:", erro)
      setResultado({ label: "Erro de conexão. A API está rodando?" })
    }
  }

  return (
    <div style={{ padding: '15px', width: '320px', fontFamily: 'sans-serif' }}>
      <h2 style={{ fontSize: '18px', marginBottom: '10px' }}>Inimigos do Prompt</h2>
      <button 
        onClick={testarAPI}
        style={{ padding: '8px 12px', cursor: 'pointer', backgroundColor: '#646cff', color: 'white', border: 'none', borderRadius: '4px' }}
      >
        Testar Inferência
      </button>
      
      {resultado && (
        <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
          <p style={{ margin: '0 0 5px 0' }}><strong>Score:</strong> {resultado.sensationalism_score}</p>
          <p style={{ margin: '0' }}><strong>Label:</strong> {resultado.label}</p>
        </div>
      )}
    </div>
  )
}

export default App