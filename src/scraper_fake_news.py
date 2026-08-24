import os
import time
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

# Headers padrão para simular um navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'lxml')
        else:
            print(f"Erro ao acessar {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Erro de conexão ao acessar {url}: {e}")
    return None

def scrape_article_detail(url):
    """
    Extrai o conteúdo detalhado de um artigo do Boatos.org:
    - O texto do boato (geralmente dentro de <blockquote>)
    - O texto da checagem (análise desmistificando o boato)
    """
    soup = get_soup(url)
    if not soup:
        return None, None
    
    content_div = soup.find('div', class_='entry-content')
    if not content_div:
        # Tenta classe alternativa caso tenha mudado
        content_div = soup.find('div', class_='nv-content-wrap')
        
    if not content_div:
        return None, None
    
    # 1. Extrair o texto do boato (dentro de blockquote)
    hoax_texts = []
    blockquotes = content_div.find_all('blockquote')
    for bq in blockquotes:
        # Remover eventuais tags de publicidade internas
        text = bq.get_text(separator=' ').strip()
        if text:
            hoax_texts.append(text)
            
    hoax_text = " | ".join(hoax_texts) if hoax_texts else None
    
    # 2. Extrair o texto da checagem/debunking (parágrafos fora de blockquotes)
    debunk_paragraphs = []
    # Clonamos para poder remover elementos e obter apenas os parágrafos limpos
    content_clone = BeautifulSoup(str(content_div), 'lxml')
    # Remover blockquotes para não duplicar no texto de debunking
    for bq in content_clone.find_all('blockquote'):
        bq.decompose()
    # Remover scripts e anúncios
    for tag in content_clone.find_all(['script', 'style', 'ins', 'iframe']):
        tag.decompose()
        
    for p in content_clone.find_all('p'):
        text = p.get_text().strip()
        # Ignorar textos comuns de fim de página ou anúncios
        if text and not text.startswith("Clique aqui para") and "adsbygoogle" not in text:
            debunk_paragraphs.append(text)
            
    debunk_text = "\n".join(debunk_paragraphs)
    
    return hoax_text, debunk_text

def scrape_boatos_page(page_num):
    url = f"https://www.boatos.org/page/{page_num}" if page_num > 1 else "https://www.boatos.org/"
    print(f"Scrapeando lista de artigos na página {page_num}...")
    soup = get_soup(url)
    if not soup:
        return []
    
    articles = soup.find_all('article')
    page_data = []
    
    for art in articles:
        # Encontrar título e link
        title_tag = art.find('h2', class_='entry-title')
        if not title_tag:
            title_tag = art.find('h2', class_='blog-entry-title')
            
        if title_tag and title_tag.find('a'):
            a_tag = title_tag.find('a')
            title = a_tag.get_text().strip()
            link = a_tag['href']
            
            # Encontrar categoria
            category = "Geral"
            cat_tag = art.find('li', class_='category')
            if cat_tag and cat_tag.find('a'):
                category = cat_tag.find('a').get_text().strip()
                
            # Encontrar data
            publish_date = ""
            time_tag = art.find('time')
            if time_tag:
                publish_date = time_tag.get('datetime', '') or time_tag.get_text().strip()
                
            # Adicionar dados iniciais
            page_data.append({
                'title': title,
                'url': link,
                'category': category,
                'publish_date': publish_date
            })
            
    return page_data

def main():
    parser = argparse.ArgumentParser(description="Scraper do site Boatos.org")
    parser.add_argument("--pages", type=int, default=5, help="Número de páginas para raspar (padrão: 5)")
    parser.add_argument("--delay", type=float, default=1.0, help="Tempo de espera entre requisições em segundos (padrão: 1.0)")
    args = parser.parse_args()
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    
    all_articles = []
    
    print(f"Iniciando scraping de {args.pages} páginas do Boatos.org...")
    for p in range(1, args.pages + 1):
        page_articles = scrape_boatos_page(p)
        if not page_articles:
            print(f"Sem artigos na página {p} ou erro. Parando.")
            break
        all_articles.extend(page_articles)
        time.sleep(args.delay)
        
    print(f"Total de links coletados: {len(all_articles)}")
    
    # Agora buscar os detalhes de cada artigo
    detailed_data = []
    for art in tqdm(all_articles, desc="Coletando detalhes dos boatos"):
        url = art['url']
        hoax, debunk = scrape_article_detail(url)
        
        # Só mantemos se conseguirmos extrair algum texto de checagem
        if debunk:
            art['hoax_text'] = hoax
            art['debunking_text'] = debunk
            detailed_data.append(art)
        
        time.sleep(args.delay)
        
    df = pd.DataFrame(detailed_data)
    
    # Salvar resultados
    output_path = os.path.join(data_dir, "scraped_fake_news.csv")
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Scraping finalizado! Dados salvos em: {output_path}")
    print(f"Total de registros raspados com sucesso: {len(df)}")

if __name__ == "__main__":
    main()
