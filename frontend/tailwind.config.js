/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // 主色：明亮温暖儿童友好
        grass: {
          DEFAULT: '#7cb342',
          50: '#f1f8e9',
          100: '#dcedc8',
          200: '#c5e1a5',
          300: '#aed581',
          400: '#9ccc65',
          500: '#7cb342',
          600: '#689f38',
          700: '#558b2f',
          800: '#33691e',
          900: '#1b5e20',
        },
        // 魔法绿（宝石蓝绿色）
        magic: {
          DEFAULT: '#26c6da',
          light: '#80deea',
          dark: '#0097a7',
        },
        // 天空蓝
        sky: {
          DEFAULT: '#4fc3f7',
          light: '#b3e5fc',
          dark: '#0288d1',
        },
        // 木质棕
        wood: {
          DEFAULT: '#8d6e63',
          light: '#bcaaa4',
          dark: '#5d4037',
          700: '#4e342e',
        },
        // 金色奖励
        gold: {
          DEFAULT: '#ffd54f',
          light: '#ffecb3',
          dark: '#ffb300',
          300: '#ffe082',
        },
        // 紫色（稀有）
        purple: {
          DEFAULT: '#ab47bc',
          light: '#ce93d8',
          dark: '#7b1fa2',
        },
        // 红色（警告）
        red: {
          DEFAULT: '#ef5350',
          light: '#ffcdd2',
          dark: '#c62828',
        },
        // 宝石色（保留兼容）
        gem: '#26c6da',
        'gem-300': '#80deea',
        night: '#37474f',
      },
      fontFamily: {
        pixel: ['"Fusion Pixel"', '"Zpix"', 'monospace'],
      },
      borderRadius: {
        'pixel': '12px',
        'pixel-sm': '8px',
        'pixel-lg': '16px',
      },
    },
  },
  plugins: [],
}
