import os
import pandas as pd
import numpy as np

def generate_sample_dataset(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Amostras de texto sóbrias (Jornalismo factual)
    sobrio_texts = [
        "A empresa de tecnologia anunciou o balanço financeiro do terceiro trimestre com um crescimento de 5% na receita.",
        "Desenvolvedores lançaram a versão 2.4 da biblioteca de código aberto com correções de segurança e otimização de memória.",
        "Estudo publicado na revista científica analisa o impacto do uso de redes de fibra óptica em cidades de médio porte.",
        "A nova atualização do sistema operacional inclui suporte para novos processadores e melhorias na vida útil da bateria.",
        "Pesquisadores da universidade apresentaram um novo algoritmo para compressão de imagens sem perda significativa de qualidade.",
        "Conferência de tecnologia reunirá especialistas para discutir regulamentação de dados e privacidade em sistemas de nuvem.",
        "Relatório anual indica aumento nas contratações de profissionais de segurança da informação no setor bancário.",
        "Startup de biotecnologia capta investimento para expandir testes clínicos de software de triagem diagnóstica.",
        "Consórcio internacional de telecomunicações define novos padrões para infraestrutura de antenas 5G.",
        "Fabricante de chips de memória anuncia construção de nova fábrica para suprir a demanda da indústria automotiva.",
        "Atualização de aplicativo corrige falha de autenticação detectada por pesquisadores independentes.",
        "Serviço de armazenamento em nuvem altera termos de serviço e reduz limite de armazenamento gratuito.",
        "Empresa de tecnologia firma parceria com universidade para incentivar formação de novos programadores.",
        "Linguagem de programação lança versão estável com novos recursos de sintaxe e desempenho aprimorado.",
        "Estudo de mercado prevê crescimento sustentável na venda de computadores corporativos nos próximos anos."
    ]
    
    # Amostras de texto sensacionalistas (Hype / Clickbait / Promessas exageradas)
    sensacionalista_texts = [
        "REVOLUCIONÁRIO! Esta nova Inteligência Artificial VAI DESTRUIR todos os empregos de programação amanhã!",
        "Segredo REVELADO: Como a nova tecnologia de criptomoedas vai deixar qualquer um milionário em 3 dias!",
        "INACREDITÁVEL! Cientistas criam processador infinito que NUNCA precisa de energia elétrica!",
        "O FIM DA APPLE? Esta empresa chinesa lançou um celular secreto que DESTRÓI o iPhone!",
        "BOMBA no mundo da tecnologia! O algoritmo proibido que as Big Techs NÃO QUEREM que você conheça!",
        "URGENTE! Robô consciente assume o controle de laboratório e deixa cientistas em PÂNICO absoluto!",
        "Esqueça o ChatGPT! Esta nova ferramenta SECRETA faz todo o seu trabalho enquanto você dorme!",
        "A MAIOR DESCOBERTA DA HISTÓRIA: Chip quântico barato vai mudar o mundo para SEMPRE esta semana!",
        "CUIDADO! Se você usa este aplicativo de mensagem, todos os seus dados e fotos já foram VAZADOS!",
        "CHOQUE! Engenheiro demitido revela a verdade assustadora sobre o que o Google está escondendo de você!",
        "Adeus placas de vídeo! A invenção milagrosa que roda qualquer jogo em 8K em computadores velhos!",
        "GOLPE OU REVOLUÇÃO? Conheça a criptomoeda secreta que vai multiplicar seu dinheiro por mil vezes!",
        "A TERREMOTICA IA: O sistema que preverá o futuro e tornará os médicos totalmente OBSOLETOS!",
        "SURPRESA ABSOLUTA! Descobriram um código secreto que acelera a internet em 500% instantaneamente!",
        "ALERTA GERAL! O fim dos smartphones chegou e esta nova tecnologia vai substituir as telas para sempre!"
    ]
    
    # Multiplicar e adicionar pequenas variações para gerar um dataset inicial razoável (150 amostras)
    data = []
    np.random.seed(42)
    
    for _ in range(5):
        for text in sobrio_texts:
            # Adicionar pequenas variações aleatórias para diversificar
            data.append({"text": text, "label": "sobrio", "target": 0})
            
        for text in sensacionalista_texts:
            data.append({"text": text, "label": "sensacionalista", "target": 1})
            
    df = pd.DataFrame(data)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Dataset de treino/teste de amostra gerado com sucesso em: {output_path} ({len(df)} registros)")

if __name__ == "__main__":
    target_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "dataset_hype_treino.csv"))
    generate_sample_dataset(target_path)
