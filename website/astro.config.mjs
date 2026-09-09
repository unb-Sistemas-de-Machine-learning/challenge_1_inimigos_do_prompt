import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://unb-sistemas-de-machine-learning.github.io',
	base: '/challenge_1_inimigos_do_prompt',
	integrations: [
		starlight({
			title: 'Inimigos do Prompt',
			locales: {
				root: { label: 'Português', lang: 'pt-BR' }
			},
			customCss: [
				'./src/styles/custom.css',
			],
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/unb-Sistemas-de-Machine-learning/challenge_1_inimigos_do_prompt' }],
			sidebar: [
				{ label: 'Início', link: '/challenge_1_inimigos_do_prompt/' },
				{ label: 'Planejamento', slug: 'planejamento' },
				{ label: 'Coleta de Dados', slug: 'dados' },
				{ label: 'Arquitetura da Extensão', slug: 'arquitetura' },
				{ label: 'Execução PoC & API', slug: 'execucao_poc_api' },
				{ label: 'Extensão Web (Frontend)', slug: 'extensao_frontend' },
				{ label: 'Backend API', slug: 'backend_api' },
				{ label: 'Guia de Configuração', slug: 'setup' }
			],
		}),
	],
});
