import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'envoic',
  description: 'Discover and report Python virtual environments on your system',
  base: '/envoic/',

  head: [
    ['link', { rel: 'icon', href: '/envoic/favicon.png' }],
  ],

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Reference', link: '/reference/commands' },
      { text: 'PyPI', link: 'https://pypi.org/project/envoic/' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Introduction',
          items: [
            { text: 'What is envoic?', link: '/guide/what-is-envoic' },
            { text: 'Getting Started', link: '/guide/getting-started' },
          ]
        },
        {
          text: 'Usage',
          items: [
            { text: 'Scanning Environments', link: '/guide/scanning' },
            { text: 'Reading Reports', link: '/guide/reports' },
            { text: 'Managing Environments', link: '/guide/managing' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'CLI Commands', link: '/reference/commands' },
            { text: 'Detection Logic', link: '/reference/detection' },
            { text: 'Output Formats', link: '/reference/output-formats' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/mahimailabs/envoic' },
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026 Mahimai Labs',
    },

    search: {
      provider: 'local',
    },
  },
})
