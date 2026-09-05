import React, { useState } from 'react'

export default function ContentApp() {
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      // Pega todo o texto visível no email aberto (o Gmail usa a classe '.ii.gt')
      const emailBody = document.querySelector('.ii.gt')?.textContent || "Texto não encontrado."
      
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: emailBody })
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      console.error(e)
      setResult({ label: 'Erro' })
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <button 
        onClick={handleAnalyze}
        disabled={analyzing}
        style={{ 
          padding: '8px 16px', 
          backgroundColor: '#db4437', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        {analyzing ? 'Analisando...' : 'Detector de Hype'}
      </button>
      
      {result && (
        <span style={{ backgroundColor: '#f1f3f4', padding: '6px 12px', borderRadius: '4px', color: '#202124' }}>
          <strong>Score:</strong> {result.sensationalism_score} ({result.label})
        </span>
      )}
    </div>
  )
}