import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'envoic',
  description: 'Discover and manage Python and JavaScript development environments',
  base: '/envoic/',

  head: [
    ['link', { rel: 'icon', href: '/envoic/favicon.png' }],
  ],

  themeConfig: {
    logo: '/logo.svg',

    nav: [
      { text: 'Python Guide', link: '/guide/getting-started' },
      { text: 'JS Guide', link: '/guide/js-getting-started' },
      { text: 'Python Ref', link: '/reference/commands' },
      { text: 'JS Ref', link: '/reference/js-commands' },
      { text: 'PyPI', link: 'https://pypi.org/project/envoic/' },
      { text: 'npm', link: 'https://www.npmjs.com/package/envoic' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Python',
          items: [
            { text: 'What is envoic?', link: '/guide/what-is-envoic' },
            { text: 'Getting Started', link: '/guide/getting-started' },
            { text: 'Scanning Environments', link: '/guide/scanning' },
            { text: 'Reading Reports', link: '/guide/reports' },
            { text: 'Managing Environments', link: '/guide/managing' },
            { text: 'Configuration', link: '/guide/configuration' },
          ]
        },
        {
          text: 'JavaScript',
          items: [
            { text: 'Getting Started (JS)', link: '/guide/js-getting-started' },
            { text: 'Scanning (JS)', link: '/guide/js-scanning' },
            { text: 'Managing (JS)', link: '/guide/js-managing' },
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Python Reference',
          items: [
            { text: 'CLI Commands', link: '/reference/commands' },
            { text: 'Detection Logic', link: '/reference/detection' },
            { text: 'Output Formats', link: '/reference/output-formats' },
          ]
        },
        {
          text: 'JavaScript Reference',
          items: [
            { text: 'CLI Commands (JS)', link: '/reference/js-commands' },
            { text: 'Detection Logic (JS)', link: '/reference/js-detection' },
            { text: 'Output Formats (JS)', link: '/reference/js-output-formats' },
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
